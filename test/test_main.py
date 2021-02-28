from unittest import TestCase
from unittest.mock import patch

from tinydb import TinyDB
from tinydb.storages import MemoryStorage
from tinydb_serialization import SerializationMiddleware
from tinydb_serialization.serializers import DateTimeSerializer
from typer.testing import CliRunner

from simple_note_taker.main import app
from simple_note_taker.model import Note

runner = CliRunner()


def get_test_db():
    serialization = SerializationMiddleware(MemoryStorage)
    serialization.register_serializer(DateTimeSerializer(), 'TinyDate')
    return TinyDB(storage=serialization)


class TestMain(TestCase):

    def test_take(self):
        test_note = "test note"
        with patch('simple_note_taker.main.notes', new=get_test_db()) as test_db:
            runner.invoke(app, ["take"], input=f"{test_note}\n")
            self.assertEqual(len(test_db.all()), 1)
            self.assertEqual(test_db.all()[0]['content'], test_note)

    def test_take_in_arg(self, ):
        test_note = "test note in 1 arg"
        with patch('simple_note_taker.main.notes', new=get_test_db()) as test_db:
            runner.invoke(app, ["take", "--note", test_note])
            assert len(test_db.all()) == 1
            assert test_db.all()[0]['content'] == test_note

    def test_search(self):
        test_note = "test note to search from"
        n = Note(content=test_note, private=False)
        n2 = Note(content="no common chars", private=False)
        with patch('simple_note_taker.main.notes', new=get_test_db()) as test_db:
            test_db.insert(n.as_insertable())
            test_db.insert(n2.as_insertable())
            self.assertEqual(len(test_db.all()), 2)
            search_str = test_note[9:13]
            result = runner.invoke(app, ["search", search_str])
            assert search_str in result.stdout
            assert "Found 1" in result.stdout
            assert "Found 2" not in result.stdout

    def test_latest(self):
        self.fail()

    def test_edit(self):
        self.fail()

    def test_note(self):
        assert 1 == 1
