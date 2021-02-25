from unittest import TestCase
from unittest.mock import patch

from click import Context
from tinydb import TinyDB
from tinydb.storages import MemoryStorage
from tinydb_serialization import SerializationMiddleware
from tinydb_serialization.serializers import DateTimeSerializer
from typer.testing import CliRunner

from .main import app, take, db

runner = CliRunner()

serialization = SerializationMiddleware(MemoryStorage)
serialization.register_serializer(DateTimeSerializer(), 'TinyDate')
test_db = TinyDB(
    storage=serialization
)


class TestMain(TestCase):

    def setUp(self) -> None:
        pass

    @patch('simple_note_taker.main.notes', new=test_db)
    def test_take(self):
        runner.invoke(app, ["take"], input="test note\n")
        print(test_db.all())

    def test_search(self):
        self.fail()

    def test_latest(self):
        self.fail()

    def test_edit(self):
        self.fail()

    def test_note(self):
        self.fail()
