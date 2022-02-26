import uuid

import pytest
from peewee import DoesNotExist

from fina.core._entities import Balance, Currency


@pytest.fixture()
def name() -> str:
    return str(uuid.uuid4())


@pytest.fixture()
def currency() -> Currency:
    try:
        currency = Currency.get(Currency.code == "BRL")
    except DoesNotExist:
        currency = Currency.create(code="BRL", decimals=2)
    return currency


@pytest.fixture()
def value() -> int:
    return 100


def test_create_real_balance(name: str, currency: Currency, value: int):
    balance_id = Balance.create_real(name=name, currency=currency, value=value).id
    balance = Balance.get_by_id(balance_id)
    assert balance.name == name
    assert balance.currency.code == "BRL"
    assert balance.value == value
    assert balance.type == "real"


def test_create_virtual_balance(name: str, currency: Currency, value: int):
    balance_id = Balance.create_virtual(name=name, currency=currency, value=value).id
    balance = Balance.get_by_id(balance_id)
    assert balance.name == name
    assert balance.currency.code == "BRL"
    assert balance.value == value
    assert balance.type == "virtual"


def test_create_real_void_balance(name: str, currency: Currency):
    balance_id = Balance.create_real_void(name=name, currency=currency).id
    balance = Balance.get_by_id(balance_id)
    assert balance.name == name
    assert balance.currency.code == "BRL"
    assert balance.type == "real"
    assert balance.value is None


def test_create_virtual_void_balance(name: str, currency: Currency):
    balance_id = Balance.create_virtual_void(name=name, currency=currency).id
    balance = Balance.get_by_id(balance_id)
    assert balance.name == name
    assert balance.currency.code == "BRL"
    assert balance.type == "virtual"
    assert balance.value is None
