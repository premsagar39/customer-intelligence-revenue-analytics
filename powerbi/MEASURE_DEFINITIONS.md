# Measure definitions


RFM snapshot measures intentionally ignore date and market selections; the full-period segmentation does not change. Transaction measures are filter-aware. Cohort totals are weighted ratios, not mean percentages. Top decile is 588 highest-spend identified purchasers.

## Net Revenue

Format: `£#,0;−£#,0`

```dax
SUM(Transactions[LineRevenue])
```

## Gross Revenue

Format: `£#,0`

```dax
SUM(Transactions[SalesRevenue])
```

## Return Value

Format: `£#,0`

```dax
SUM(Transactions[ReturnValue])
```

## Sales Orders

Format: `#,0`

```dax
CALCULATE(DISTINCTCOUNT(Transactions[InvoiceNo]),Transactions[LineType]="Sale")
```

## Average Order Value

Format: `£#,0.00`

```dax
DIVIDE([Gross Revenue],[Sales Orders])
```

## Return to Gross

Format: `0.0%`

```dax
DIVIDE([Return Value],[Gross Revenue])
```

## Accepted Lines

Format: `#,0`

```dax
COUNTROWS(Transactions)
```

## Units Sold

Format: `#,0`

```dax
CALCULATE(SUM(Transactions[Quantity]),Transactions[LineType]="Sale")
```

## Purchasing Customers

Format: `#,0`

```dax
CALCULATE(DISTINCTCOUNT(Transactions[CustomerID]),Transactions[LineType]="Sale",Transactions[CustomerID]<>"UNKNOWN")
```

## Repeat Customers

Format: `#,0`

```dax
COUNTROWS(FILTER(VALUES(Transactions[CustomerID]),Transactions[CustomerID]<>"UNKNOWN" && CALCULATE([Sales Orders])>=2))
```

## Repeat Customer Share

Format: `0.0%`

```dax
DIVIDE([Repeat Customers],[Purchasing Customers])
```

## Anonymous Revenue Share

Format: `0.0%`

```dax
DIVIDE(CALCULATE([Gross Revenue],Transactions[CustomerID]="UNKNOWN"),[Gross Revenue])
```

## Active Products

Format: `#,0`

```dax
DISTINCTCOUNT(Transactions[ProductKey])
```

## Markets

Format: `#,0`

```dax
DISTINCTCOUNT(Transactions[Country])
```

## Net Revenue Previous Month

Format: `£#,0`

```dax
CALCULATE([Net Revenue],DATEADD(Dates[DateKey],-1,MONTH))
```

## Net Revenue MoM

Format: `0.0%`

```dax
DIVIDE([Net Revenue]-[Net Revenue Previous Month],[Net Revenue Previous Month])
```

## Net Revenue YTD

Format: `£#,0`

```dax
TOTALYTD([Net Revenue],Dates[DateKey])
```

## Customer Revenue Share

Format: `0.0%`

```dax
DIVIDE([Gross Revenue],CALCULATE([Gross Revenue],REMOVEFILTERS(Customers)))
```

## RFM Customers

Format: `#,0`

```dax
COUNTROWS(FILTER(Customers,NOT ISBLANK(Customers[Frequency])))
```

## RFM Gross Spend

Format: `£#,0`

```dax
SUM(Customers[Monetary])
```

## RFM Mean Recency

Format: `0.0`

```dax
AVERAGE(Customers[Recency])
```

## RFM Top Decile Spend Share

Format: `0.0%`

```dax
VAR C=FILTER(ALL(Customers),NOT ISBLANK(Customers[Monetary])) VAR N=ROUNDUP(COUNTROWS(C)*0.1,0) RETURN DIVIDE(SUMX(TOPN(N,C,Customers[Monetary],DESC,Customers[CustomerID],ASC),Customers[Monetary]),SUMX(C,Customers[Monetary]))
```

## Cohort Retention

Format: `0.0%`

```dax
DIVIDE(SUM(Cohorts[ActiveCustomers]),SUM(Cohorts[CohortSize]))
```

## Cohort Active Customers

Format: `#,0`

```dax
SUM(Cohorts[ActiveCustomers])
```
