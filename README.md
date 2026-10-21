# Customer Analytics

A customer and revenue study of UCI Online Retail II, covering December 2009 to December 2011. It follows the transactions from data-quality checks through SQL analysis, customer segmentation and a four-page Power BI report.

![Analysis overview](reports/figures/portfolio_overview.png)

**Tools:** Python, pandas, NumPy, MySQL 8, SQLAlchemy, Power Query, Power BI and DAX. The project contains 21 executed MySQL business queries and 26 report measures. 

## Results to review

- **GBP 19.01m net revenue** after GBP 1.46m in returns and credits; Python and MySQL reconcile the same transaction totals.
- **63.93% of identified gross purchase spend** comes from the highest-spend customer decile.
- **15.15% of gross revenue** comes from anonymous purchases. Those transactions stay in revenue totals but cannot support customer-level RFM or cohort analysis.

## Analysis question

Which customer and product groups deserve retention and returns review, and how much confidence should we place in incomplete customer identity and partial-month trends?

## Explore the deliverables

- [Business findings](reports/BUSINESS_FINDINGS.md)
- [Interactive offline dashboard](reports/Interactive_Dashboard.html) — download and open in a browser; GitHub does not execute HTML.
- [Native Power BI project](powerbi/Customer_Intelligence.pbip) — download the repository and open in Power BI Desktop.
- [DAX definitions and scope](powerbi/MEASURE_DEFINITIONS.md)
- [21 MySQL questions and queries](sql/analysis_queries.sql)
- [Executed notebook](notebooks/01_analysis.ipynb)
- [Data quality decisions](reports/DATA_QUALITY.md), [dictionary](reports/DATA_DICTIONARY.md) and [MySQL reconciliation](reports/mysql_validation.json)

## Reproduce

Use Python 3.11+ and MySQL 8.0+. Install `requirements.txt` in a virtual environment. Keep source data outside Git.

```text
pip install -r requirements.txt
python src/pipeline.py --source "PATH_TO_SOURCE_FILE"
python src/comparison_analysis.py
python -m pytest tests -q
```

Create an empty local MySQL database, set `DATABASE_URL` using `.env.example` as a reference (the loader reads the environment, not the file automatically), enable LOCAL INFILE on your local server and run `python src/database.py`. The loader refuses nonempty tables and checks bulk-load warnings. It creates relational tables, constraints, views and query result CSVs. Never point this loader at a production database.

Open `powerbi/Customer_Intelligence.pbip`, set the DataRoot parameter to the local `data/` folder with a trailing slash and Refresh. See [report instructions](powerbi/OPEN_REPORT.md). Full processed data is generated locally, not committed. The native model is CSV-backed; MySQL independently validates the same transformed facts.

## Model and quality

Transaction fact → Customers, Products and Dates through one-way relationships. Numeric product surrogates preserve case-sensitive source codes. Cohorts form a separate aggregate table with its own cohort fields. Static RFM measures are explicitly labeled.

Python and MySQL totals reconcile independently. Unit tests cover analytical failure cases, including duplicate handling, signed returns, anonymous purchases, invoice frequency, tied scores and censored cohort grids. Report visuals and refresh status are documented separately; query execution does not prove every business interpretation.

## Source and limitations

[UCI Online Retail II](https://archive.ics.uci.edu/dataset/502/online+retail+ii), Daqing Chen, DOI 10.24432/C5CG6D, CC BY 4.0. Currency: GBP.

Customer anonymity limits RFM coverage. First observed purchase is not confirmed acquisition. Final December is partial. Exact duplicate exclusion and static RFM are documented assumptions.

Code and original documentation use the MIT license. Source datasets retain their own rights. Review the [publication checklist](reports/PUBLICATION_CHECKLIST.md) before sharing. Prepared by Singara Prem Sagar as a portfolio study.

## Comparison view

![Comparison overview](reports/figures/comparison_review.png)

[Open the comparison dashboard](reports/Comparison_Dashboard.html) after downloading the repository; these comparison charts require an internet connection for Plotly.

Customer segment comparison adds a focused review page with two contextual measures, a comparison table, chart tooltips and a project-specific theme. Full-period RFM snapshot at 10 Dec 2011. Index 1.00 matches selected segments; anonymous and return-only records are excluded. SQL Q21 provides the related aggregate analysis. See [enhancement checks](reports/COMPARISON_VALIDATION.md).

Current report: **4 pages, 26 DAX measures and 21 SQL analyses**.

[Report notes](powerbi/REPORT_NOTES.md) contain the date, scope and interpretation details behind the visuals.

## Dashboard controls

The redesigned report adds page navigation, collapsible synchronized filters, metric and ranking views, a contextual tooltip page and a drillthrough detail page. Light and dark themes are included. Display bookmarks preserve filter selections; existing SQL, DAX and imported data are retained. See the [control guide](docs/dashboard-controls.md) and [Power BI source](powerbi/Customer_Intelligence.Report).
