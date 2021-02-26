from unittest import TestCase
from unittest.mock import patch

from click import Context
from tinydb import TinyDB
from tinydb.storages import MemoryStorage
from tinydb_serialization import SerializationMiddleware
from tinydb_serialization.serializers import DateTimeSerializer
from typer.testing import CliRunner

from .main import app

runner = CliRunner()


def get_test_db():
    serialization = SerializationMiddleware(MemoryStorage)
    serialization.register_serializer(DateTimeSerializer(), 'TinyDate')
    return TinyDB(storage=serialization)


class TestMain(TestCase):

    def test_take(self):
        with patch('simple_note_taker.main.notes', new=get_test_db()) as test_db:
            test_note = "test note"
            runner.invoke(app, ["take"], input=f"{test_note}\n")
            self.assertEqual(len(test_db.all()), 1)
            self.assertEqual(test_db.all()[0]['content'], test_note)

    def test_take_non_string(self):
        with patch('simple_note_taker.main.notes', new=get_test_db()) as test_db:
            test_note = "test note"
            runner.invoke(app, ["take"], input=2341)
            self.assertEqual(len(test_db.all()), 1)
            self.assertEqual(test_db.all()[0]['content'], test_note)

    def test_search(self):
        self.fail()

    def test_latest(self):
        self.fail()

    def test_edit(self):
        self.fail()

    def test_note(self):
        self.fail()
