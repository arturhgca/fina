import pendulum

# set environment up
brl = Currency.new("BRL", decimals=2).budgets.add("Main BRL")
jpy = Currency.new("JPY", decimals=0).budgets.add("Main JPY")

# create accounts
checking_account = brl.balances.add("Checking Account", starting_value=0)
wise_accounts = {
    "brl": brl.balances.add("Wise (BRL)", starting_value=10000),
    "jpy": jpy.balances.add("Wise (JPY)"),
}

# add money from an external source
employer = brl.sources.new("Employer")
employer.pay(
    # category can be empty, in which case money goes to the unallocated pool
    value=100000,
    to=checking_account,
    when=pendulum.datetime(2022, 1, 31),
    description="Salary",
)

# allocate money from the unallocated pool
rent = brl.categories.add("Rent").allocate(
    value=50000,
    when=pendulum.datetime(2022, 2, 1),
)
fun_money = brl.categories.add("Fun Money").allocate(
    value=60000,
    when=pendulum.datetime(2022, 2, 1),
)
# Category.deallocate should also exist!

# convert money between currencies
figures = jpy.categories.add("Figures")
checking_account.transfer(
    value=50000,
    to=wise_accounts["brl"],
    when=pendulum.datetime(2022, 2, 1),
)
wise_accounts["brl"].convert(
    # accepts (convert, into), (convert, rate), or (into, rate)
    convert=60000,
    into=13000,
    to=wise_accounts["jpy"],
    when=pendulum.datetime(2022, 2, 1),
    deducing_from_category=fun_money,
    adding_to_category=figures,
)

# spend money
landlord = brl.sinks.add("Landlord")
checking_account.pay(
    value=40000,
    payee=landlord,
    when=pendulum.datetime(2022, 2, 2),
    category=rent,
)

amiami = jpy.sinks.new("AmiAmi")
wise_accounts["jpy"].pay(
    value=13000,
    payee=amiami,
    when=pendulum.datetime(2022, 2, 2),
    category=figures,
)
