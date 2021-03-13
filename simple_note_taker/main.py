from typing import List, Optional

import typer

from simple_note_taker.config import config
from simple_note_taker.core.notes import Note, NoteInDB, Notes, DATE_FORMAT
from simple_note_taker.help_texts import *
from simple_note_taker.subcommands.config import config_app

import pkg_resources

_DISTRIBUTION_METADATA = pkg_resources.get_distribution("simple_note_taker")

__version__ = _DISTRIBUTION_METADATA.version


def version_callback(value: bool):
    if value:
        typer.echo(__version__)
        raise typer.Exit()


def check_for_reminders(version: Optional[bool] = typer.Option(None, "--version", callback=version_callback)):
    reminders = Notes.due_reminders()
    if len(reminders) > 0:
        reminder_str = f"{len(reminders)} reminders due! Mark these as done soon."
        typer.secho(reminder_str)
        typer.secho("-" * len(reminder_str))
        print_notes(reminders)
        typer.secho("-" * len(reminder_str))


app = typer.Typer(name="Simple Note Taker", callback=check_for_reminders)
app.add_typer(config_app, name="config")


def print_notes(notes_to_print: List[NoteInDB]) -> None:
    for note in notes_to_print:
        typer.secho(" - " + note.pretty_str())


# Insert Commands
@app.command()
def take(
        note: str = typer.Option(..., prompt=TAKE_NOTE_PROMPT),
        private: bool = typer.Option(config.default_private),
):
    """
    Take a note and save it. Include any of the magic commands to execute their functionality.

    Magic commands:
    !task - Mark a note as a task,
    !todo - Same as !task
    !chore - Same as !task
    !remindme - Mark note as a task and set a reminder. Optionally include a single timeframe block 'e.g. 2m1w4d2h5s' to set reminder date.
    !reminder - Same as !remindme
    !alert - Same as !remindme
    !private - Marks a note as private as its saved
    !secret - Same as !private
    """
    note_content = note.strip()
    note = Note(content=note_content, private=private).save()
    note_str = 'Note'
    reminder_str = ''
    if note.task:
        note_str = 'Task'
        if note.reminder:
            reminder_str = f'Reminder set for {note.reminder.strftime(DATE_FORMAT)}'

    typer.secho(f"{note_str} saved with id {note.doc_id}. {reminder_str}")


# Retrieval subcommands
@app.command()
def match(term: str):
    """
    Search your notes you've saved previously.
    """
    found_notes = Notes.search(term, "content")
    typer.secho(f'Found {len(found_notes)} notes matching "{term}"')
    print_notes(found_notes)


@app.command()
def ls(count: int = typer.Argument(10, help=LS_COUNT_HELP)):
    """
    Fetch the latest notes you've taken.
    """
    all_notes = Notes.all()
    if count == 0:
        count = len(all_notes)
    latest_notes = sorted(all_notes, reverse=True)[:count]
    typer.secho(f"Last {min(count, len(latest_notes))} notes")
    print_notes(latest_notes)


@app.command()
def tasks(include_complete: bool = typer.Option(False), count: int = typer.Argument(10, help=LS_COUNT_HELP)):
    """
    Lists notes marked as Tasks.
    """
    all_tasks = Notes.all_tasks(include_complete)
    if count == 0:
        count = len(all_tasks)
    latest_notes = sorted(all_tasks, reverse=True)[:count]
    typer.secho(f"Last {min(count, len(latest_notes))} tasks:")
    print_notes(latest_notes)


@app.command()
def mark_done(note_id: int = typer.Argument(...)):
    """
    Mark a task type note as done.
    """
    note = Notes.get_by_id(note_id)
    if note is not None:
        note.mark_as_done()
        note.update(run_magic=False)
        typer.secho(f"Marked note {note_id} as done.")
    else:
        typer.secho(f"No note under id {note_id} found.")
        raise typer.Abort()


# Editing
@app.command()
def size():
    """
    Returns details on the size of you notes.
    """
    typer.secho(f"There are {len(Notes.all())} notes in the database")


@app.command()
def edit(note_id: int = typer.Argument(..., help=EDIT_NOTE_ID_HELP)):
    """
    Edit a note you've taken.
    """
    note = Notes.get_by_id(note_id)
    if note is not None:
        typer.secho(note.pretty_str())
        update = typer.prompt("New content")
        note.content = update
        note.update()
        typer.secho(f"Note {note_id} updated.")
    else:
        typer.secho(f"No note of ID {note_id} found.")
        raise typer.Abort()


@app.command()
def delete(
        note_id: int = typer.Argument(..., help=DELETE_NOTE_ID_HELP),
        force: bool = typer.Option(False),
):
    """
    Delete a note you've taken.
    """
    note = Notes.get_by_id(note_id)
    if note is not None:
        typer.secho(note.pretty_str())
        if force or typer.confirm("Are you sure you want to delete this note?",
                                  abort=True):
            note.delete()
            typer.secho(f"Note under ID {note_id} deleted.")
    else:
        typer.secho(f"No note under id {note_id} found.")
        raise typer.Abort()


if __name__ == "__main__":
    app()
