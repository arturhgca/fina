import datetime
import uuid

import pytest
from peewee import DoesNotExist

from fina.core._entities import Balance, Currency, Transaction


@pytest.fixture()
def name() -> str:
    return str(uuid.uuid4())


def _currency() -> Currency:
    try:
        currency = Currency.get(Currency.code == "BRL")
    except DoesNotExist:
        currency = Currency.create(code="BRL", decimals=2)
    return currency


def _currency_jpy() -> Currency:
    try:
        currency = Currency.get(Currency.code == "JPY")
    except DoesNotExist:
        currency = Currency.create(code="JPY", decimals=0)
    return currency


@pytest.fixture()
def currency() -> Currency:
    return _currency()


@pytest.fixture()
def value() -> int:
    return 100


@pytest.fixture()
def occurred() -> datetime:
    return datetime.datetime.now()


def real_balance() -> Balance:
    return Balance.create_real(name=str(uuid.uuid4()), currency=_currency(), value=100)


@pytest.fixture()
def source_real_balance() -> Balance:
    return real_balance()


@pytest.fixture()
def target_real_balance() -> Balance:
    return real_balance()


@pytest.fixture()
def target_real_balance_jpy() -> Balance:
    balance = real_balance()
    balance.currency = _currency_jpy()
    balance.save()
    return balance


def virtual_balance() -> Balance:
    return Balance.create_virtual(
        name=str(uuid.uuid4()), currency=_currency(), value=100
    )


@pytest.fixture()
def source_virtual_balance() -> Balance:
    return virtual_balance()


@pytest.fixture()
def target_virtual_balance() -> Balance:
    return virtual_balance()


def void_balance() -> Balance:
    return Balance.create_void(name=str(uuid.uuid4()), currency=_currency())


@pytest.fixture()
def source_void_balance() -> Balance:
    return void_balance()


@pytest.fixture()
def source_value() -> int:
    return 20000


@pytest.fixture()
def target_value() -> int:
    return 4000


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


def test_create_void_balance(name: str, currency: Currency):
    balance_id = Balance.create_void(name=name, currency=currency).id
    balance = Balance.get_by_id(balance_id)
    assert balance.name == name
    assert balance.currency.code == "BRL"
    assert balance.type == "real"
    assert balance.value is None


def test_create_real_transaction(
    occurred: datetime,
    source_real_balance: Balance,
    target_real_balance: Balance,
    source_value: int,
):
    transaction_id = Transaction.create_from_balances(
        occurred=occurred,
        source_balance=source_real_balance,
        target_balance=target_real_balance,
        source_value=source_value,
    ).id
    transaction = Transaction.get_by_id(transaction_id)
    assert transaction.source_balance == source_real_balance
    assert transaction.target_balance == target_real_balance
    assert transaction.source_value == source_value
    assert transaction.type == "real"


def test_create_real_transaction_with_void_balance(
    occurred: datetime,
    source_void_balance: Balance,
    target_real_balance: Balance,
    source_value: int,
):
    transaction_id = Transaction.create_from_balances(
        occurred=occurred,
        source_balance=source_void_balance,
        target_balance=target_real_balance,
        source_value=source_value,
    ).id
    transaction = Transaction.get_by_id(transaction_id)
    assert transaction.source_balance == source_void_balance
    assert transaction.target_balance == target_real_balance
    assert transaction.source_value == source_value
    assert transaction.type == "real"


def test_create_virtual_transaction(
    occurred: datetime,
    source_virtual_balance: Balance,
    target_virtual_balance: Balance,
    source_value: int,
):
    transaction_id = Transaction.create_from_balances(
        occurred=occurred,
        source_balance=source_virtual_balance,
        target_balance=target_virtual_balance,
        source_value=source_value,
    ).id
    transaction = Transaction.get_by_id(transaction_id)
    assert transaction.source_balance == source_virtual_balance
    assert transaction.target_balance == target_virtual_balance
    assert transaction.source_value == source_value
    assert transaction.type == "virtual"


def test_create_transaction_with_different_balance_types(
    occurred: datetime,
    source_real_balance: Balance,
    target_virtual_balance: Balance,
    source_value: int,
):
    with pytest.raises(ValueError):
        Transaction.create_from_balances(
            occurred=occurred,
            source_balance=source_real_balance,
            target_balance=target_virtual_balance,
            source_value=source_value,
        )


def test_create_transaction_with_different_currencies(
    occurred: datetime,
    source_real_balance: Balance,
    target_real_balance_jpy: Balance,
    source_value: int,
    target_value: int,
):
    transaction_id = Transaction.create_from_balances(
        occurred=occurred,
        source_balance=source_real_balance,
        target_balance=target_real_balance_jpy,
        source_value=source_value,
        target_value=target_value,
    ).id
    transaction = Transaction.get_by_id(transaction_id)
    assert transaction.source_balance == source_real_balance
    assert transaction.target_balance == target_real_balance_jpy
    assert transaction.source_value == source_value
    assert transaction.target_value == target_value
    assert transaction.type == "real"
    assert transaction.vet == 20
