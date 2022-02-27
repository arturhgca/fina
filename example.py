import datetime

from core import Currency, Budget, Balance, Source, Category, Sink

# set environment up
brl_currency = Currency.new(code="BRL", decimals=2)
jpy_currency = Currency.new(code="JPY", decimals=0)
brl_budget = Budget.new(currency=brl_currency, name="Main BRL")
jpy_budget = Budget.new(currency=jpy_currency, name="Main JPY")

# create accounts
checking_account = Balance.new(
    budget=brl_budget, name="Checking Account", starting_value=0
)
wise_accounts = {
    "brl": Balance.new(budget=brl_budget, name="Wise (BRL)", starting_value=10000),
    "jpy": Balance.new(budget=jpy_budget, name="Wise (JPY)"),
}

# add money from an external source
employer = Source.new(budget=brl_budget, name="Employer")
employer.pay(
    # category can be empty, in which case money goes to the unallocated pool
    value=100000,
    to=checking_account,
    when=datetime.datetime(2022, 1, 31),
    description="Salary",
)

# allocate money from the unallocated pool
rent = Category.new(budget=brl_budget, name="Rent").allocate(
    value=50000,
    when=datetime.datetime(2022, 2, 1),
)
fun_money = Category.new(budget=brl_budget, name="Fun Money").allocate(
    value=60000,
    when=datetime.datetime(2022, 2, 1),
)
# Category.deallocate should also exist!

# convert money between currencies
figures = Category.new(budget=jpy_budget, name="Figures")
checking_account.transfer(
    value=50000,
    to=wise_accounts["brl"],
    when=datetime.datetime(2022, 2, 1),
)
wise_accounts["brl"].convert(
    convert=60000,
    into=13000,
    to=wise_accounts["jpy"],
    when=datetime.datetime(2022, 2, 1),
    deducing_from_category=fun_money,
    adding_to_category=figures,
)

# spend money
landlord = Sink.new(budget=brl_budget, name="Landlord")
checking_account.pay(
    value=40000,
    to=landlord,
    when=datetime.datetime(2022, 2, 2),
    category=rent,
)

amiami = Sink.new(budget=jpy_budget, name="AmiAmi")
wise_accounts["jpy"].pay(
    value=13000,
    to=amiami,
    when=datetime.datetime(2022, 2, 2),
    category=figures,
)
