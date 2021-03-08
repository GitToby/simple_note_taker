from dataclasses import asdict, dataclass
from datetime import datetime

from simple_note_taker.config import config


@dataclass
class Note:
    """
    A crude ORM of sorts
    """

    # Database use
    content: str
    private: bool
    user: str = config.username
    taken_at: datetime = datetime.now()

    # App use
    doc_id: int = None

    def pretty_str(self) -> str:
        return f"Note {self.doc_id}: {self.taken_at.strftime('%H:%M, %a %d %b %Y')} | {self.content}"

    def as_insertable(self) -> dict:
        tmp = asdict(self)
        del tmp["doc_id"]  # this shouldn't be inserted into the db again
        return tmp

    def __lt__(self, other) -> bool:
        return self.taken_at < other.taken_at
