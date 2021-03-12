from typing import List

import typer

from simple_note_taker.config import config
from simple_note_taker.core.notes import Note, NoteInDB, Notes
from simple_note_taker.help_texts import *
from simple_note_taker.subcommands.config import config_app


def check_for_reminders():
    reminders = Notes.due_reminders()
    if len(reminders) > 0:
        typer.secho(f"{len(reminders)} reminders due! Mark these as done soon.")
        typer.secho("---------------------------------------")
        print_notes(reminders)
        typer.secho("---------------------------------------")


app = typer.Typer(callback=check_for_reminders)
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
    Take a note and save it.
    """
    note_content = note.strip()
    note = Note(content=note_content, private=private).save()
    typer.secho(f"Saved with id {note.doc_id}.")


# Retrieval subcommands
@app.command()
def search(term: str):
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
    Lists all the task notes that are not complete, sorted by due date.
    """
    all_tasks = Notes.all_tasks(include_complete)
    if count == 0:
        count = len(all_tasks)
    latest_notes = sorted(all_tasks, reverse=True)[:count]
    typer.secho(f"Last {min(count, len(latest_notes))} notes")
    print_notes(latest_notes)


@app.command()
def mark_done(note_id=typer.Argument(...)):
    note = Notes.get_by_id(note_id)
    if note is not None:
        note.mark_as_done()
        note.save()
        typer.secho(f"Marked note {note_id} as done.")
    else:
        typer.secho(f"No note under id {note_id} found.")


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
    Edit a note in the DB
    """
    note = Notes.get_by_id(note_id)
    if note is not None:
        typer.secho(note.pretty_str())
        update = typer.prompt("New content")
        note.content = update
        note.save()
    else:
        typer.secho(f"No note of ID {note_id}")


@app.command()
def delete(
        note_id: int = typer.Argument(..., help=DELETE_NOTE_ID_HELP),
        force: bool = typer.Option(False),
):
    """
    Delete a note in the DB.
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


if __name__ == "__main__":
    app()
