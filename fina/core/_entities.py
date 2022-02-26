from __future__ import annotations

import datetime

from peewee import (
    Model,
    CharField,
    TextField,
    IntegerField,
    ForeignKeyField,
    DateTimeField,
)

from ._database import db


class BaseModel(Model):
    class Meta:
        database = db

    created = DateTimeField(default=datetime.datetime.now())
    last_updated = DateTimeField(default=datetime.datetime.now())


class Currency(BaseModel):
    code = CharField(max_length=3, unique=True)
    decimals = IntegerField()


class Balance(BaseModel):
    _type = CharField(column_name="type")
    name = CharField(unique=True)
    description = TextField(null=True)
    currency = ForeignKeyField(Currency, backref="balances")
    _value = IntegerField(null=True, column_name="value")

    @property
    def type(self) -> str:
        return self._type

    @type.setter
    def type(self, value: str):
        if self._type and self._type != value:
            raise ValueError("This attribute cannot be modified!")
        elif value not in ["real", "virtual", "void"]:
            raise ValueError("Type can only be one of 'real', 'virtual', or 'void'!")
        else:
            self._type = value

    @property
    def value(self) -> int:
        return self._value

    @value.setter
    def value(self, value: int):
        if self._type == "void":
            raise ValueError("Void balances cannot have a value!")
        else:
            self._value = value

    @classmethod
    def create_real(
        cls, *, name: str, description: str = None, currency: Currency, value: int
    ) -> Balance:
        return cls.create(
            type="real",
            name=name,
            description=description,
            currency=currency,
            value=value,
        )

    @classmethod
    def create_virtual(
        cls, *, name: str, description: str = None, currency: Currency, value: int
    ) -> Balance:
        return cls.create(
            type="virtual",
            name=name,
            description=description,
            currency=currency,
            value=value,
        )

    @classmethod
    def create_void(
        cls, *, name: str, description: str = None, currency: Currency
    ) -> Balance:
        return cls.create(
            type="void", name=name, description=description, currency=currency
        )
