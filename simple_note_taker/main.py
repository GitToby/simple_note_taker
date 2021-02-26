import os
import re
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path

import typer
from tinydb import TinyDB, Query, JSONStorage
from tinydb_serialization import SerializationMiddleware
from tinydb_serialization.serializers import DateTimeSerializer

app = typer.Typer()

snt_home_dir = os.sep.join([str(Path.home()), ".simpleNoteTaker"])

if not Path(snt_home_dir).exists():
    os.mkdir(snt_home_dir)

db_file = os.sep.join([snt_home_dir, "database.json"])

serialization = SerializationMiddleware(JSONStorage)
serialization.register_serializer(DateTimeSerializer(), 'TinyDate')

db = TinyDB(
    path=db_file,
    storage=serialization,
    # json.dump() kwargs
    sort_keys=True,
    indent=4,
    separators=(',', ': ')
)

notes = db.table("notes")


@dataclass
class Note:
    """
    A crude ORM of sorts
    """
    content: str
    doc_id: int = None
    time_taken: datetime = datetime.now()

    def pretty_str(self) -> str:
        return f"Note {self.doc_id}: {self.time_taken.strftime('%H:%M, %a %d %b %Y')} | {self.content}"

    def as_insertable(self) -> dict:
        tmp = asdict(self)
        del tmp['doc_id']  # this shouldn't be inserted into the db again
        return tmp

    def __lt__(self, other) -> bool:
        return self.time_taken < other.time_taken


@app.command()
def take(note: str = typer.Option(..., prompt="Note content")):
    """
    Take a note and save it.
    """
    note_content = note.strip()
    n = Note(note_content)
    n_id = notes.insert(n.as_insertable())
    typer.secho(f"Saved with id {n_id}.")


@app.command()
def search(term: str):
    """
    Search your notes you've saved previously
    """
    q = Query()
    search_res = notes.search(q.content.search(term, flags=re.IGNORECASE))
    found_notes = [Note(**n, doc_id=n.doc_id) for n in search_res]
    typer.secho(f"Found {len(found_notes)} notes matching \"{term}\"")
    for i, note in enumerate(found_notes):
        typer.secho(f'({i})\t{note}')


@app.command()
def latest(count: int = typer.Argument(10)):
    """
    Fetch the latest notes you've taken
    """
    all_notes = [Note(**n, doc_id=n.doc_id) for n in notes.all()]
    latest_notes = sorted(all_notes, reverse=True)[:count]
    typer.secho(f"Last {min(count, len(latest_notes))} notes")
    for note in latest_notes:
        typer.secho(" - " + note.pretty_str())


@app.command()
def since(date: datetime = typer.Option(str(datetime.now().date() - timedelta(days=7)), prompt=True)):
    """
    Print notes since a given date
    """
    search_res = [Note(**n, doc_id=n.doc_id) for n in notes.search(Query().time_taken > date)]
    typer.secho(f"Found {len(search_res)} notes since {date}")
    for note in search_res:
        typer.secho(" - " + note.pretty_str())


@app.command()
def edit(note_id: int = typer.Argument(..., help="Note ID to of note edit")):
    """
    Edit a note in the DB
    """
    notes_get = notes.get(doc_id=note_id)
    if notes_get is not None:
        note = Note(**notes_get, doc_id=notes_get.doc_id)
        typer.secho(note.pretty_str())
        update = typer.prompt("New content")
        note.content = update
        notes.update(note.as_insertable(), doc_ids=[note.doc_id])
    else:
        typer.secho(f"No note of ID {note_id}")


if __name__ == "__main__":
    app()
