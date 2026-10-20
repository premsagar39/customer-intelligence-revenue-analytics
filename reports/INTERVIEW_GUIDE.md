# Interview preparation

**What problem did you investigate?** Explain the decision, source scope, dataset grain and one verified finding. Use README numbers; do not describe a simulated or proposed benefit as realized.

**How do you reproduce this?** Run the pipeline against the original source, inspect quality metrics, load an empty MySQL schema, execute the business queries and refresh the parameterized Power BI model.

**What could make the answer wrong?** Discuss missing identity and partial observation for retail; outcome maturity and accepted-only selection for loans; future leakage and missing calendar days for demand.

**Why both SQL and Python?** Python handles source cleaning and analytics; SQL provides relational constraints and independently computed KPI checks. Matching totals are evidence, not proof every metric is correct.

**How is the dashboard interactive?** Explain slicer filter context, measures versus columns, one-way relationships, fixed snapshots and why distinct order counts differ from line counts.

**What would you do next with a business partner?** Validate the decision, ownership, data refresh requirements and intervention test before claiming ROI. Ask which metric and trade-off matter.

**Which work is yours?** Be accurate about tools and assistance. Demonstrate the cleaning rule, query, DAX denominator and test yourself; do not misrepresent authorship or workplace experience.