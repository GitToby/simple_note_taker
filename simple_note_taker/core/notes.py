import logging
import re
from datetime import datetime
from typing import Any, List

from pydantic.main import BaseModel
from tinydb import Query

from simple_note_taker.config import config
from simple_note_taker.core.database import tiny_db, NOTES_TABLE_NAME, REMINDERS_TABLE_NAME

_notes_db = tiny_db.table(NOTES_TABLE_NAME)
_reminders_db = tiny_db.table(REMINDERS_TABLE_NAME)


class _NoteModel(BaseModel):
    """
    A crude ORM of sorts. Base model with fields we want to save via the Note class
    """

    # Database use
    content: str
    private: bool = config.default_private
    shared: bool = False
    user: str = config.username
    taken_at: datetime = datetime.now()

    def pretty_str(self) -> str:
        return f"Unsaved Note: {self.taken_at.strftime('%H:%M, %a %d %b %Y')} | {self.content}"

    def __lt__(self, other) -> bool:
        return self.taken_at < other.taken_at


def _remind_me_parse(note: 'Note'):
    logging.info(f'_remind_me_parse for {note.content}')


MAGIC_COMMANDS = {
    "!remindme": _remind_me_parse
}


class Note(_NoteModel):
    """
    Class for creating notes and saving them, to ensure the create hooks are run.
    """

    def save(self) -> 'NoteInDB':
        commands = [cmd for cmd in MAGIC_COMMANDS if cmd in self.content.lower()]
        for command in commands:
            MAGIC_COMMANDS[command](self)

        note_id = _notes_db.insert(self.dict())
        return Notes.get_by_id(note_id)


class NoteInDB(_NoteModel):
    """
    A note from the database is the same as a note but with a doc ID value.
    This model can be updated
    """
    # App use
    doc_id: int = None

    def pretty_str(self) -> str:
        return f"Note {self.doc_id}\t: {self.taken_at.strftime('%H:%M, %a %d %b %Y')} | {self.content}"

    def delete(self) -> int:
        return _notes_db.remove(doc_ids=[self.doc_id])


class Notes:
    @staticmethod
    def all() -> List[NoteInDB]:
        return [NoteInDB(**n, doc_id=n.doc_id) for n in _notes_db.all()]

    @staticmethod
    def get_by_id(doc_id: int) -> NoteInDB:
        res = _notes_db.get(doc_id=doc_id)
        return NoteInDB(**res, doc_id=res.doc_id)

    @staticmethod
    def search(query: str, field: str) -> List[NoteInDB]:
        query = Query()[field].search(query, flags=re.IGNORECASE)
        search_res = _notes_db.search(query)
        return [NoteInDB(**n, doc_id=n.doc_id) for n in search_res]

    def search_date(self, date):
        q = Query()
        res = _notes_db.search(q.time_taken > date)
        # ... return these
