-- MySQL 8.0+. Run against an empty project database, never a production schema.

CREATE TABLE IF NOT EXISTS `customers` (
  `CustomerID` VARCHAR(32) NOT NULL PRIMARY KEY,
  `Segment` VARCHAR(64),
  `Recency` INT,
  `Frequency` INT,
  `Monetary` DECIMAL(20,6),
  `RScore` INT,
  `FScore` INT,
  `MScore` INT,
  `SnapshotDate` DATE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_bin;

CREATE TABLE IF NOT EXISTS `products` (
  `StockCode` VARCHAR(64) NOT NULL PRIMARY KEY,
  `Description` VARCHAR(500)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_bin;

CREATE TABLE IF NOT EXISTS `dates` (
  `DateKey` DATE NOT NULL PRIMARY KEY,
  `Year` INT,
  `Month` VARCHAR(7),
  `MonthNumber` INT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_bin;

CREATE TABLE IF NOT EXISTS `transactions` (
  `LineID` BIGINT NOT NULL PRIMARY KEY,
  `InvoiceNo` VARCHAR(64) NOT NULL,
  `StockCode` VARCHAR(64) NOT NULL,
  `CustomerID` VARCHAR(32) NOT NULL,
  `DateKey` DATE NOT NULL,
  `InvoiceDate` DATETIME NOT NULL,
  `Country` VARCHAR(100),
  `Quantity` BIGINT,
  `UnitPrice` DECIMAL(20,6),
  `LineType` VARCHAR(10),
  `LineRevenue` DECIMAL(20,6),
  `SalesRevenue` DECIMAL(20,6),
  `ReturnValue` DECIMAL(20,6),
  FOREIGN KEY (`CustomerID`) REFERENCES customers(`CustomerID`),
  FOREIGN KEY (`StockCode`) REFERENCES products(`StockCode`),
  FOREIGN KEY (`DateKey`) REFERENCES dates(`DateKey`),
  INDEX ix_order (`InvoiceNo`),
  INDEX ix_market_date (`Country`,`DateKey`),
  INDEX ix_line_date (`LineType`,`DateKey`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_bin;

CREATE OR REPLACE VIEW positive_sales AS SELECT * FROM transactions WHERE LineType = 'Sale';

CREATE OR REPLACE VIEW identified_orders AS SELECT CustomerID, InvoiceNo, MIN(InvoiceDate) OrderDate, SUM(SalesRevenue) GrossRevenue FROM positive_sales WHERE CustomerID <> 'UNKNOWN' GROUP BY CustomerID,InvoiceNo;