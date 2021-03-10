import re
from datetime import datetime
from typing import Any, List

from pydantic.main import BaseModel
from tinydb import Query
from tinydb.table import Table

from simple_note_taker.config import config
from simple_note_taker.core.database import tiny_db


def _remind_me_parse(note: 'Note'):
    print('_remind_me_parse')


MAGIC_COMMANDS = {
    "!remindme": _remind_me_parse
}


class Note(BaseModel):
    """
    A crude ORM of sorts
    """

    # Database use
    content: str
    private: bool
    shared: bool = False
    user: str = config.username
    taken_at: datetime = datetime.now()

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        commands = [cmd for cmd in MAGIC_COMMANDS if cmd in self.content.lower()]
        for command in commands:
            MAGIC_COMMANDS[command](self)

    def _remind_me_parse(self):
        pass

    def pretty_str(self) -> str:
        return f"Unsaved Note: {self.taken_at.strftime('%H:%M, %a %d %b %Y')} | {self.content}"

    def __lt__(self, other) -> bool:
        return self.taken_at < other.taken_at


class NoteInDB(Note):
    # App use
    doc_id: int = None

    def pretty_str(self) -> str:
        return f"Note {self.doc_id}: {self.taken_at.strftime('%H:%M, %a %d %b %Y')} | {self.content}"


class _Collection:
    # todo: make this a generic typed and extrapolate into reminder tables also
    _db_table: Table = tiny_db.table("notes")

    def all(self) -> List[NoteInDB]:
        return [NoteInDB(**n, doc_id=n.doc_id) for n in self._db_table.all()]

    def search(self, query: str, field: str) -> List[NoteInDB]:
        q = Query()
        search_res = self._db_table.search(q[field].search(query, flags=re.IGNORECASE))
        return [NoteInDB(**n, doc_id=n.doc_id) for n in search_res]

    def add(self, Note) -> NoteInDB:
        self._db_table.insert(Note.dict())


notes = _Collection()
res = notes.search("hello world")
