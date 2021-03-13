import time
from unittest import TestCase
from unittest.mock import patch

from tinydb import TinyDB
from tinydb.storages import MemoryStorage
from tinydb_serialization import SerializationMiddleware
from tinydb_serialization.serializers import DateTimeSerializer
from typer.testing import CliRunner

from simple_note_taker.main import app

runner = CliRunner()

_serialization = SerializationMiddleware(MemoryStorage)
_serialization.register_serializer(DateTimeSerializer(), "TinyDate")

test_db = TinyDB(storage=_serialization)
_notes_db = test_db.table("notes")


@patch('simple_note_taker.core.notes._notes_db', new=_notes_db)
class TestTakeMain(TestCase):
    def setUp(self) -> None:
        _notes_db.truncate()
        super().tearDown()

    def test_take(self):
        test_note = "tests note"
        result = runner.invoke(app, ["take"], input=f"{test_note}\n")
        assert result.exit_code == 0
        assert test_note in result.stdout
        assert "saved with id 1" in result.stdout.lower()

    def test_take_task(self):
        test_note = "tests note which is a !task"
        result = runner.invoke(app, ["take"], input=f"{test_note}\n")
        assert result.exit_code == 0
        assert test_note in result.stdout
        assert "saved with id 1" in result.stdout.lower()
        assert "task" in result.stdout.lower()

    def test_take_reminder(self):
        test_note = "tests note with a !reminder"
        result = runner.invoke(app, ["take"], input=f"{test_note}\n")
        assert result.exit_code == 0
        assert test_note in result.stdout
        assert "saved with id 1" in result.stdout.lower()
        assert "task" in result.stdout.lower()
        assert "reminder" in result.stdout.lower()
        time.sleep(1)  # test runs too fast for reminder to be picked up
        result2 = runner.invoke(app, ["ls"])
        assert result.exit_code == 0
        assert "1 reminders due" in result2.stdout.lower()
        assert test_note in result2.stdout

    def test_take_in_arg(self):
        test_note = "tests note in 1 arg"
        result = runner.invoke(app, ["take", "--note", test_note])
        assert result.exit_code == 0
        assert test_note not in result.stdout
        print(result.stdout)
        assert "saved with id 1" in result.stdout.lower()

    def test_search(self):
        runner.invoke(app, ["take", "--note", "note one"])
        runner.invoke(app, ["take", "--note", "note two"])
        runner.invoke(app, ["take", "--note", "note three"])
        ls_res = runner.invoke(app, ["ls"])
        assert "one" in ls_res.stdout
        assert "two" in ls_res.stdout
        assert "three" in ls_res.stdout
        search_res = runner.invoke(app, ["search", "three"])
        assert search_res.exit_code == 0
        assert "note one" not in search_res.stdout
        assert "note three" in search_res.stdout

    def test_ls(self):
        for i in range(15):
            runner.invoke(app, ["take", "--note", f"note number {i}"])
        result = runner.invoke(app, ["ls"])
        assert result.exit_code == 0
        # Default is a header line, 10 record lines and a final \n
        assert len(result.stdout.split("\n")) == 12

    def test_ls_all(self):
        for i in range(15):
            runner.invoke(app, ["take", "--note", f"note number {i}"])
        result = runner.invoke(app, ["ls", "0"])
        assert result.exit_code == 0
        assert len(result.stdout.split("\n")) == 17

    def test_ls_5(self):
        for i in range(15):
            runner.invoke(app, ["take", "--note", f"note number {i}"])
        result = runner.invoke(app, ["ls", "5"])
        assert result.exit_code == 0
        assert len(result.stdout.split("\n")) == 7

    def test_ls_less_than_entries(self):
        for i in range(5):
            runner.invoke(app, ["take", "--note", f"note number {i}"])
        result = runner.invoke(app, ["ls"])
        assert result.exit_code == 0
        assert len(result.stdout.split("\n")) == 7

    def test_tasks(self):
        runner.invoke(app, ["take", "--note", "!task number 1"])
        runner.invoke(app, ["take", "--note", "!chore number 2"])
        runner.invoke(app, ["take", "--note", "!todo number 3"])
        result = runner.invoke(app, ["tasks"])
        assert result.exit_code == 0
        assert len(result.stdout.split("\n")) == 5

    def test_tasks_all(self):
        runner.invoke(app, ["take", "--note", "!task number 1"])
        runner.invoke(app, ["take", "--note", "!chore number 2"])
        runner.invoke(app, ["take", "--note", "!todo number 3"])
        for i in range(15):
            runner.invoke(app, ["take", "--note", f"!todo number {i}"])
        result = runner.invoke(app, ["tasks", "0"])
        assert result.exit_code == 0
        assert len(result.stdout.split("\n")) == 20

    def test_tasks_with_include_done(self):
        runner.invoke(app, ["take", "--note", "!task number 1"])
        runner.invoke(app, ["take", "--note", "!task number 2"])
        runner.invoke(app, ["mark-done", "1"])
        result = runner.invoke(app, ["tasks"])
        assert result.exit_code == 0
        assert len(result.stdout.split("\n")) == 3
        result2 = runner.invoke(app, ["tasks", "--include-complete"])
        assert result2.exit_code == 0
        assert f"[x] | !task number 1" in result2.stdout.lower()
        assert len(result2.stdout.split("\n")) == 4

    def test_mark_done(self):
        runner.invoke(app, ["take", "--note", f"!task number 1"])
        result = runner.invoke(app, ["tasks"])
        assert result.exit_code == 0
        assert len(result.stdout.split("\n")) == 3
        assert "number 1" in result.stdout
        result2 = runner.invoke(app, ["mark-done", "1"])
        assert result2.exit_code == 0
        assert "Marked note 1 as done." in result2.stdout
        result3 = runner.invoke(app, ["tasks"])
        assert result3.exit_code == 0
        assert len(result3.stdout.split("\n")) == 2
        assert "number 1" not in result3.stdout

    def test_mark_done_not_found(self):
        result = runner.invoke(app, ["mark-done", "1"])
        assert result.exit_code == 1
        assert "No note under id 1 found." in result.stdout

    def test_size(self):
        for i in range(15):
            runner.invoke(app, ["take", "--note", f"note number {i}"])
        result = runner.invoke(app, ["size"])
        assert result.exit_code == 0
        assert "15" in result.stdout

    def test_edit(self):
        runner.invoke(app, ["take", "--note", "note one"])
        result = runner.invoke(app, ["edit", "1"], input="note one with an edit\n")
        assert result.exit_code == 0
        assert "note 1 updated" in result.stdout.lower()

    def test_edit_not_found(self):
        result = runner.invoke(app, ["edit", "2"], input="note one with an edit\n")
        assert result.exit_code == 1
        assert "No note of ID 2 found" in result.stdout

    def test_delete_no_force(self):
        runner.invoke(app, ["take", "--note", "note one"])
        result = runner.invoke(app, ["ls"])
        assert len(result.stdout.split("\n")) == 3
        assert "Note 1" in result.stdout
        result2 = runner.invoke(app, ["delete", "1"])
        assert result2.exit_code == 1
        assert "are you sure" in result2.stdout.lower()

    def test_delete_no_force_input(self):
        runner.invoke(app, ["take", "--note", "note one"])
        result = runner.invoke(app, ["ls"])
        assert len(result.stdout.split("\n")) == 3
        assert "Note 1" in result.stdout
        result2 = runner.invoke(app, ["delete", "1"], input="y\n")
        assert result2.exit_code == 0
        assert "are you sure" in result2.stdout.lower()
        assert "id 1 deleted" in result2.stdout.lower()

    def test_delete_force(self):
        runner.invoke(app, ["take", "--note", "note one"])
        result = runner.invoke(app, ["ls"])
        assert len(result.stdout.split("\n")) == 3
        assert "Note 1" in result.stdout
        result2 = runner.invoke(app, ["delete", "1", "--force"])
        assert result2.exit_code == 0
        assert "id 1 deleted" in result2.stdout.lower()

    def test_delete_not_found(self):
        result = runner.invoke(app, ["delete", "1", "--force"])
        assert result.exit_code == 1
        assert "No note under id 1 found." in result.stdout
