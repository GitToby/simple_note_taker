import re
from datetime import datetime, timedelta
from typing import List

import typer
from tinydb import Query

from simple_note_taker.config import config
from simple_note_taker.database import notes
from simple_note_taker.help_texts import *
from simple_note_taker.model import Note
from simple_note_taker.subcommands.config import config_app
from simple_note_taker.subcommands.notes import notes_app

app = typer.Typer()
app.add_typer(config_app, name="config")
app.add_typer(notes_app, name="notes")


def print_notes(notes_to_print: List[Note]) -> None:
    for note in notes_to_print:
        typer.secho(" - " + note.pretty_str())


# Insert Commands
@app.command()
def take(note: str = typer.Option(..., prompt=TAKE_NOTE_PROMPT), private: bool = typer.Option(config.default_private)):
    """
    Take a note and save it.
    """
    note_content = note.strip()
    n = Note(content=note_content, private=private)
    n_id = notes.insert(n.as_insertable())
    typer.secho(f"Saved with id {n_id}.")


# Retrieval subcommands
@app.command()
def search(term: str):
    """
    Search your notes you've saved previously
    """
    q = Query()
    search_res = notes.search(q.content.search(term, flags=re.IGNORECASE))
    found_notes = [Note(**n, doc_id=n.doc_id) for n in search_res]
    typer.secho(f"Found {len(found_notes)} notes matching \"{term}\"")
    print_notes(found_notes)


@app.command()
def latest(count: int = typer.Argument(10)):
    """
    Fetch the latest notes you've taken
    """
    all_notes = [Note(**n, doc_id=n.doc_id) for n in notes.all()]
    latest_notes = sorted(all_notes, reverse=True)[:count]
    typer.secho(f"Last {min(count, len(latest_notes))} notes")
    print_notes(latest_notes)


@app.command()
def since(date: datetime = typer.Option(str(datetime.now().date() - timedelta(days=7)), prompt=True)):
    """
    Print notes since a given date
    """
    search_res = [Note(**n, doc_id=n.doc_id) for n in notes.search(Query().time_taken > date)]
    typer.secho(f"Found {len(search_res)} notes since {date}")
    print_notes(search_res)


if __name__ == "__main__":
    app()
