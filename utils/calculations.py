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