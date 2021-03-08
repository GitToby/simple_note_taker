import re
from datetime import datetime, timedelta
from typing import List

import typer
from tinydb import Query

from simple_note_taker.config import config
from simple_note_taker.database.core import notes_db
from simple_note_taker.help_texts import *
from simple_note_taker.model import Note
from simple_note_taker.subcommands.config import config_app

app = typer.Typer()
app.add_typer(config_app, name="config")


def print_notes(notes_to_print: List[Note]) -> None:
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
    n = Note(content=note_content, private=private)
    n_id = notes_db.insert(n.as_insertable())
    typer.secho(f"Saved with id {n_id}.")


# Retrieval subcommands
@app.command()
def search(term: str):
    """
    Search your notes you've saved previously
    """
    q = Query()
    search_res = notes_db.search(q.content.search(term, flags=re.IGNORECASE))
    found_notes = [Note(**n, doc_id=n.doc_id) for n in search_res]
    typer.secho(f'Found {len(found_notes)} notes matching "{term}"')
    print_notes(found_notes)


@app.command()
def ls(count: int = typer.Argument(10)):
    """
    Fetch the latest notes you've taken
    """
    all_notes = [Note(**n, doc_id=n.doc_id) for n in notes_db.all()]
    latest_notes = sorted(all_notes, reverse=True)[:count]
    typer.secho(f"Last {min(count, len(latest_notes))} notes")
    print_notes(latest_notes)


@app.command()
def since(
        date: datetime = typer.Option(
            str(datetime.now().date() - timedelta(days=7)), prompt=True
        )
):
    """
    Print notes since a given date
    """
    search_res = [
        Note(**n, doc_id=n.doc_id) for n in notes_db.search(Query().time_taken > date)
    ]
    typer.secho(f"Found {len(search_res)} notes since {date}")
    print_notes(search_res)


# Editing
@app.command()
def size():
    """
    Returns details on the size of you notes
    """
    typer.secho(f"There are {len(notes_db)} notes in the database")


@app.command()
def edit(note_id: int = typer.Argument(..., help=NOTES_EDIT_NOTE_ID_HELP)):
    """
    Edit a note in the DB
    """
    notes_get = notes_db.get(doc_id=note_id)
    if notes_get is not None:
        note = Note(**notes_get, doc_id=notes_get.doc_id)
        typer.secho(note.pretty_str())
        update = typer.prompt("New content")
        note.content = update
        notes_db.update(note.as_insertable(), doc_ids=[note.doc_id])
    else:
        typer.secho(f"No note of ID {note_id}")


@app.command()
def delete(
        note_id: int = typer.Argument(..., help=NOTES_DELETE_NOTE_ID_HELP),
        force: bool = typer.Option(False),
):
    """
    Delete a note in the DB
    """
    notes_get = notes_db.get(doc_id=note_id)
    if notes_get is not None:
        note = Note(**notes_get, doc_id=notes_get.doc_id)
        typer.secho(note.pretty_str())
        if force or typer.prompt("Are you sure you want to delete this note?"):
            notes_db.remove(doc_ids=[note_id])
            typer.secho(f"Note under ID {note_id} deleted.")
        else:
            typer.secho("Nothing deleted")
    else:
        typer.secho(f"No note under id {note_id} found.")


if __name__ == "__main__":
    app()
