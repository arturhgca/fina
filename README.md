# fina-core
Multicurrency envelope system implementation.

## The philosophy of fina

This project aims to be a highly extensible financial life management platform.
With modularity in mind, the current code base will serve as its foundation.

### What fina-core is

fina-core, as the kernel of the platform, aims to provide modules with access
to base functionality and entities that should suffice for most use cases.

It is a Python API with a CLI application for testing.

### Module ideas

* A web API (*fina-http*)
* A web application (*fina-ui*)
* An investment portfolio manager (*fina-invest*)
* A future budget manager (*fina-forward*)
* A tax manager (*fina-tax*)

## Data model

A **currency** is the top level entity of the platform. Within a currency,
**budgets** can be created. A budget contains **balances** and **categories**,
which are manipulated by **transactions**.

### Balances

A balance represents a *place* where money is (e.g., a bank account or a
physical wallet). It indicates how much money is available there.

There are special types of balances:
* **Sources** are valueless balances from which money can only be taken.
* **Sinks** are valueless balances to which money can only be added.

### Transactions

Transactions represent any act of moving money from one balance to another.
They usually aren't directly created - instead, balances expose the correct
interfaces for moving money out of them.

It is also possible to move money between budgets, even those of different
currencies.

A few examples:
* A source balance can **pay** values to a normal balance.
* A balance can **transfer** values to another balance.
* A balance can **convert** values to a balance of another currency.
* A balance can **pay** values to a sink balance.

### Categories

Categories are where the actual *budgeting* happens. They are essentially the
envelopes of the eponymous system, where money is *allocated* for spending.

Transactions usually *can* indicate a category, but each transaction type
defines whether that's required.

## Data Store

The core uses sqlite3 for storing all data. There are six _dimension_ tables:

* Currencies
* Budgets
* Sources
* Balances
* Sinks
* Categories

And five _fact_ tables:

* Allocations
* Incomes
* Transactions
* Exchange Transactions
* Expenses

Joining facts and dimensions allows for rewinding, snapshotting, flexible
reporting, data revisions, and more.

All entities have:

* Primary key (incremental)
* Creation timestamp (Unix epoch time, seconds)
* Last updated timestamp (Unix epoch time, seconds)

Furthermore, all deletions are soft.
