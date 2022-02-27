from __future__ import annotations

import datetime

from peewee import CharField, IntegerField, ForeignKeyField, DateTimeField, TextField

from ._database import BaseModel


class Currency(BaseModel):
    code = CharField(unique=True, max_length=3)
    decimals = IntegerField()

    @classmethod
    def new(cls, *, code: str, decimals: int) -> Currency:
        return cls.create(code=code, decimals=decimals)


class Budget(BaseModel):
    name = CharField(unique=True)
    currency = ForeignKeyField(Currency, backref="budgets")

    @classmethod
    def new(cls, *, currency: Currency, name: str) -> Budget:
        return cls.create(currency=currency, name=name)


class Balance(BaseModel):
    name = CharField(unique=True)
    budget = ForeignKeyField(Budget, backref="balances")
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

    @classmethod
    def new(cls, *, budget: Budget, name: str, starting_value: int = 0) -> Balance:
        return cls.create(budget=budget, name=name, starting_value=starting_value)


class Source(BaseModel):
    name = CharField(unique=True)
    budget = ForeignKeyField(Budget, backref="sources")

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

    @classmethod
    def new(cls, *, budget: Budget, name: str) -> Source:
        return cls.create(budget=budget, name=name)


class Sink(BaseModel):
    name = CharField(unique=True)
    budget = ForeignKeyField(Budget, backref="sinks")

    @classmethod
    def new(cls, *, budget: Budget, name: str) -> Sink:
        return cls.create(budget=budget, name=name)


class Category(BaseModel):
    name = CharField(unique=True)
    budget = ForeignKeyField(Budget, backref="categories")
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

    @classmethod
    def new(cls, *, budget: Budget, name: str, starting_value: int = 0) -> Category:
        return cls.create(budget=budget, name=name, starting_value=starting_value)


class Income(BaseModel):
    value = IntegerField()
    source = ForeignKeyField(Source, backref="transactions")
    destination = ForeignKeyField(Balance, backref="incomes")
    when = DateTimeField()
    description = TextField(null=True)


class Transaction(BaseModel):
    value = IntegerField()
    source = ForeignKeyField(Balance, backref="outgoing_transactions")
    destination = ForeignKeyField(Balance, backref="incoming_transactions")
    when = DateTimeField()
    description = TextField(null=True)


class ExchangeTransaction(BaseModel):
    source_value = IntegerField()
    destination_value = IntegerField()
    source = ForeignKeyField(Balance, backref="outgoing_exchange_transactions")
    destination = ForeignKeyField(Balance, backref="incoming_exchange_transactions")
    when = DateTimeField()
    description = TextField(null=True)


class Expense(BaseModel):
    value = IntegerField()
    source = ForeignKeyField(Balance, backref="expenses")
    destination = ForeignKeyField(Sink, backref="transactions")
    when = DateTimeField()
    description = TextField(null=True)


class Allocation(BaseModel):
    value = IntegerField()
    category = ForeignKeyField(Category, backref="allocations")
    when = DateTimeField()
    description = TextField(null=True)
