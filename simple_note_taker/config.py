import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Union

from .__version__ import VERSION

APP_NAME = "simpleNoteTaker"

snt_home_dir = (
        Path().home() / f".{APP_NAME}"
)  # maybe migrate to `typer.get_app_dir(APP_NAME)`
config_file_path = snt_home_dir / "config.json"

# init the config dir location
if not Path(snt_home_dir).exists():
    os.mkdir(snt_home_dir)


@dataclass
class MetaData:
    cli_version: str = (
        VERSION  # used for when we need to prompt to update the cli config
    )


@dataclass
class Configuration:
    username: str = None
    default_private: bool = False
    share_enabled: bool = False

    db_file_path: str = str(snt_home_dir / "database.json")
    metadata: MetaData = MetaData()


def write_config_to_file(configuration: Configuration):
    with open(config_file_path, "w+") as f:
        conf_dict = asdict(configuration)
        json.dump(conf_dict, f, sort_keys=True, indent=4, separators=(",", ": "))


def read_config_from_file(file_path: Union[str, Path]) -> Configuration:
    with open(file_path) as f:
        config_dict = json.load(f)

    return Configuration(**config_dict)


def _get_conf() -> Configuration:
    if not config_file_path.is_file():
        write_config_to_file(Configuration())

    return read_config_from_file(config_file_path)


config = _get_conf()
