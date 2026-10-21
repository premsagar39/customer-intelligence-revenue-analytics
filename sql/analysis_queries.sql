-- Q01: Portfolio revenue controls
SELECT COUNT(*) AcceptedLines,SUM(SalesRevenue) GrossRevenue,SUM(ReturnValue) ReturnsValue,SUM(LineRevenue) NetRevenue,COUNT(DISTINCT CASE WHEN LineType='Sale' THEN InvoiceNo END) SaleOrders,SUM(SalesRevenue)/COUNT(DISTINCT CASE WHEN LineType='Sale' THEN InvoiceNo END) AOV FROM transactions;



-- Q02: Monthly revenue and observed month growth
WITH m AS (SELECT d.`Month`,SUM(t.LineRevenue) NetRevenue,SUM(t.SalesRevenue) GrossRevenue FROM transactions t JOIN dates d USING(DateKey) GROUP BY d.`Month`) SELECT *,NetRevenue/LAG(NetRevenue) OVER(ORDER BY `Month`)-1 MoMNetGrowth FROM m ORDER BY `Month`;



-- Q03: Country contribution
SELECT Country,SUM(LineRevenue) NetRevenue,SUM(SalesRevenue) GrossRevenue,SUM(ReturnValue) ReturnsValue,COUNT(DISTINCT CASE WHEN LineType='Sale' THEN InvoiceNo END) Orders FROM transactions GROUP BY Country ORDER BY NetRevenue DESC;



-- Q04: Product performance ranking
WITH p AS (SELECT StockCode,SUM(LineRevenue) NetRevenue FROM transactions GROUP BY StockCode) SELECT p.*,d.Description,DENSE_RANK() OVER(ORDER BY NetRevenue DESC) RevenueRank FROM p JOIN products d USING(StockCode) ORDER BY RevenueRank LIMIT 30;



-- Q05: Customer spend and net credits
SELECT c.CustomerID,c.Segment,c.Frequency,c.Recency,SUM(t.SalesRevenue) GrossRevenue,SUM(t.LineRevenue) NetRevenue FROM customers c JOIN transactions t USING(CustomerID) WHERE c.CustomerID<>'UNKNOWN' GROUP BY c.CustomerID,c.Segment,c.Frequency,c.Recency ORDER BY GrossRevenue DESC LIMIT 30;



-- Q06: Top customer decile concentration
WITH ranked AS (SELECT Monetary,NTILE(10) OVER(ORDER BY Monetary DESC,CustomerID) decile FROM customers WHERE CustomerID<>'UNKNOWN' AND Frequency IS NOT NULL) SELECT decile,COUNT(*) Customers,SUM(Monetary) GrossRevenue,SUM(Monetary)/SUM(SUM(Monetary)) OVER() RevenueShare FROM ranked GROUP BY decile ORDER BY decile;



-- Q07: RFM segments
SELECT Segment,COUNT(*) Customers,SUM(Monetary) GrossRevenue,AVG(Recency) AverageRecency,AVG(Frequency) AverageFrequency FROM customers WHERE CustomerID<>'UNKNOWN' AND Frequency IS NOT NULL GROUP BY Segment ORDER BY GrossRevenue DESC;



-- Q08: Repeat purchasing
SELECT COUNT(*) IdentifiedCustomers,SUM(Frequency>=2) RepeatCustomers,AVG(Frequency>=2) RepeatShare FROM customers WHERE CustomerID<>'UNKNOWN' AND Frequency IS NOT NULL;



-- Q09: Score distribution
SELECT RScore,FScore,MScore,COUNT(*) Customers,SUM(Monetary) GrossRevenue FROM customers WHERE CustomerID<>'UNKNOWN' AND Frequency IS NOT NULL GROUP BY RScore,FScore,MScore ORDER BY RScore DESC,FScore DESC,MScore DESC;

-- Q10: Complete observed cohort grid, including observed zero activity
WITH RECURSIVE active AS (SELECT DISTINCT CustomerID,DATE_FORMAT(OrderDate,'%Y-%m-01') MonthStart FROM identified_orders),
firsts AS (SELECT CustomerID,MIN(MonthStart) Cohort FROM active GROUP BY CustomerID),
sizes AS (SELECT Cohort,COUNT(*) CohortSize FROM firsts GROUP BY Cohort),
ages AS (SELECT 0 MonthIndex UNION ALL SELECT MonthIndex+1 FROM ages WHERE MonthIndex<60),
counts AS (SELECT f.Cohort,TIMESTAMPDIFF(MONTH,f.Cohort,a.MonthStart) MonthIndex,COUNT(DISTINCT a.CustomerID) ActiveCustomers FROM active a JOIN firsts f USING(CustomerID) GROUP BY f.Cohort,MonthIndex)
SELECT s.Cohort,a.MonthIndex,s.CohortSize,COALESCE(c.ActiveCustomers,0) ActiveCustomers,COALESCE(c.ActiveCustomers,0)/s.CohortSize Retention
FROM sizes s CROSS JOIN ages a LEFT JOIN counts c ON c.Cohort=s.Cohort AND c.MonthIndex=a.MonthIndex
WHERE a.MonthIndex<=TIMESTAMPDIFF(MONTH,s.Cohort,(SELECT MAX(MonthStart) FROM active)) ORDER BY s.Cohort,a.MonthIndex;



-- Q11: Time to second observed purchase
WITH x AS (SELECT CustomerID,OrderDate,ROW_NUMBER() OVER(PARTITION BY CustomerID ORDER BY OrderDate,InvoiceNo) rn,LEAD(OrderDate) OVER(PARTITION BY CustomerID ORDER BY OrderDate,InvoiceNo) NextOrder FROM identified_orders) SELECT COUNT(*) FirstObservedCustomers,SUM(NextOrder IS NOT NULL) ReturnedCustomers,AVG(DATEDIFF(NextOrder,OrderDate)) MeanDaysToSecondOrder FROM x WHERE rn=1;



-- Q12: Observed interpurchase gaps
WITH x AS (SELECT CustomerID,OrderDate,LAG(OrderDate) OVER(PARTITION BY CustomerID ORDER BY OrderDate,InvoiceNo) PreviousOrder FROM identified_orders) SELECT CASE WHEN DATEDIFF(OrderDate,PreviousOrder)<=30 THEN '0-30 days' WHEN DATEDIFF(OrderDate,PreviousOrder)<=90 THEN '31-90 days' ELSE '91+ days' END GapBand,COUNT(*) RepeatOrders FROM x WHERE PreviousOrder IS NOT NULL GROUP BY GapBand;



-- Q13: Return value by country
SELECT Country,SUM(ReturnValue) ReturnValue,SUM(SalesRevenue) GrossRevenue,SUM(ReturnValue)/NULLIF(SUM(SalesRevenue),0) ReturnToGrossValue FROM transactions GROUP BY Country ORDER BY ReturnValue DESC;



-- Q14: Return-heavy products with at least GBP1000 gross sales
SELECT StockCode,SUM(SalesRevenue) GrossRevenue,SUM(ReturnValue) ReturnValue,SUM(ReturnValue)/NULLIF(SUM(SalesRevenue),0) ReturnValueRatio FROM transactions GROUP BY StockCode HAVING SUM(SalesRevenue)>=1000 ORDER BY ReturnValueRatio DESC LIMIT 25;



-- Q15: Anonymous revenue coverage
SELECT DATE_FORMAT(InvoiceDate,'%Y-%m') Month,SUM(CASE WHEN CustomerID='UNKNOWN' THEN SalesRevenue ELSE 0 END)/SUM(SalesRevenue) AnonymousRevenueShare FROM transactions GROUP BY Month ORDER BY Month;



-- Q16: Basket composition
WITH baskets AS (SELECT InvoiceNo,COUNT(DISTINCT StockCode) Products,SUM(Quantity) Units,SUM(SalesRevenue) GrossRevenue FROM positive_sales GROUP BY InvoiceNo) SELECT AVG(Products) MeanProducts,AVG(Units) MeanUnits,AVG(GrossRevenue) AverageOrderValue FROM baskets;



-- Q17: Weekday and hour order profile
SELECT WEEKDAY(InvoiceDate) Weekday,HOUR(InvoiceDate) Hour,COUNT(DISTINCT InvoiceNo) Orders,SUM(SalesRevenue) Revenue FROM positive_sales GROUP BY Weekday,Hour ORDER BY Weekday,Hour;



-- Q18: Newly observed versus returning customer monthly orders
WITH firsts AS (SELECT CustomerID,MIN(OrderDate) FirstDate FROM identified_orders GROUP BY CustomerID) SELECT DATE_FORMAT(o.OrderDate,'%Y-%m') Month,CASE WHEN DATE_FORMAT(o.OrderDate,'%Y-%m')=DATE_FORMAT(f.FirstDate,'%Y-%m') THEN 'Newly observed' ELSE 'Returning' END CustomerType,COUNT(*) Orders,SUM(o.GrossRevenue) GrossRevenue FROM identified_orders o JOIN firsts f USING(CustomerID) GROUP BY Month,CustomerType ORDER BY Month;



-- Q19: At risk customers for manual campaign review
SELECT CustomerID,Recency,Frequency,Monetary FROM customers WHERE Segment='At risk' ORDER BY Monetary DESC LIMIT 50;



-- Q20: Customers recorded in multiple countries
SELECT CustomerID,COUNT(DISTINCT Country) Countries,COUNT(DISTINCT CASE WHEN LineType='Sale' THEN InvoiceNo END) Orders,SUM(LineRevenue) NetRevenue FROM transactions WHERE CustomerID<>'UNKNOWN' GROUP BY CustomerID HAVING COUNT(DISTINCT Country)>1 ORDER BY NetRevenue DESC;

-- Q21: Compare full-period RFM segments against a customer-weighted benchmark
WITH segments AS (
 SELECT Segment,COUNT(*) Customers,SUM(Monetary) GrossSpend,AVG(Monetary) SpendPerCustomer
 FROM customers WHERE Frequency IS NOT NULL GROUP BY Segment
)
SELECT *,SpendPerCustomer/NULLIF(SUM(GrossSpend) OVER()/SUM(Customers) OVER(),0) SpendIndex,
 DENSE_RANK() OVER(ORDER BY SpendPerCustomer DESC) SpendRank
FROM segments ORDER BY SpendPerCustomer DESC,Segment;
