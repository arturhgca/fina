from . import _database
from ._entities import (
    Currency,
    Budget,
    Balance,
    Source,
    Sink,
    Category,
    Income,
    Transaction,
    ExchangeTransaction,
    Expense,
    Allocation,
)

_database.db.connect()
_database.db.create_tables(
    [
        Currency,
        Budget,
        Balance,
        Source,
        Sink,
        Category,
        Income,
        Transaction,
        ExchangeTransaction,
        Expense,
        Allocation,
    ]
)
