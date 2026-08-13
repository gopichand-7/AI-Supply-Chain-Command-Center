import os
import re
import pandas as pd
from google import genai
from dotenv import load_dotenv


# ============================================================
# ENVIRONMENT / GEMINI CLIENT
# ============================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("Gemini API Key not found.")

client = genai.Client(api_key=GEMINI_API_KEY)


# ============================================================
# HELPERS
# ============================================================

def _find_column(df, possible_names):
    """
    Return the first matching column from a list of possible names.
    Matching is case-insensitive.
    """
    if df is None or df.empty:
        return None

    normalized = {
        str(col).strip().lower(): col
        for col in df.columns
    }

    for name in possible_names:
        key = str(name).strip().lower()
        if key in normalized:
            return normalized[key]

    return None


def _safe_number(value, default=0.0):
    """Convert a value to a numeric value safely."""
    try:
        if pd.isna(value):
            return default
        return float(value)
    except (ValueError, TypeError):
        return default


def _clean_status(value):
    """Normalize stock-status text."""
    if pd.isna(value):
        return ""

    value = str(value).strip()

    value = value.replace("🟢", "").replace("🟡", "").replace("🔴", "")
    value = value.strip()

    return value.lower()


def _format_currency(value):
    return f"${_safe_number(value):,.2f}"


def _format_percent(value):
    return f"{_safe_number(value):.1f}%"


def _format_number(value, decimals=1):
    return f"{_safe_number(value):,.{decimals}f}"


# ============================================================
# VERIFIED INVENTORY FACTS
# ============================================================

def _build_inventory_facts(df):
    """
    Calculate all inventory facts in Python.

    IMPORTANT:
    Gemini receives these verified facts rather than being asked
    to calculate them from the complete dataframe.
    """

    if df is None or df.empty:
        return {
            "error": "Inventory dataset is empty."
        }

    value_col = _find_column(
        df,
        [
            "InventoryValueUSD",
            "Inventory_Value_USD",
            "Inventory Value USD",
        ],
    )

    status_col = _find_column(
        df,
        [
            "StockStatus",
            "Stock Status",
        ],
    )

    category_col = _find_column(
        df,
        [
            "Category",
        ],
    )

    warehouse_col = _find_column(
        df,
        [
            "Warehouse",
        ],
    )

    sku_col = _find_column(
        df,
        [
            "SKU",
            "Sku",
        ],
    )

    item_col = _find_column(
        df,
        [
            "ItemName",
            "Item Name",
        ],
    )

    supplier_col = _find_column(
        df,
        [
            "Supplier",
        ],
    )

    current_stock_col = _find_column(
        df,
        [
            "CurrentStock",
            "Current Stock",
        ],
    )

    safety_stock_col = _find_column(
        df,
        [
            "SafetyStock",
            "Safety Stock",
        ],
    )

    max_stock_col = _find_column(
        df,
        [
            "MaxStockLevel",
            "Max Stock Level",
        ],
    )

    avg_usage_col = _find_column(
        df,
        [
            "AvgDailyUsage",
            "AverageDailyUsage",
            "Average Daily Usage",
        ],
    )

    days_inventory_col = _find_column(
        df,
        [
            "DaysOfInventory",
            "Days of Inventory",
        ],
    )

    facts = {}

    # --------------------------------------------------------
    # Basic inventory totals
    # --------------------------------------------------------

    facts["total_skus"] = int(len(df))

    if value_col:
        facts["total_inventory_value"] = _safe_number(
            pd.to_numeric(df[value_col], errors="coerce").sum()
        )
    else:
        facts["total_inventory_value"] = 0.0

    # --------------------------------------------------------
    # Stock status
    # --------------------------------------------------------

    if status_col:
        statuses = df[status_col].apply(_clean_status)

        facts["healthy_items"] = int(
            (statuses == "healthy").sum()
        )

        facts["low_stock_items"] = int(
            (statuses == "low stock").sum()
        )

        facts["overstock_items"] = int(
            (statuses == "overstock").sum()
        )
    else:
        facts["healthy_items"] = 0
        facts["low_stock_items"] = 0
        facts["overstock_items"] = 0

    if facts["total_skus"] > 0:
        facts["healthy_percent"] = (
            facts["healthy_items"]
            / facts["total_skus"]
            * 100
        )
    else:
        facts["healthy_percent"] = 0.0

    # --------------------------------------------------------
    # Demand
    # --------------------------------------------------------

    if avg_usage_col:
        usage = pd.to_numeric(
            df[avg_usage_col],
            errors="coerce",
        ).fillna(0)

        facts["total_daily_demand"] = float(usage.sum())

        facts["average_daily_demand_per_sku"] = (
            float(usage.mean())
            if len(usage) > 0
            else 0.0
        )
    else:
        facts["total_daily_demand"] = 0.0
        facts["average_daily_demand_per_sku"] = 0.0

    # --------------------------------------------------------
    # Critical low-stock items
    # --------------------------------------------------------

    critical_items = []

    if (
        status_col
        and sku_col
        and item_col
        and current_stock_col
        and days_inventory_col
    ):
        temp = df.copy()

        temp["_status_clean"] = temp[status_col].apply(
            _clean_status
        )

        temp["_days_inventory"] = pd.to_numeric(
            temp[days_inventory_col],
            errors="coerce",
        ).fillna(999999)

        low = temp[
            temp["_status_clean"] == "low stock"
        ].sort_values(
            "_days_inventory",
            ascending=True,
        )

        for _, row in low.iterrows():

            critical_items.append(
                {
                    "sku": str(row[sku_col]),
                    "item": str(row[item_col]),
                    "current_stock": _safe_number(
                        row[current_stock_col]
                    ),
                    "days_inventory": _safe_number(
                        row[days_inventory_col]
                    ),
                }
            )

    facts["critical_low_stock_items"] = critical_items

    # --------------------------------------------------------
    # Overstock items
    # --------------------------------------------------------

    overstock_items = []

    if (
        status_col
        and sku_col
        and item_col
        and current_stock_col
        and max_stock_col
        and value_col
    ):
        temp = df.copy()

        temp["_status_clean"] = temp[status_col].apply(
            _clean_status
        )

        temp["_current_stock"] = pd.to_numeric(
            temp[current_stock_col],
            errors="coerce",
        ).fillna(0)

        temp["_max_stock"] = pd.to_numeric(
            temp[max_stock_col],
            errors="coerce",
        ).fillna(0)

        temp["_inventory_value"] = pd.to_numeric(
            temp[value_col],
            errors="coerce",
        ).fillna(0)

        temp["_excess_units"] = (
            temp["_current_stock"]
            - temp["_max_stock"]
        )

        over = temp[
            temp["_status_clean"] == "overstock"
        ].sort_values(
            "_inventory_value",
            ascending=False,
        )

        for _, row in over.iterrows():

            excess_units = max(
                0,
                _safe_number(row["_excess_units"]),
            )

            unit_cost = (
                _safe_number(row["_inventory_value"])
                / _safe_number(row["_current_stock"])
                if _safe_number(row["_current_stock"]) > 0
                else 0
            )

            excess_value = excess_units * unit_cost

            overstock_items.append(
                {
                    "sku": str(row[sku_col]),
                    "item": str(row[item_col]),
                    "current_stock": _safe_number(
                        row[current_stock_col]
                    ),
                    "max_stock": _safe_number(
                        row[max_stock_col]
                    ),
                    "excess_units": excess_units,
                    "excess_value": excess_value,
                }
            )

    facts["overstock_items"] = overstock_items

    # --------------------------------------------------------
    # Category summary
    # --------------------------------------------------------

    category_summary = []

    if category_col:

        grouped = df.groupby(category_col)

        for category, group in grouped:

            category_value = (
                pd.to_numeric(
                    group[value_col],
                    errors="coerce",
                ).fillna(0).sum()
                if value_col
                else 0
            )

            category_demand = (
                pd.to_numeric(
                    group[avg_usage_col],
                    errors="coerce",
                ).fillna(0).sum()
                if avg_usage_col
                else 0
            )

            category_days = (
                pd.to_numeric(
                    group[days_inventory_col],
                    errors="coerce",
                ).fillna(0).mean()
                if days_inventory_col
                else 0
            )

            category_summary.append(
                {
                    "category": str(category),
                    "skus": int(len(group)),
                    "inventory_value": float(category_value),
                    "daily_demand": float(category_demand),
                    "average_days_inventory": float(
                        category_days
                    ),
                }
            )

    facts["category_summary"] = category_summary

    # --------------------------------------------------------
    # Warehouse summary
    # --------------------------------------------------------

    warehouse_summary = []

    if warehouse_col:

        grouped = df.groupby(warehouse_col)

        for warehouse, group in grouped:

            warehouse_value = (
                pd.to_numeric(
                    group[value_col],
                    errors="coerce",
                ).fillna(0).sum()
                if value_col
                else 0
            )

            warehouse_days = (
                pd.to_numeric(
                    group[days_inventory_col],
                    errors="coerce",
                ).fillna(0).mean()
                if days_inventory_col
                else 0
            )

            low_count = 0
            over_count = 0

            if status_col:
                statuses = group[status_col].apply(
                    _clean_status
                )

                low_count = int(
                    (statuses == "low stock").sum()
                )

                over_count = int(
                    (statuses == "overstock").sum()
                )

            warehouse_summary.append(
                {
                    "warehouse": str(warehouse),
                    "skus": int(len(group)),
                    "inventory_value": float(
                        warehouse_value
                    ),
                    "average_days_inventory": float(
                        warehouse_days
                    ),
                    "low_stock_items": low_count,
                    "overstock_items": over_count,
                }
            )

    facts["warehouse_summary"] = warehouse_summary

    # --------------------------------------------------------
    # Supplier summary
    # --------------------------------------------------------

    supplier_summary = []

    if supplier_col:

        grouped = df.groupby(supplier_col)

        for supplier, group in grouped:

            supplier_value = (
                pd.to_numeric(
                    group[value_col],
                    errors="coerce",
                ).fillna(0).sum()
                if value_col
                else 0
            )

            low_count = 0
            over_count = 0

            if status_col:

                statuses = group[status_col].apply(
                    _clean_status
                )

                low_count = int(
                    (statuses == "low stock").sum()
                )

                over_count = int(
                    (statuses == "overstock").sum()
                )

            supplier_summary.append(
                {
                    "supplier": str(supplier),
                    "skus": int(len(group)),
                    "inventory_value": float(
                        supplier_value
                    ),
                    "low_stock_items": low_count,
                    "overstock_items": over_count,
                }
            )

    facts["supplier_summary"] = supplier_summary

    return facts


# ============================================================
# AI INVENTORY ADVISOR
# ============================================================

def generate_inventory_advice(df):

    """
    Generate an inventory assessment using ONLY verified
    Python-calculated facts.

    Gemini is explicitly prohibited from inventing:
    - SKUs
    - suppliers
    - warehouses
    - quantities
    - percentages
    - causal relationships
    - financial values
    """

    facts = _build_inventory_facts(df)

    if "error" in facts:
        return "Inventory dataset is empty or unavailable."

    # --------------------------------------------------------
    # Build verified fact block
    # --------------------------------------------------------

    prompt = f"""
You are an experienced Supply Chain Manager.

You are reviewing a real inventory dataset.

IMPORTANT:
The numbers below have already been calculated by Python from
the source CSV. Treat them as VERIFIED FACTS.

Your job is ONLY to interpret these facts and write a concise
executive inventory assessment.

DO NOT recalculate numbers.
DO NOT invent any information.
DO NOT introduce names, SKUs, suppliers, warehouses, values,
percentages, quantities, dates, or metrics that are not present
in the verified facts.

CRITICAL GROUNDING RULE:

You may state a FACT only when it appears in the verified data.

You may make a RECOMMENDATION based on a fact, but clearly
present it as a recommendation rather than as an established fact.

Do NOT claim that one event caused another unless the dataset
explicitly establishes causation.

For example:

ALLOWED:
"125 purchase orders have pending payment status."

NOT ALLOWED:
"Pending payments are causing supplier delivery delays."

ALLOWED:
"142 purchase orders are delayed."

NOT ALLOWED:
"These delays are caused by payment issues."

ALLOWED:
"SKU-1006 has 0 units in stock."

NOT ALLOWED:
"SKU-1006 will stop production."

Do not use words such as:
"caused by", "resulted in", "due to", "driving",
"retaliatory", "will halt", "will cause", or similar causal
language unless the supplied data explicitly proves the
relationship.

------------------------------------------------------------
VERIFIED INVENTORY FACTS
------------------------------------------------------------

Total SKUs:
{facts["total_skus"]}

Total Inventory Value:
{_format_currency(facts["total_inventory_value"])}

Healthy Items:
{facts["healthy_items"]}

Low Stock Items:
{facts["low_stock_items"]}

Overstock Items:
{facts["overstock_items"]}

Healthy Inventory Percentage:
{_format_percent(facts["healthy_percent"])}

Total Daily Demand:
{_format_number(facts["total_daily_demand"])}

Average Daily Demand per SKU:
{_format_number(facts["average_daily_demand_per_sku"])}

------------------------------------------------------------
CRITICAL LOW-STOCK ITEMS
------------------------------------------------------------

{facts["critical_low_stock_items"]}

------------------------------------------------------------
OVERSTOCK ITEMS
------------------------------------------------------------

{facts["overstock_items"]}

------------------------------------------------------------
CATEGORY SUMMARY
------------------------------------------------------------

{facts["category_summary"]}

------------------------------------------------------------
WAREHOUSE SUMMARY
------------------------------------------------------------

{facts["warehouse_summary"]}

------------------------------------------------------------
SUPPLIER SUMMARY
------------------------------------------------------------

{facts["supplier_summary"]}

------------------------------------------------------------
REQUIRED OUTPUT
------------------------------------------------------------

Use EXACTLY these headings:

## Executive Summary

## Key Findings

## Risks

## Recommendations

## Priority Actions

Keep the report concise and suitable for senior management.

Every numerical statement must be supported by the verified
facts above.

Do not invent explanations for why a condition exists.

Recommendations should be operational suggestions based on
the observed inventory conditions.

Do not introduce new metrics or new entities.

Do not repeat the same point unnecessarily.
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt,
    )

    return response.text


# ============================================================
# VERIFIED PROCUREMENT FACTS
# ============================================================

def _build_procurement_facts(procurement_df):

    """
    Calculate procurement metrics in Python before Gemini sees
    them.
    """

    if procurement_df is None or procurement_df.empty:
        return {
            "error": "Procurement dataset is empty."
        }

    facts = {}

    facts["total_purchase_orders"] = int(
        len(procurement_df)
    )

    # --------------------------------------------------------
    # Procurement value
    # --------------------------------------------------------

    value_col = _find_column(
        procurement_df,
        [
            "PurchaseOrderValueUSD",
            "PurchaseOrderValue",
            "POValueUSD",
            "PO_Value_USD",
            "OrderValueUSD",
            "OrderValue",
            "ProcurementValueUSD",
        ],
    )

    if value_col:

        values = pd.to_numeric(
            procurement_df[value_col],
            errors="coerce",
        ).fillna(0)

        facts["total_procurement_spend"] = float(
            values.sum()
        )

        facts["average_order_value"] = (
            float(values.mean())
            if len(values) > 0
            else 0.0
        )

    else:

        facts["total_procurement_spend"] = None
        facts["average_order_value"] = None

    # --------------------------------------------------------
    # Delivery delay
    # --------------------------------------------------------

    delay_col = _find_column(
        procurement_df,
        [
            "DeliveryDelayDays",
            "Delivery Delay Days",
            "DelayDays",
            "Delay_Days",
        ],
    )

    if delay_col:

        delays = pd.to_numeric(
            procurement_df[delay_col],
            errors="coerce",
        ).fillna(0)

        delayed_mask = delays > 0

        facts["delayed_orders"] = int(
            delayed_mask.sum()
        )

        facts["delay_rate"] = (
            facts["delayed_orders"]
            / facts["total_purchase_orders"]
            * 100
            if facts["total_purchase_orders"] > 0
            else 0.0
        )

        facts["average_delivery_delay"] = (
            float(delays.mean())
            if len(delays) > 0
            else 0.0
        )

    else:

        facts["delayed_orders"] = None
        facts["delay_rate"] = None
        facts["average_delivery_delay"] = None

    # --------------------------------------------------------
    # Lead time
    # --------------------------------------------------------

    lead_col = _find_column(
        procurement_df,
        [
            "LeadTimeDays",
            "Lead Time Days",
            "LeadTime",
            "Lead_Time_Days",
        ],
    )

    if lead_col:

        lead_times = pd.to_numeric(
            procurement_df[lead_col],
            errors="coerce",
        ).dropna()

        facts["average_lead_time"] = (
            float(lead_times.mean())
            if len(lead_times) > 0
            else 0.0
        )

    else:

        facts["average_lead_time"] = None

    # --------------------------------------------------------
    # Payment status
    # --------------------------------------------------------

    payment_col = _find_column(
        procurement_df,
        [
            "PaymentStatus",
            "Payment Status",
        ],
    )

    if payment_col:

        payment_status = (
            procurement_df[payment_col]
            .astype(str)
            .str.strip()
            .str.lower()
        )

        pending_mask = payment_status == "pending"

        facts["pending_payment_orders"] = int(
            pending_mask.sum()
        )

        facts["pending_payment_rate"] = (
            facts["pending_payment_orders"]
            / facts["total_purchase_orders"]
            * 100
            if facts["total_purchase_orders"] > 0
            else 0.0
        )

    else:

        facts["pending_payment_orders"] = None
        facts["pending_payment_rate"] = None

    # --------------------------------------------------------
    # Supplier summary
    # --------------------------------------------------------

    supplier_col = _find_column(
        procurement_df,
        [
            "Supplier",
        ],
    )

    supplier_summary = []

    if supplier_col:

        grouped = procurement_df.groupby(
            supplier_col
        )

        for supplier, group in grouped:

            supplier_value = None

            if value_col:

                supplier_value = float(
                    pd.to_numeric(
                        group[value_col],
                        errors="coerce",
                    )
                    .fillna(0)
                    .sum()
                )

            delayed_orders = None

            if delay_col:

                delay_values = pd.to_numeric(
                    group[delay_col],
                    errors="coerce",
                ).fillna(0)

                delayed_orders = int(
                    (delay_values > 0).sum()
                )

            supplier_summary.append(
                {
                    "supplier": str(supplier),
                    "purchase_orders": int(len(group)),
                    "procurement_value": supplier_value,
                    "delayed_orders": delayed_orders,
                }
            )

    facts["supplier_summary"] = supplier_summary

    return facts


# ============================================================
# AI EXECUTIVE SUPPLY CHAIN ADVISOR
# ============================================================

def generate_executive_supply_chain_summary(
    inventory_df,
    procurement_df,
):
    """
    Generates an executive-level supply chain report.

    Python calculates the verified metrics first.
    Gemini only converts those metrics into executive language.
    """

    inventory_facts = _build_inventory_facts(
        inventory_df
    )

    procurement_facts = _build_procurement_facts(
        procurement_df
    )

    if "error" in inventory_facts:
        return "Inventory dataset is empty or unavailable."

    if "error" in procurement_facts:
        return "Procurement dataset is empty or unavailable."

    # ========================================================
    # VERIFIED FACT BLOCK
    # ========================================================

    prompt = f"""
You are the Chief Supply Chain Officer of a global
manufacturing company.

Prepare an executive management report using ONLY the verified
facts supplied below.

The figures were calculated by Python directly from the source
CSV datasets.

You MUST NOT independently invent, infer, or fabricate data.

============================================================
GROUNDING RULES
============================================================

1. Use ONLY entities that appear in the verified facts.

2. Use ONLY numerical values that appear in the verified facts.

3. Do not invent SKUs, suppliers, warehouses, purchase orders,
   quantities, dates, percentages, costs, or metrics.

4. Do not calculate new numerical metrics.

5. Do not claim causation unless causation is explicitly
   established by the supplied data.

6. Do not convert correlation or simultaneous conditions into
   causal statements.

7. Separate observations from recommendations.

8. Recommendations may suggest an action, but must not state
   that the action will definitely produce a particular result.

9. If a conclusion is not supported by the supplied facts,
   leave it out.

10. Do not mention data that is not present in the verified
    fact block.

NUMBER FORMATTING RULES:

11. Format all currency values to exactly 2 decimal places with commas.
    Example: $1,121,242.59

12. Format percentages to 1 decimal place.
    Example: 71.0%

13. Format days and other decimal metrics to 1 decimal place.
    Example: 29.6 days

14. Never display long floating-point values.

15. Always include proper spaces between numbers and words.
    Example: "$152,135.50 in excess value"       

Examples:

FACT:
"142 purchase orders are delayed."

NOT:
"Payment delays caused the 142 delayed orders."

FACT:
"125 purchase orders have pending payment status."

NOT:
"Suppliers are withholding shipments because of unpaid invoices."

FACT:
"SKU-1006 has 0 units in stock."

NOT:
"SKU-1006 will stop production."

FACT:
"Warehouse A has 5 overstock items."

NOT:
"Warehouse A has a storage crisis."

============================================================
VERIFIED INVENTORY FACTS
============================================================

Total SKUs:
{inventory_facts["total_skus"]}

Total Inventory Value:
{_format_currency(inventory_facts["total_inventory_value"])}

Healthy Items:
{inventory_facts["healthy_items"]}

Low Stock Items:
{inventory_facts["low_stock_items"]}

Overstock Items:
{inventory_facts["overstock_items"]}

Healthy Inventory Percentage:
{_format_percent(inventory_facts["healthy_percent"])}

Total Daily Demand:
{_format_number(inventory_facts["total_daily_demand"])}

Average Daily Demand per SKU:
{_format_number(
    inventory_facts["average_daily_demand_per_sku"]
)}

Critical Low-Stock Items:
{inventory_facts["critical_low_stock_items"]}

Overstock Items:
{inventory_facts["overstock_items"]}

Category Summary:
{inventory_facts["category_summary"]}

Warehouse Summary:
{inventory_facts["warehouse_summary"]}

Inventory Supplier Summary:
{inventory_facts["supplier_summary"]}


============================================================
VERIFIED PROCUREMENT FACTS
============================================================

Total Purchase Orders:
{procurement_facts["total_purchase_orders"]}

Total Procurement Spend:
{
    _format_currency(
        procurement_facts["total_procurement_spend"]
    )
    if procurement_facts["total_procurement_spend"] is not None
    else "Not available"
}

Average Order Value:
{
    _format_currency(
        procurement_facts["average_order_value"]
    )
    if procurement_facts["average_order_value"] is not None
    else "Not available"
}

Delayed Orders:
{
    procurement_facts["delayed_orders"]
    if procurement_facts["delayed_orders"] is not None
    else "Not available"
}

Delay Rate:
{
    _format_percent(
        procurement_facts["delay_rate"]
    )
    if procurement_facts["delay_rate"] is not None
    else "Not available"
}

Average Delivery Delay:
{
    _format_number(
        procurement_facts["average_delivery_delay"]
    )
    if procurement_facts["average_delivery_delay"] is not None
    else "Not available"
}

Average Lead Time:
{
    _format_number(
        procurement_facts["average_lead_time"]
    )
    if procurement_facts["average_lead_time"] is not None
    else "Not available"
}

Pending Payment Orders:
{
    procurement_facts["pending_payment_orders"]
    if procurement_facts["pending_payment_orders"] is not None
    else "Not available"
}

Pending Payment Rate:
{
    _format_percent(
        procurement_facts["pending_payment_rate"]
    )
    if procurement_facts["pending_payment_rate"] is not None
    else "Not available"
}

Procurement Supplier Summary:
{procurement_facts["supplier_summary"]}


============================================================
REPORT STRUCTURE
============================================================

Use EXACTLY these headings:

# Executive Summary

## Inventory Overview

## Procurement Overview

## Supplier Insights

## Warehouse Insights

## Demand Insights

## Risks

## Opportunities

## Top 5 Executive Recommendations


============================================================
WRITING REQUIREMENTS
============================================================

Executive Summary:
Give a concise overview of the verified inventory and
procurement conditions.

Inventory Overview:
Discuss inventory value, stock-status distribution, and the
most important verified stock extremes.

Procurement Overview:
Discuss purchase-order volume, procurement spend, delays,
lead time, and pending payments only where those facts are
available.

Supplier Insights:
Use only suppliers present in the verified supplier summaries.

Warehouse Insights:
Use only warehouses present in the verified warehouse summary.

Demand Insights:
Focus specifically on daily demand, category demand, and
inventory coverage where available.

Do NOT substitute inventory value for demand.

Risks:
Describe observable operational risks based on the data.
Do not claim unsupported causes.

Opportunities:
Describe practical opportunities based on observed inventory
or procurement conditions.

Top 5 Executive Recommendations:
Give exactly five concise recommendations.
Each recommendation must be traceable to one or more verified
facts.

Do not invent implementation results.

Do not use unsupported causal language.

Do not use phrases such as:
"this caused"
"this resulted in"
"due to"
"therefore suppliers are"
"will halt production"
"will cause"
"retaliatory"
"production will stop"

unless the supplied facts explicitly establish those
relationships.

Keep the report professional, concise, factual, and suitable
for senior management.
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt,
    )

    return response.text