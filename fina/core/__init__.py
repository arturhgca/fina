from . import _database
from core._entities import Balance, Currency, Transaction

_database.db.connect()
_database.db.create_tables([Currency, Balance, Transaction])
