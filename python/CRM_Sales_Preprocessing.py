"""
CRM Sales Opportunities preprocessing workflow.

Inputs:
- accounts.csv
- products.csv
- sales_pipeline.csv
- sales_teams.csv

Outputs:
- master_opportunities.csv

This script preserves raw source files, standardizes known source inconsistencies
only in derived data, enriches opportunities with lookup fields, creates calculated
analysis fields, and reconciles source totals after processing.
"""

import csv
from datetime import datetime
from pathlib import Path

BASE = Path(".")

def read_csv(name):
    with open(BASE / name, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))

accounts = read_csv("accounts.csv")
products = read_csv("products.csv")
pipeline = read_csv("sales_pipeline.csv")
teams = read_csv("sales_teams.csv")

account_map = {r["account"]: r for r in accounts}
product_map = {r["product"]: r for r in products}
team_map = {r["sales_agent"]: r for r in teams}

def parse_date(value):
    return datetime.strptime(value, "%Y-%m-%d").date() if value else None

master = []

for row in pipeline:
    product = "GTX Pro" if row["product"] == "GTXPro" else row["product"]

    product_record = product_map.get(product, {})
    account_record = account_map.get(row["account"], {}) if row["account"] else {}
    team_record = team_map.get(row["sales_agent"], {})

    sector_raw = account_record.get("sector", "")
    sector = "technology" if sector_raw == "technolgy" else sector_raw

    engage_date = parse_date(row["engage_date"])
    close_date = parse_date(row["close_date"])
    close_value = float(row["close_value"]) if row["close_value"] else None
    list_price = (
        float(product_record["sales_price"])
        if product_record.get("sales_price")
        else None
    )

    stage = row["deal_stage"]
    sales_cycle_days = (
        (close_date - engage_date).days
        if engage_date and close_date
        else None
    )

    price_variance = (
        close_value - list_price
        if stage == "Won"
        and close_value is not None
        and list_price is not None
        else None
    )

    master.append({
        "opportunity_id": row["opportunity_id"],
        "sales_agent": row["sales_agent"],
        "manager": team_record.get("manager", ""),
        "regional_office": team_record.get("regional_office", ""),
        "product_raw": row["product"],
        "product": product,
        "product_series": product_record.get("series", ""),
        "list_price": list_price,
        "account": row["account"],
        "sector_raw": sector_raw,
        "sector": sector,
        "account_revenue": (
            float(account_record["revenue"])
            if account_record.get("revenue")
            else None
        ),
        "employees": (
            int(account_record["employees"])
            if account_record.get("employees")
            else None
        ),
        "office_location": account_record.get("office_location", ""),
        "deal_stage": stage,
        "engage_date": engage_date,
        "close_date": close_date,
        "close_value": close_value,
        "sales_cycle_days": sales_cycle_days,
        "won_flag": int(stage == "Won"),
        "lost_flag": int(stage == "Lost"),
        "open_flag": int(stage in {"Prospecting", "Engaging"}),
        "close_month": close_date.strftime("%Y-%m") if close_date else "",
        "close_quarter": (
            f"{close_date.year}-Q{((close_date.month - 1) // 3) + 1}"
            if close_date else ""
        ),
        "close_year": close_date.year if close_date else None,
        "price_variance": price_variance,
        "price_variance_pct": (
            price_variance / list_price
            if price_variance is not None and list_price
            else None
        ),
    })

# Reconciliation checks
assert len(master) == len(pipeline)
assert len({r["opportunity_id"] for r in master}) == len(master)

source_won_revenue = sum(
    float(r["close_value"])
    for r in pipeline
    if r["deal_stage"] == "Won" and r["close_value"]
)
master_won_revenue = sum(
    r["close_value"]
    for r in master
    if r["deal_stage"] == "Won"
)

assert source_won_revenue == master_won_revenue

headers = list(master[0].keys())
with open("master_opportunities.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=headers)
    writer.writeheader()
    writer.writerows(master)

print(f"Created master_opportunities.csv with {len(master):,} rows")
print(f"Won revenue reconciled: ${master_won_revenue:,.0f}")
