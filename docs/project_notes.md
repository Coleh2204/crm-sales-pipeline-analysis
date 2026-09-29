# Project Notes

## Objective
Analyze a public CRM sales-opportunities dataset and turn raw relational data into an auditable, management-ready sales performance report.

## Workflow
1. Preserve raw source data.
2. Standardize known source inconsistencies in the derived layer only.
3. Join opportunity records to account, product, and sales-team lookup data.
4. Create analysis fields for deal stage, sales cycle, close period, and price variance.
5. Validate row counts, unique opportunity IDs, and won-revenue reconciliation.
6. Analyze overall performance, products, teams, sales reps, sectors, accounts, and monthly trends.
7. Present results in an Excel dashboard and portfolio report.

## Validation checks
The preprocessing script asserts that:
- row count remains unchanged after enrichment;
- opportunity IDs remain unique;
- won revenue in the processed data exactly reconciles to the source pipeline.

## Data source
Maven Analytics — CRM Sales Opportunities public practice dataset.

Source page: https://mavenanalytics.io/data-playground/crm-sales-opportunities
