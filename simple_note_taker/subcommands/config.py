from dataclasses import asdict

import typer

from simple_note_taker.config import Configuration, config, config_file_path, write_config_to_file
from simple_note_taker.help_texts import CONFIG_APP_HELP, CONFIG_SET_USERNAME_PROMPT

config_app = typer.Typer(help=CONFIG_APP_HELP)


@config_app.command(name="print")
def print_config():
    """
    List the configuration or open the file in the file explorer.
    """
    typer.secho(f"Config settings from {config_file_path}")
    typer.secho(str(config))


@config_app.command(name="open")
def open_conf_path():
    """
    Open the config file location
    """
    typer.launch(str(config_file_path), locate=True)


@config_app.command()
def update():
    """
    Updates the configurations file with missing defaults, keeps existing settings.
    """
    conf_dict = {**asdict(Configuration()), **asdict(config)}
    write_config_to_file(Configuration(**conf_dict))
    typer.secho(f"Updated missing config with default settings")
    print_config()


@config_app.command()
def set_username(username: str = typer.Option(..., prompt=CONFIG_SET_USERNAME_PROMPT)):
    """
    Updates the username in the configuration. This will also push change of username to any remote servers
    """
    config.username = username
    write_config_to_file(config)
    typer.secho(f"Updated username to: {config.username}")
