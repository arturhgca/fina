import datetime
import uuid

import pytest
from peewee import DoesNotExist

from fina.core._entities import Balance, Currency, Transaction, AggregateTransaction


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


def occurred() -> datetime:
    return datetime.datetime.now()


def real_balance() -> Balance:
    return Balance.create_real(name=str(uuid.uuid4()), currency=_currency(), value=100)


def real_balance_jpy() -> Balance:
    balance = real_balance()
    balance.currency = _currency_jpy()
    balance.save()
    return balance


def virtual_balance_jpy() -> Balance:
    balance = virtual_balance()
    balance.currency = _currency_jpy()
    balance.save()
    return balance


def virtual_balance() -> Balance:
    return Balance.create_virtual(
        name=str(uuid.uuid4()), currency=_currency(), value=100
    )


def real_void_balance() -> Balance:
    return Balance.create_real_void(name=str(uuid.uuid4()), currency=_currency())


def virtual_void_balance() -> Balance:
    return Balance.create_virtual_void(name=str(uuid.uuid4()), currency=_currency())


@pytest.fixture()
def real_transaction_from_void() -> Transaction:
    return Transaction.create_from_balances(
        occurred=occurred(),
        source_balance=real_void_balance(),
        target_balance=real_balance_jpy(),
        source_value=10000,
        target_value=200,
    )


@pytest.fixture()
def virtual_transaction_from_void() -> Transaction:
    return Transaction.create_from_balances(
        occurred=occurred(),
        source_balance=virtual_void_balance(),
        target_balance=virtual_balance_jpy(),
        source_value=10000,
        target_value=200,
    )


@pytest.fixture()
def real_transaction_to_void() -> Transaction:
    return Transaction.create_from_balances(
        occurred=occurred(),
        source_balance=real_balance_jpy(),
        target_balance=real_void_balance(),
        source_value=10000,
        target_value=200,
    )


@pytest.fixture()
def virtual_transaction_to_void() -> Transaction:
    return Transaction.create_from_balances(
        occurred=occurred(),
        source_balance=virtual_balance_jpy(),
        target_balance=virtual_void_balance(),
        source_value=10000,
        target_value=200,
    )


def test_create_inbound_transaction(
    real_transaction_from_void: Transaction, virtual_transaction_from_void: Transaction
):
    aggregate_transaction_id = AggregateTransaction.create_inbound(
        real_transaction=real_transaction_from_void,
        virtual_transaction=virtual_transaction_from_void,
    ).id
    aggregate_transaction = AggregateTransaction.get_by_id(aggregate_transaction_id)
    assert aggregate_transaction.real_transaction == real_transaction_from_void
    assert aggregate_transaction.virtual_transaction == virtual_transaction_from_void
    assert aggregate_transaction.type == "inbound"


def test_create_outbound_transaction(
    real_transaction_to_void: Transaction, virtual_transaction_to_void: Transaction
):
    aggregate_transaction_id = AggregateTransaction.create_outbound(
        real_transaction=real_transaction_to_void,
        virtual_transaction=virtual_transaction_to_void,
    ).id
    aggregate_transaction = AggregateTransaction.get_by_id(aggregate_transaction_id)
    assert aggregate_transaction.real_transaction == real_transaction_to_void
    assert aggregate_transaction.virtual_transaction == virtual_transaction_to_void
    assert aggregate_transaction.type == "inbound"
