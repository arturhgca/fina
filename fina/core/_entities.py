from __future__ import annotations

import datetime
from decimal import Decimal

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
    code: str = CharField(max_length=3, unique=True)
    decimals: int = IntegerField()

    def parse_value(self, integer_value: int) -> Decimal:
        return Decimal(integer_value) / (10**self.decimals)


class Balance(BaseModel):
    _type: str = CharField(column_name="type")
    name: str = CharField(unique=True)
    description: str = TextField(null=True)
    currency: Currency = ForeignKeyField(Currency, backref="balances")
    _value: int = IntegerField(null=True, column_name="value", default=0)

    @property
    def type(self) -> str:
        return self._type

    @type.setter
    def type(self, value: str):
        if self._type and self._type != value:
            raise ValueError("This attribute cannot be modified!")
        elif value not in ["real", "virtual"]:
            raise ValueError("Type can only be one of 'real' or 'virtual'!")
        else:
            self._type = value

    @property
    def value(self) -> int:
        return self._value

    @value.setter
    def value(self, value: int):
        if self._value is None:
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
            type="real",
            name=name,
            description=description,
            currency=currency,
            value=None,
        )


class Transaction(BaseModel):
    _type: str = CharField(column_name="type")
    description: str = TextField(null=True)
    occurred = DateTimeField()
    source_balance: Balance = ForeignKeyField(Balance, backref="outgoing_transactions")
    target_balance: Balance = ForeignKeyField(Balance, backref="incoming_transactions")
    source_value: int = IntegerField()
    target_value: int = IntegerField(null=True)

    @property
    def type(self) -> str:
        return self._type

    @type.setter
    def type(self, value: str):
        if self._type and self._type != value:
            raise ValueError("This attribute cannot be modified!")
        elif value not in ["real", "virtual"]:
            raise ValueError("Type can only be one of 'real' or 'virtual'!")
        else:
            self._type = value

    @property
    def vet(self) -> Decimal:
        if self.target_value:
            return self.target_balance.currency.parse_value(
                self.target_value
            ) / self.source_balance.currency.parse_value(self.source_value)
        else:
            return Decimal(1)

    @classmethod
    def create_from_balances(
        cls,
        *,
        description: str = None,
        occurred: datetime,
        source_balance: Balance,
        target_balance: Balance,
        source_value: int,
        target_value: int = None,
    ) -> Transaction:
        if (transaction_type := source_balance.type) != target_balance.type:
            raise ValueError(
                "The target balance must have the same type as the source balance!"
            )
        return cls.create(
            type=transaction_type,
            description=description,
            occurred=occurred,
            source_balance=source_balance,
            target_balance=target_balance,
            source_value=source_value,
            target_value=target_value,
        )
