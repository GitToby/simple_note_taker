import typer

from simple_note_taker.database import notes
from simple_note_taker.help_texts import NOTES_APP_HELP, NOTES_EDIT_NOTE_ID_HELP
from simple_note_taker.model import Note

notes_app = typer.Typer(help=NOTES_APP_HELP)


@notes_app.command()
def size():
    typer.secho(f'There are {len(notes)} notes in the database')


@notes_app.command()
def edit(note_id: int = typer.Argument(..., help=NOTES_EDIT_NOTE_ID_HELP)):
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
