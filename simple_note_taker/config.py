import json
import os
from dataclasses import dataclass, asdict
from pathlib import Path

import typer

APP_NAME = 'simpleNoteTaker'

snt_home_dir = Path(typer.get_app_dir(APP_NAME))
config_file = snt_home_dir / "config.json"

# init the config dir location
if not Path(snt_home_dir).exists():
    os.mkdir(snt_home_dir)


@dataclass
class Configuration:
    db_file_path: str = str(snt_home_dir / "database.json")


def write_config_to_file(configuration: Configuration):
    with open(config_file, 'w+') as f:
        conf_dict = asdict(configuration)
        json.dump(conf_dict, f, sort_keys=True, indent=4, separators=(',', ': '))
    return True


def get_conf() -> Configuration:
    if not config_file.is_file():
        write_config_to_file(Configuration())

    with open(config_file) as f:
        config_dict = json.load(f)

    return Configuration(**config_dict)
