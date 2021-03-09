from datetime import datetime
from typing import Any

from pydantic.main import BaseModel

from simple_note_taker.config import config


def _remind_me_parse(note: 'Note'):
    print('_remind_me_parse')


# Constants
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

    # App use
    doc_id: int = None

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        commands = [cmd for cmd in MAGIC_COMMANDS if cmd in self.content.lower()]
        for command in commands:
            MAGIC_COMMANDS[command](self)

    def _remind_me_parse(self):
        pass

    def pretty_str(self) -> str:
        return f"Note {self.doc_id}: {self.taken_at.strftime('%H:%M, %a %d %b %Y')} | {self.content}"

    def as_insertable(self) -> dict:
        return self.dict(exclude={"doc_id"})

    def __lt__(self, other) -> bool:
        return self.taken_at < other.taken_at
