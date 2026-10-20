# Open the native report

Open `Customer_Intelligence.pbip` in Power BI Desktop. This is an editable Power BI Project, not a renamed PBIX. In Transform data → Edit parameters, set DataRoot to your local project data folder with a trailing slash. Run the Python pipeline first, then Refresh. Save As PBIX if you prefer a portable cached report. Full processed data is intentionally excluded from Git.

The CSV model uses a local data parameter; no database password is embedded. Retail product surrogate keys preserve source SKU case before loading into the case-insensitive semantic engine.
