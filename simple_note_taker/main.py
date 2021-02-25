import os
import re
from dataclasses import dataclass, asdict
from datetime import datetime
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
    content: str
    time_taken: datetime = datetime.now()

    def __repr__(self):
        return f"{self.time_taken.strftime('%H:%M, %a %d %b %Y')} | {self.content}"


@app.command()
def take(note: str = typer.Option(..., prompt="Note content")):
    n_id = notes.insert(asdict(Note(note)))
    typer.secho(f"Saved with id {n_id}.")


@app.command()
def search(term: str):
    q = Query()
    search_res = notes.search(q.content.search(term, flags=re.IGNORECASE))
    found_notes = [Note(**n) for n in search_res]
    typer.secho(f"Found {len(found_notes)} notes matching \"{term}\"")
    for i, note in enumerate(found_notes):
        typer.secho(f'({i})\t{note}')


@app.command()
def latest(count: int = 5):
    typer.secho(f"Last {count} notes")
    for i, note in enumerate(notes.all())[:count]:
        typer.secho(f'({i})\t{note}')


def edit(note_id: int):
    pass


if __name__ == "__main__":
    app()
