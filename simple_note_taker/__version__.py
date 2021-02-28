import pkg_resources

_DISTRIBUTION_METADATA = pkg_resources.get_distribution('simple_note_taker')

VERSION = _DISTRIBUTION_METADATA.version
