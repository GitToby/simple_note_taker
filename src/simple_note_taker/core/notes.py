import re
from datetime import datetime, timedelta
from typing import List, Optional

from pydantic.main import BaseModel
from pytimeparse import parse
from rapidfuzz import fuzz, process
from tinydb import Query
from tinydb.table import Table

from simple_note_taker.core.config import config
from simple_note_taker.core.database import tiny_db

DATE_FORMAT = "%H:%M, %a %d %b %Y"


def _get_note_db(db_name: str = config.default_notebook) -> Table:
    return tiny_db.table(db_name)


class Note(BaseModel):
    """
    A crude ORM of sorts. Base model with fields we want to save via the Note class
    """

    # Database use
    content: str
    tags: List[str] = []
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
        """
        super().__init__(content=content, **data)

    def _note_id_str(self) -> str:
        return "Unsaved note"

    def pretty_str(self) -> str:
        time_taken_str = self.taken_at.strftime(DATE_FORMAT)
        task_str = "   "
        if self.task:
            task_x = "x" if self.task_complete else " "
            task_str = f"[{task_x}]"  # e.g. [x] for a task which is done

        return f"{self._note_id_str()}: {time_taken_str} | {task_str} | {self.content}"

    def __lt__(self, other) -> bool:
        return self.taken_at < other.taken_at

    def _remind_me_parse(self):
        """
        Given a note, we should process and save a reminder which maps back to the content.
        Examples:
            '!remindme 3d i should take out the bins!' - should set a task with reminder to today + 3 days
            '!remindme that i need to make dinner' - should set a task with a reminder thats due now
            '!remindme that in 3d i should create the 3d models!' - will parse the first 3d but not the second
        """
        parse_times = [parse(s) for s in self.content.split(" ") if parse(s) is not None]
        delta_seconds = 0 if len(parse_times) == 0 else parse_times[0]
        self._task_parse(timedelta(seconds=delta_seconds))

    def _task_parse(self, reminder_delta: Optional[timedelta] = None):
        """
        Tags the note as a task, optionally adds a reminder date also.
        """
        self.task = True
        if reminder_delta is not None:
            self.reminder = datetime.now() + reminder_delta

    def _private_parse(self):
        self.private = True

    def _run_magic(self):
        magic_commands = {
            "!todo": self._task_parse,
            "!task": self._task_parse,
            "!chore": self._task_parse,
            "!remindme": self._remind_me_parse,
            "!reminder": self._remind_me_parse,
            "!alert": self._remind_me_parse,
            "!private": self._private_parse,
            "!secret": self._private_parse,
        }
        commands = {cmd for cmd in magic_commands if cmd in self.content.lower()}
        for command in commands:
            magic_commands[command]()

    def save(self, run_magic=True) -> "NoteInDB":
        if run_magic:
            self._run_magic()

        note_id = _get_note_db().insert(self.dict())
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
        spacer = ""
        if self.doc_id < 10:
            spacer = "  "
        elif self.doc_id < 100:
            spacer = " "
        return f"Note {self.doc_id}{spacer}"

    def delete(self) -> int:
        remove_res = _get_note_db().remove(doc_ids=[self.doc_id])
        return remove_res[0]

    def update(self, run_magic=False):
        if run_magic:
            self._run_magic()

        update_res = _get_note_db().update(self.dict(exclude={"doc_id"}), doc_ids=[self.doc_id])
        return update_res


class Notes:
    @staticmethod
    def all() -> List[NoteInDB]:
        return [NoteInDB(**n, doc_id=n.doc_id) for n in _get_note_db().all()]

    @staticmethod
    def latest() -> Optional[NoteInDB]:
        notes_all = Notes.all()
        if len(notes_all) > 0:
            return notes_all[0]
        else:
            return None

    @staticmethod
    def get_by_id(doc_id: int) -> Optional[NoteInDB]:
        res = _get_note_db().get(doc_id=doc_id)
        if res is None:
            return None
        else:
            return NoteInDB(**res, doc_id=res.doc_id)

    @staticmethod
    def find_by_tags(tags_list: List[str], union=False):
        if union:
            query = Query().tags.all(tags_list)
        else:
            query = Query().tags.any(tags_list)
        search_res = _get_note_db().search(query)
        return [NoteInDB(**n, doc_id=n.doc_id) for n in search_res]

    @staticmethod
    def find_match(query: str, field: str) -> List[NoteInDB]:
        query = Query()[field].search(query, flags=re.IGNORECASE)
        search_res = _get_note_db().search(query)
        return [NoteInDB(**n, doc_id=n.doc_id) for n in search_res]

    @staticmethod
    def search(query: str, result_size: int = 5) -> List[NoteInDB]:
        all_notes_dict = {note.doc_id: note.content for note in Notes.all()}
        search_results = process.extract(
            query, choices=all_notes_dict, scorer=fuzz.token_set_ratio, limit=result_size, score_cutoff=20
        )
        return [Notes.get_by_id(res_record[2]) for res_record in search_results]

    @staticmethod
    def all_tasks(include_complete: bool = False) -> List[NoteInDB]:
        search_res = _get_note_db().search(Query()["task"] is True)
        tasks = [NoteInDB(**n, doc_id=n.doc_id) for n in search_res]
        if include_complete:
            return tasks
        else:
            return [task for task in tasks if not task.task_complete]

    @staticmethod
    def due_reminders():
        now = datetime.now()
        return [
            note
            for note in Notes.all()
            if note.task and not note.task_complete and note.reminder is not None and note.reminder < now
        ]


n = Notes()
