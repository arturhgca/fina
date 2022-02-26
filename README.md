# fina-core
Multicurrency envelope system implementation.

## The philosophy of fina

This project aims to be a highly extensible financial life management platform.
Therefore, it is to be modular, with the current code base serving as its
foundation.

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

fina-core operates on two levels: **real** and **virtual**. The real level
manages the actual money, while the virtual manages budgeting.

### Balances

All entities in a budget are represented by balances:

* A **real balance** represents a *place* where money is (e.g., a bank 
account or a physical wallet).
  * A real balance can optionally be a **void balance**, which
represents an *external entity* that does not belong in the budget but
interacts with it (like an employee or a store).
* A **virtual balance** represents a *category* to which money is allocated
(i.e., the actual budgeting: groceries, rent, emergency fund, etc.).

#### Core attributes

* Type
* Display name
* Description (optional)
* Currency
* Value (null for void balances)

### Core transactions

Any time a balance is altered, that is done by a transaction. These can be
single operations or part of a set.

All transactions boil down to:

* **Real transactions**, which move money from one real balance to another.
* **Virtual transactions**, which move money from one virtual balance to another.

#### Core attributes

* Type (inferred from the source balance)
* Description (optional)
* Occurrence timestamp
* Source balance
* Target balance (must be of the same type as the source balance)
* Source value
* Target value (optional)
* VET (calculated if both values are specified)

### Aggregate transactions

These contain one real transaction *and* one virtual transaction:
* An **inbound transaction** moves money from a void balance to a real balance
and maps it to a virtual balance.
* An **outbound transaction** moves money from both a real balance and a
virtual balance to a void balance.

#### Core attributes

* Reference to real transaction
* Reference to virtual transaction

## API

The API is a CRUD for the core entities. It also provides an abstracted CRUD
for the aggregate transactions.

## Data Store

The core uses sqlite3 for storing all data. There are three tables:

* Balances
* Core transactions
* Aggregate transactions

On top of the core attributes previously listed, all entities have:

* Primary key (UUID)
* Creation timestamp (Unix epoch time, seconds)
* Last updated timestamp (Unix epoch time, seconds)

Furthermore, all deletions are soft.