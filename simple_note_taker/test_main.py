from unittest import TestCase

from tinydb import TinyDB
from typer.testing import CliRunner

from .main import app, db

runner = CliRunner()


class TestMain(TestCase):

    def setUp(self) -> None:
        pass

    def test_take(self):
        runner.invoke(app)

    def test_search(self):
        self.fail()

    def test_latest(self):
        self.fail()

    def test_edit(self):
        self.fail()

    def test_note(self):
        self.fail()
