from tinydb import JSONStorage, TinyDB
from tinydb_serialization import SerializationMiddleware
from tinydb_serialization.serializers import DateTimeSerializer

from simple_note_taker.config import config

_serialization = SerializationMiddleware(JSONStorage)
_serialization.register_serializer(DateTimeSerializer(), "TinyDate")

tiny_db = TinyDB(
    path=config.db_file_path,
    storage=_serialization,
    # json.dump() kwargs
    sort_keys=True,
    indent=4,
    separators=(",", ": "),
)
