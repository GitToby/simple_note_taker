from datetime import datetime
from unittest import TestCase
from unittest.mock import patch

import dateparser
from tinydb import TinyDB
from tinydb.storages import MemoryStorage
from tinydb_serialization import SerializationMiddleware
from tinydb_serialization.serializers import DateTimeSerializer

from simple_note_taker.core.notes import Note

_serialization = SerializationMiddleware(MemoryStorage)
_serialization.register_serializer(DateTimeSerializer(), "TinyDate")

test_db = TinyDB(storage=_serialization)
notes_db = test_db.table("notes")


@patch('simple_note_taker.core.notes._notes_db', new=notes_db)
class TestNoteModelDBInteractions(TestCase):
    def setUp(self) -> None:
        test_db.drop_tables()

    def test_create_and_save_note(self):
        note = Note("test content")
        self.assertEqual(0, len(notes_db.all()))
        note.save()
        self.assertEqual(1, len(notes_db.all()))


@patch('simple_note_taker.core.notes._notes_db', new=notes_db)
class TestNoteModel(TestCase):
    def test_ordering(self):
        note_1 = Note("test note 1", taken_at=datetime(2021, 1, 1))
        note_2 = Note("test note 2")
        self.assertLess(note_1, note_2)

    def test_create_and_execute_magic_remind_me(self):
        note = Note("test content with !remindMe").save()
        assert note.task is True

    def test_retester(self):
        exs = [
            "2w",
            "2d2h 5mins",
        ]
        print(datetime.now())
        for e in exs:
            print(dateparser.parse(e))
