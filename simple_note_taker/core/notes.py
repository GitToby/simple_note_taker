import re
from datetime import datetime, timedelta
from typing import List, Optional

from pydantic.main import BaseModel
from tinydb import Query

from simple_note_taker.config import config
from simple_note_taker.core.database import NOTES_TABLE_NAME, tiny_db

_notes_db = tiny_db.table(NOTES_TABLE_NAME)


class Note(BaseModel):
    """
    A crude ORM of sorts. Base model with fields we want to save via the Note class
    """

    # Database use
    content: str
    private: bool = config.default_private
    shared: bool = False
    task: bool = False  # tasks are a subset of notes
    task_complete: Optional[datetime] = None  # tasks can be noted as complete with a date when they were completed
    reminder: Optional[datetime] = None  # if a note is a task it can have a optionally have a reminder
    user: str = config.username
    taken_at: datetime = datetime.now()

    def __init__(self, content: str, **data):
        """
        All other fields have defaults and should be altered with helper methods in NoteInDB
        :param content:
        """
        super().__init__(content=content, **data)

    def _note_id_str(self) -> str:
        return "Unsaved note"

    def pretty_str(self) -> str:
        time_taken_str = self.taken_at.strftime('%H:%M, %a %d %b %Y')

        task_str = "    "
        if self.task:
            task_x = "x" if self.task_complete else " "
            task_r = "R" if self.reminder is not None and self.reminder > datetime.now() else " "

            task_str = f"{task_r}[{task_x}]"  # e.g. R[x] for a task which had a reminder and is done

        return f"{self._note_id_str()}: {time_taken_str} | {task_str} | {self.content}"

    def __lt__(self, other) -> bool:
        return self.taken_at < other.taken_at

    def _remind_me_parse(self):
        """
        Given a note, we should process and save a reminder which maps back to the content.
        Examples:
            '!remindme 3d i should take out the bins!' - should set a task with reminder to today + 3 days
            '!remindme that i need to make dinner' - should set a task with a reminder thats due now
        """

        self._task_parse(timedelta(0))

    def _task_parse(self, reminder_delta: Optional[timedelta] = None):
        """
        Tags the note as a task, optionally adds a reminder date also.
        """
        self.task = True
        if reminder_delta is not None:
            self.reminder = datetime.now() + reminder_delta

    def save(self, run_magic=True) -> 'NoteInDB':
        if run_magic:
            magic_commands = {
                "!todo": self._task_parse,
                "!task": self._task_parse,
                "!chore": self._task_parse,
                "!remindme": self._remind_me_parse,
            }

            commands = [cmd for cmd in magic_commands if cmd in self.content.lower()]
            for command in commands:
                magic_commands[command]()

        note_id = _notes_db.insert(self.dict())
        return Notes.get_by_id(note_id)

    def mark_as_done(self):
        self.task_complete = datetime.now()


class NoteInDB(Note):
    """
    A note from the database is the same as a note but with a doc ID value.
    This model can be updated
    """
    # App use
    doc_id: int = None

    def _note_id_str(self) -> str:
        return f"Note {self.doc_id}"

    def delete(self) -> int:
        return _notes_db.remove(doc_ids=[self.doc_id])


class Notes:
    @staticmethod
    def all() -> List[NoteInDB]:
        return [NoteInDB(**n, doc_id=n.doc_id) for n in _notes_db.all()]

    @staticmethod
    def latest() -> Optional[NoteInDB]:
        notes_all = Notes.all()
        if len(notes_all) > 0:
            return notes_all[0]
        else:
            return None

    @staticmethod
    def get_by_id(doc_id: int) -> Optional[NoteInDB]:
        res = _notes_db.get(doc_id=doc_id)
        if res is None:
            return None
        else:
            return NoteInDB(**res, doc_id=res.doc_id)

    @staticmethod
    def search(query: str, field: str) -> List[NoteInDB]:
        query = Query()[field].search(query, flags=re.IGNORECASE)
        search_res = _notes_db.search(query)
        return [NoteInDB(**n, doc_id=n.doc_id) for n in search_res]

    @staticmethod
    def all_tasks(include_complete: bool = False) -> List[NoteInDB]:
        search_res = _notes_db.search(Query()["task"] is True)
        tasks = [NoteInDB(**n, doc_id=n.doc_id) for n in search_res]
        if include_complete:
            return tasks
        else:
            return [task for task in tasks if not task.task_complete]

    @staticmethod
    def due_reminders():
        now = datetime.now()
        return [note for note in Notes.all() if
                note.task
                and not note.task_complete
                and note.reminder is not None
                and note.reminder < now]
