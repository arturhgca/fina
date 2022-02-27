from __future__ import annotations

from peewee import CharField, IntegerField, ForeignKeyField

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

    @classmethod
    def new(cls, *, parent: Budget, name: str, starting_value: int = 0) -> Balance:
        return cls.create(budget=parent, name=name, starting_value=starting_value)


class Source(BaseModel):
    name = CharField(unique=True)
    budget = ForeignKeyField(Budget, backref="_sources")

    @classmethod
    def new(cls, *, parent: Budget, name: str) -> Source:
        return cls.create(budget=parent, name=name)


class Sink(BaseModel):
    name = CharField(unique=True)
    budget = ForeignKeyField(Budget, backref="_sinks")

    @classmethod
    def new(cls, *, parent: Budget, name: str) -> Sink:
        return cls.create(budget=parent, name=name)


class Category(BaseModel):
    name = CharField(unique=True)
    budget = ForeignKeyField(Budget, backref="_categories")
    starting_value = IntegerField()

    @classmethod
    def new(cls, *, parent: Budget, name: str, starting_value: int = 0) -> Category:
        return cls.create(budget=parent, name=name, starting_value=starting_value)
