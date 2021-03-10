import time
from datetime import datetime
from unittest import TestCase
from unittest.mock import patch

from tinydb import TinyDB
from tinydb.storages import MemoryStorage
from tinydb_serialization import SerializationMiddleware
from tinydb_serialization.serializers import DateTimeSerializer

from simple_note_taker.core.notes import Note

_serialization = SerializationMiddleware(MemoryStorage)
_serialization.register_serializer(DateTimeSerializer(), "TinyDate")

test_db = TinyDB(storage=_serialization)
notes_db = test_db.table("notes")
reminders_db = test_db.table("reminders")


@patch('simple_note_taker.core.notes._notes_db', new=notes_db)
@patch('simple_note_taker.core.notes._reminders_db', new=notes_db)
class TestNoteModel(TestCase):
    def setUp(self) -> None:
        test_db.drop_tables()

    def test_create_and_save_note(self):
        note = Note(content="test content", private=False)
        self.assertEqual(0, len(notes_db.all()))
        note.save()
        self.assertEqual(1, len(notes_db.all()))

    def test_ordering(self):
        note_1 = Note(content="test note 1", private=False, taken_at=datetime(2021, 1, 1))
        note_2 = Note(content="test note 2", private=False)
        self.assertLess(note_1, note_2)

    def test_create_and_execute_magic_remind_me(self):
        note = Note(content="test content with !remindMe 2d", private=False)
        self.assertEqual(0, len(notes_db.all()))
        note.save()
        self.assertEqual(1, len(notes_db.all()))

# class TestNoteInDBModel(TestCase):
#     def test_pretty_str(self):
#         self.assertEqual(0, 1)
