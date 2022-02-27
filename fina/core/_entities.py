from __future__ import annotations

import datetime

from peewee import CharField, IntegerField, ForeignKeyField, DateTimeField, TextField

from ._database import BaseModel


class SmartList:
    def __init__(self, wrapping, of_type, belonging_to):
        self.original_list = wrapping
        self.entity_type = of_type
        self.parent = belonging_to

    def add(self, **kwargs):
        return self.entity_type.new(parent=self.parent, **kwargs)


class Currency(BaseModel):
    code = CharField(unique=True, max_length=3)
    decimals = IntegerField()

    @property
    def budgets(self):
        return SmartList(wrapping=self._budgets, of_type=Budget, belonging_to=self)

    @classmethod
    def new(cls, *, code: str, decimals: int) -> Currency:
        return cls.create(code=code, decimals=decimals)


class Budget(BaseModel):
    name = CharField(unique=True)
    currency = ForeignKeyField(Currency, backref="_budgets")

    @property
    def balances(self):
        return SmartList(wrapping=self._balances, of_type=Balance, belonging_to=self)

    @property
    def sources(self):
        return SmartList(wrapping=self._sources, of_type=Source, belonging_to=self)

    @property
    def sinks(self):
        return SmartList(wrapping=self._sinks, of_type=Sink, belonging_to=self)

    @property
    def categories(self):
        return SmartList(wrapping=self._categories, of_type=Category, belonging_to=self)

    @classmethod
    def new(cls, *, parent: Currency, name: str) -> Budget:
        return cls.create(currency=parent, name=name)


class Balance(BaseModel):
    name = CharField(unique=True)
    budget = ForeignKeyField(Budget, backref="_balances")
    starting_value = IntegerField()

    def transfer(
        self, *, value: int, to: Balance, when: datetime, description: str = None
    ) -> Balance:
        Transaction.create(
            value=value,
            source=self,
            destination=to,
            when=when,
            description=description,
        )
        return self

    def convert(
        self,
        *,
        convert: int,
        into: int,
        to: Balance,
        when: datetime,
        deducing_from_category: Category,
        adding_to_category: Category,
        description: str = None,
    ) -> Balance:
        ExchangeTransaction.create(
            source_value=convert,
            destination_value=into,
            source=self,
            destination=to,
            when=when,
            description=description,
        )
        deducing_from_category.deallocate(
            value=convert,
            when=when,
            description=description,
        )
        adding_to_category.allocate(
            value=into,
            when=when,
            description=description,
        )
        return self

    def pay(
        self,
        *,
        value: int,
        to: Balance,
        when: datetime,
        category: Category = None,
        description: str = None,
    ) -> Source:
        Expense.create(
            value=value,
            source=self,
            destination=to,
            when=when,
            description=description,
        )
        if category:
            category.deallocate(
                value=value,
                when=when,
                description=description,
            )
        return self

    @property
    def incomes(self):
        return SmartList(wrapping=self._incomes, of_type=Income, belonging_to=self)

    @property
    def outgoing_transactions(self):
        return SmartList(
            wrapping=self._outgoing_transactions, of_type=Transaction, belonging_to=self
        )

    @property
    def incoming_transactions(self):
        return SmartList(
            wrapping=self._incoming_transactions, of_type=Transaction, belonging_to=self
        )

    @property
    def outgoing_exchange_transactions(self):
        return SmartList(
            wrapping=self._outgoing_exchange_transactions,
            of_type=ExchangeTransaction,
            belonging_to=self,
        )

    @property
    def incoming_exchange_transactions(self):
        return SmartList(
            wrapping=self._incoming_exchange_transactions,
            of_type=ExchangeTransaction,
            belonging_to=self,
        )

    @property
    def expenses(self):
        return SmartList(wrapping=self._expenses, of_type=Expense, belonging_to=self)

    @classmethod
    def new(cls, *, parent: Budget, name: str, starting_value: int = 0) -> Balance:
        return cls.create(budget=parent, name=name, starting_value=starting_value)


class Source(BaseModel):
    name = CharField(unique=True)
    budget = ForeignKeyField(Budget, backref="_sources")

    def pay(
        self,
        *,
        value: int,
        to: Balance,
        when: datetime,
        category: Category = None,
        description: str = None,
    ) -> Source:
        Income.create(
            value=value,
            source=self,
            destination=to,
            when=when,
            description=description,
        )
        if category:
            category.allocate(
                value=value,
                when=when,
                description=description,
            )
        return self

    @property
    def transactions(self):
        return SmartList(wrapping=self._transactions, of_type=Income, belonging_to=self)

    @classmethod
    def new(cls, *, parent: Budget, name: str) -> Source:
        return cls.create(budget=parent, name=name)


class Sink(BaseModel):
    name = CharField(unique=True)
    budget = ForeignKeyField(Budget, backref="_sinks")

    @property
    def transactions(self):
        return SmartList(
            wrapping=self._transactions, of_type=Expense, belonging_to=self
        )

    @classmethod
    def new(cls, *, parent: Budget, name: str) -> Sink:
        return cls.create(budget=parent, name=name)


class Category(BaseModel):
    name = CharField(unique=True)
    budget = ForeignKeyField(Budget, backref="_categories")
    starting_value = IntegerField()

    def allocate(
        self, *, value: int, when: datetime, description: str = None
    ) -> Category:
        Allocation.create(
            value=value,
            category=self,
            when=when,
            description=description,
        )
        return self

    def deallocate(
        self, *, value: int, when: datetime, description: str = None
    ) -> Category:
        return self.allocate(
            value=-value,
            when=when,
            description=description,
        )

    @property
    def allocations(self):
        return SmartList(
            wrapping=self._allocations, of_type=Allocation, belonging_to=self
        )

    @classmethod
    def new(cls, *, parent: Budget, name: str, starting_value: int = 0) -> Category:
        return cls.create(budget=parent, name=name, starting_value=starting_value)


class Income(BaseModel):
    value = IntegerField()
    source = ForeignKeyField(Source, backref="_transactions")
    destination = ForeignKeyField(Balance, backref="_incomes")
    when = DateTimeField()
    description = TextField(null=True)


class Transaction(BaseModel):
    value = IntegerField()
    source = ForeignKeyField(Balance, backref="_outgoing_transactions")
    destination = ForeignKeyField(Balance, backref="_incoming_transactions")
    when = DateTimeField()
    description = TextField(null=True)


class ExchangeTransaction(BaseModel):
    source_value = IntegerField()
    destination_value = IntegerField()
    source = ForeignKeyField(Balance, backref="_outgoing_exchange_transactions")
    destination = ForeignKeyField(Balance, backref="_incoming_exchange_transactions")
    when = DateTimeField()
    description = TextField(null=True)


class Expense(BaseModel):
    value = IntegerField()
    source = ForeignKeyField(Balance, backref="_expenses")
    destination = ForeignKeyField(Sink, backref="_transactions")
    when = DateTimeField()
    description = TextField(null=True)


class Allocation(BaseModel):
    value = IntegerField()
    category = ForeignKeyField(Category, backref="_allocations")
    when = DateTimeField()
    description = TextField(null=True)
