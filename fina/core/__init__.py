from . import _database
from core._entities import Balance, Currency, Transaction, AggregateTransaction

_database.db.connect()
_database.db.create_tables([Currency, Balance, Transaction, AggregateTransaction])
