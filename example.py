import datetime

from core import Currency, Balance, AggregateTransaction, Transaction

currency_brl = Currency.create(code="BRL", decimals=2)
employer = Balance.create_real_void(name="Employer", currency=currency_brl)
checking_account = Balance.create_real(
    name="Checking account", currency=currency_brl, value=0
)
# TODO:
#  checking = 0

virtual_dummy = Balance.create_virtual_void(name="_dummy_brl", currency=currency_brl)
to_budget = Balance.create_virtual(
    name="To budget (BRL)", currency=currency_brl, value=0
)
AggregateTransaction.create_inbound(
    real_transaction=Transaction.create_from_balances(
        occurred=datetime.datetime.now(),
        source_balance=employer,
        target_balance=checking_account,
        source_value=100000,
    ),
    virtual_transaction=Transaction.create_from_balances(
        occurred=datetime.datetime.now(),
        source_balance=virtual_dummy,
        target_balance=to_budget,
        source_value=100000,
    ),
)
# TODO:
#  checking = 1,000.00 BRL
#  to budget = 1,000.00 BRL

rent_budget = Balance.create_virtual(name="Rent", currency=currency_brl, value=0)
Transaction.create_from_balances(
    occurred=datetime.datetime.now(),
    source_balance=to_budget,
    target_balance=rent_budget,
    source_value=50000,
)
# TODO:
#  checking = 1,000.00 BRL
#  to budget = 500.00 BRL
#  rent = 500.00 BRL

currency_jpy = Currency.create(code="JPY", decimals=0)
to_budget_jpy = Balance.create_virtual(
    name="To budget (JPY)", currency=currency_jpy, value=0
)
figures_budget = Balance.create_virtual(
    name="Anime figures", currency=currency_jpy, value=0
)
jpy_wise_account = Balance.create_real(
    name="Wise Borderless Account (JPY)", currency=currency_jpy, value=0
)
Transaction.create_from_balances(
    occurred=datetime.datetime.now(),
    source_balance=checking_account,
    target_balance=jpy_wise_account,
    source_value=50000,
    target_value=10000,
)
Transaction.create_from_balances(
    occurred=datetime.datetime.now(),
    source_balance=to_budget,
    target_balance=to_budget_jpy,
    source_value=50000,
    target_value=10000,
)
Transaction.create_from_balances(
    occurred=datetime.datetime.now(),
    source_balance=to_budget_jpy,
    target_balance=figures_budget,
    source_value=5000,
)
# TODO:
#  checking = 500.00 BRL
#  to budget = 0.00 BRL
#  rent = 500.00 BRL
#  to budget JPY = 5,000 JPY
#  anime figures = 5,000 JPY

amiami = Balance.create_real_void(name="AmiAmi", currency=currency_jpy)
virtual_dummy_jpy = Balance.create_virtual_void(
    name="_dummy_jpy", currency=currency_jpy
)
AggregateTransaction.create_outbound(
    real_transaction=Transaction.create_from_balances(
        occurred=datetime.datetime.now(),
        source_balance=jpy_wise_account,
        target_balance=amiami,
        source_value=5000,
    ),
    virtual_transaction=Transaction.create_from_balances(
        occurred=datetime.datetime.now(),
        source_balance=figures_budget,
        target_balance=virtual_dummy_jpy,
        source_value=5000,
    ),
)
# TODO:
#  checking = 500.00 BRL
#  to budget = 0.00 BRL
#  rent = 500.00 BRL
#  to budget JPY = 5,000 JPY
#  anime figures = 0 JPY
