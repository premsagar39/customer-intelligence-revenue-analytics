# Data dictionary

SQL types, nullable attributes, primary keys and relationships are defined in `sql/schema.sql`. All pipeline output columns are specified in `src/schema.json`.

## customers

| Field | MySQL type |
|---|---|
| CustomerID | VARCHAR(32) NOT NULL PRIMARY KEY |
| Segment | VARCHAR(64) |
| Recency | INT |
| Frequency | INT |
| Monetary | DECIMAL(20,6) |
| RScore | INT |
| FScore | INT |
| MScore | INT |
| SnapshotDate | DATE |

## products

| Field | MySQL type |
|---|---|
| StockCode | VARCHAR(64) NOT NULL PRIMARY KEY |
| Description | VARCHAR(500) |

## dates

| Field | MySQL type |
|---|---|
| DateKey | DATE NOT NULL PRIMARY KEY |
| Year | INT |
| Month | VARCHAR(7) |
| MonthNumber | INT |

## transactions

| Field | MySQL type |
|---|---|
| LineID | BIGINT NOT NULL PRIMARY KEY |
| InvoiceNo | VARCHAR(64) NOT NULL |
| StockCode | VARCHAR(64) NOT NULL |
| CustomerID | VARCHAR(32) NOT NULL |
| DateKey | DATE NOT NULL |
| InvoiceDate | DATETIME NOT NULL |
| Country | VARCHAR(100) |
| Quantity | BIGINT |
| UnitPrice | DECIMAL(20,6) |
| LineType | VARCHAR(10) |
| LineRevenue | DECIMAL(20,6) |
| SalesRevenue | DECIMAL(20,6) |
| ReturnValue | DECIMAL(20,6) |
