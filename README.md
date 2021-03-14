A simple CLI note taker, written in Python.

Home: https://github.com/GitToby/simple_note_taker
Pypi: https://pypi.org/project/simple-note-taker/

# Install

Via `pip`

```commandline
pip install simple_note_taker
```

# Usage.

```commandline
Usage: snt [OPTIONS] COMMAND [ARGS]...

Options:
  --version
  --install-completion [bash|zsh|fish|powershell|pwsh]
                                  Install completion for the specified shell.
  --show-completion [bash|zsh|fish|powershell|pwsh]
                                  Show completion for the specified shell, to
                                  copy it or customize the installation.

  --help                          Show this message and exit.

Commands:
  config     For interacting with configuration tooling
  delete     Delete a note you've taken.
  edit       Edit a note you've taken.
  ls         Fetch the latest notes you've taken.
  mark-done  Mark a task type note as done.
  match      Search your notes you've saved previously which match a search...
  search
  size       Returns details on the size of you notes.
  take       Take a note and save it.
  tasks      Lists notes marked as Tasks.
```

Dev with [Poetry](https://python-poetry.org/). Run tests from root with `pytest --cov=simple_note_taker`