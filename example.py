import datetime

from core import Currency

# set environment up
brl_currency = Currency.new(code="BRL", decimals=2)
jpy_currency = Currency.new(code="JPY", decimals=0)
brl = brl_currency.budgets.add(name="Main BRL")
jpy = jpy_currency.budgets.add(name="Main JPY")

# create accounts
checking_account = brl.balances.add(name="Checking Account", starting_value=0)
wise_accounts = {
    "brl": brl.balances.add(name="Wise (BRL)", starting_value=10000),
    "jpy": jpy.balances.add(name="Wise (JPY)"),
}

# add money from an external source
employer = brl.sources.add(name="Employer")
employer.pay(
    # category can be empty, in which case money goes to the unallocated pool
    value=100000,
    to=checking_account,
    when=datetime.datetime(2022, 1, 31),
    description="Salary",
)

# allocate money from the unallocated pool
rent = brl.categories.add(name="Rent").allocate(
    value=50000,
    when=datetime.datetime(2022, 2, 1),
)
fun_money = brl.categories.add(name="Fun Money").allocate(
    value=60000,
    when=datetime.datetime(2022, 2, 1),
)
# Category.deallocate should also exist!

# convert money between currencies
figures = jpy.categories.add(name="Figures")
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
landlord = brl.sinks.add(name="Landlord")
checking_account.pay(
    value=40000,
    to=landlord,
    when=datetime.datetime(2022, 2, 2),
    category=rent,
)

amiami = jpy.sinks.add(name="AmiAmi")
wise_accounts["jpy"].pay(
    value=13000,
    to=amiami,
    when=datetime.datetime(2022, 2, 2),
    category=figures,
)
