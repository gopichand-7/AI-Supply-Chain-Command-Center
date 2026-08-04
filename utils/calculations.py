import pandas as pd
import numpy as np


def add_stock_status(df):
    conditions = [
        df["CurrentStock"] < df["ReorderLevel"],
        df["CurrentStock"] > df["MaxStockLevel"],
    ]

    choices = [
        "🔴 Low Stock",
        "🟡 Overstock",
    ]

    df["StockStatus"] = np.select(
        conditions,
        choices,
        default="🟢 Healthy"
    )

    return df


def calculate_kpis(df):
    total_inventory_value = df["InventoryValueUSD"].sum()

    inventory_health = (
        (df["StockStatus"] == "🟢 Healthy").sum() / len(df)
    ) * 100

    low_stock = (df["StockStatus"] == "🔴 Low Stock").sum()

    overstock = (df["StockStatus"] == "🟡 Overstock").sum()

    return {
        "Total Inventory Value": total_inventory_value,
        "Inventory Health": inventory_health,
        "Low Stock": low_stock,
        "Overstock": overstock,
    }


# ==========================================================
# Top Critical Inventory
# ==========================================================

def get_top_critical_inventory(df, top_n=10):
    """
    Returns the most critical inventory items where
    CurrentStock is below ReorderLevel.
    """

    critical = df[df["CurrentStock"] < df["ReorderLevel"]].copy()

    critical = critical.sort_values(
        by=["DaysOfInventory", "InventoryValueUSD"],
        ascending=[True, False]
    )

    return critical[
        [
            "SKU",
            "ItemName",
            "Category",
            "CurrentStock",
            "ReorderLevel",
            "DaysOfInventory",
            "InventoryValueUSD",
        ]
    ].head(top_n)


# ==========================================================
# Overstock Inventory
# ==========================================================

def get_overstock_inventory(df, top_n=10):
    """
    Returns the most overstocked inventory items where
    CurrentStock exceeds MaxStockLevel.
    """

    overstock = df[df["CurrentStock"] > df["MaxStockLevel"]].copy()

    overstock = overstock.sort_values(
        by="InventoryValueUSD",
        ascending=False
    )

    return overstock[
        [
            "SKU",
            "ItemName",
            "Category",
            "CurrentStock",
            "MaxStockLevel",
            "InventoryValueUSD",
        ]
    ].head(top_n)


# ==========================================================
# ABC Inventory Classification
# ==========================================================

def get_abc_inventory(df):
    """
    Classifies inventory into A, B, and C classes
    based on cumulative inventory value.
    """

    abc_df = df.sort_values(
        by="InventoryValueUSD",
        ascending=False
    ).copy()

    total_value = abc_df["InventoryValueUSD"].sum()

    abc_df["CumulativeValue"] = abc_df["InventoryValueUSD"].cumsum()

    abc_df["CumulativePct"] = (
        abc_df["CumulativeValue"] / total_value
    ) * 100

    def classify(pct):
        if pct <= 80:
            return "A"
        elif pct <= 95:
            return "B"
        else:
            return "C"

    abc_df["ABC_Class"] = abc_df["CumulativePct"].apply(classify)

    return abc_df


# ==========================================================
# Category Summary
# ==========================================================

def get_category_summary(df):
    """
    Returns category-wise inventory summary.
    """

    summary = (
        df.groupby("Category")
        .agg(
            Total_SKUs=("SKU", "count"),
            Inventory_Value_USD=("InventoryValueUSD", "sum"),
            Average_Days=("DaysOfInventory", "mean"),
            Healthy_Items=("StockStatus", lambda x: (x == "🟢 Healthy").sum()),
            Low_Stock_Items=("StockStatus", lambda x: (x == "🔴 Low Stock").sum()),
            Overstock_Items=("StockStatus", lambda x: (x == "🟡 Overstock").sum()),
        )
        .reset_index()
    )

    summary["Average_Days"] = summary["Average_Days"].round(1)

    summary = summary.sort_values(
        by="Inventory_Value_USD",
        ascending=False
    )

    return summary