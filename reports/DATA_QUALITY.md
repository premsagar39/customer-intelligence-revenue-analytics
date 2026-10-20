# Data quality decisions

Source rows: 1,067,371. Exact duplicates removed: 34,335. Invalid rows excluded: 6,020. Accepted lines: 1,027,016. These reconcile exactly.

Exact duplicates across all original eight columns are treated as repeated records; the source has no line identifier, so this is an explicit assumption that can remove legitimate identical lines. Invalid prices, zero quantities, missing keys/dates and one positive-quantity credit note are excluded. The rejection review file is capped at 5,000 examples; metrics cover all exclusions.

Negative quantity is a return/credit, including invoices without C. Positive C invoices are not silently negated. Return value is not matched to the originating sale; period return/gross is a value ratio, not a customer return probability.

229,201 accepted lines without customer identity remain in revenue. They are excluded from RFM and cohort metrics. Customer dimension includes return-only customers and an UNKNOWN member, but only 5,878 positive purchasing customers are RFM-scored. Frequency counts distinct sale invoices.

Source product codes are case-sensitive. MySQL uses a binary collation; Power Query creates numeric product keys before the tabular model's case-insensitive comparisons. Product descriptions use the latest observed nonmissing description; this is a historical snapshot, not an SCD dimension.

The 4,931 retained stock codes include postage, manual charges and other non-merchandise codes. This is a count of recorded stock codes, not a verified count of physical products. Inspect descriptions before using the product ranking for merchandising decisions.

RFM scores preserve ties and may produce uneven groups. Full-period RFM snapshot is 10 December 2011 and does not recalculate with report time slicers. Cohorts begin at first observed purchase, not proven acquisition. Missing observed cohort cells become zero; unobserved future cells remain absent. December 2011 ends on the ninth and is flagged partial.
