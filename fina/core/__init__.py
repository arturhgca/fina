from . import _database
from ._dimensions import Currency, Budget, Balance, Source, Sink, Category

_database.db.connect()
_database.db.create_tables([Currency, Budget, Balance, Source, Sink, Category])
