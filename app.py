import streamlit as st
import pandas as pd
import plotly.express as px

from utils.calculations import (
    add_stock_status,
    calculate_kpis,
    get_top_critical_inventory,
    get_overstock_inventory,
    get_abc_inventory,
    get_category_summary,
    get_warehouse_summary,
    get_supplier_summary,
)
from utils.ai_inventory_advisor import generate_inventory_advice

# -----------------------------------
# Page Configuration
# -----------------------------------

st.set_page_config(
    page_title="AI Supply Chain Command Center",
    page_icon="📦",
    layout="wide"
)

# -----------------------------------
# Title
# -----------------------------------

st.title("📦 AI Supply Chain Command Center")
st.markdown("### Executive Dashboard (v0.2.6)")

# -----------------------------------
# Load Data
# -----------------------------------

try:
    df = pd.read_csv("data/inventory_data.csv")
    trend_df = pd.read_csv("data/inventory_trend.csv")

    trend_df["Date"] = pd.to_datetime(trend_df["Date"])

    df = add_stock_status(df)
    kpis = calculate_kpis(df)

    st.success("Inventory data loaded successfully!")

except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# -----------------------------------
# KPI Dashboard
# -----------------------------------

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "💰 Total Inventory Value",
        f"${kpis['Total Inventory Value']:,.2f}"
    )

with col2:
    st.metric(
        "📈 Inventory Health",
        f"{kpis['Inventory Health']:.1f}%"
    )

with col3:
    st.metric(
        "🔴 Low Stock Items",
        kpis["Low Stock"]
    )

with col4:
    st.metric(
        "🟡 Overstock Items",
        kpis["Overstock"]
    )

st.divider()

# -----------------------------------
# Inventory Value by Category
# -----------------------------------

col1, col2 = st.columns(2)

with col1:

    st.subheader("📊 Inventory Value by Category")

    category_value = (
        df.groupby("Category")["InventoryValueUSD"]
        .sum()
        .reset_index()
    )

    fig = px.bar(
        category_value,
        x="Category",
        y="InventoryValueUSD",
        text_auto=".2s",
        title="Inventory Investment by Category"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with col2:

    st.subheader("🏭 Warehouse Inventory Distribution")

    warehouse_value = (
        df.groupby("Warehouse")["InventoryValueUSD"]
        .sum()
        .reset_index()
    )

    fig = px.pie(
        warehouse_value,
        names="Warehouse",
        values="InventoryValueUSD",
        title="Inventory Value by Warehouse"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

st.divider()

# -----------------------------------
# AI Inventory Advisor
# -----------------------------------

st.subheader("🤖 AI Inventory Advisor")

st.write(
    "Generate executive-level inventory insights and recommendations using Google Gemini AI."
)

if st.button("Generate AI Inventory Analysis"):

    with st.spinner("Analyzing inventory using Gemini AI..."):

        try:

            advice = generate_inventory_advice(df)

            st.success("AI analysis completed successfully.")

            st.markdown(advice)

        except Exception as e:

            st.error(f"AI Analysis Failed: {e}")

st.divider()

# -----------------------------------
# Top Critical Inventory
# -----------------------------------

st.subheader("🚨 Top Critical Inventory")

critical_df = get_top_critical_inventory(df)

st.caption(
    "Items where Current Stock is below the Reorder Level, sorted by urgency."
)

st.dataframe(
    critical_df,
    use_container_width=True,
    hide_index=True,
)

st.divider()

# -----------------------------------
# Overstock Inventory
# -----------------------------------

st.subheader("📦 Overstock Inventory")

st.caption(
    "Items where Current Stock exceeds the Maximum Stock Level."
)

overstock_df = get_overstock_inventory(df)

st.dataframe(
    overstock_df,
    use_container_width=True,
    hide_index=True,
)

st.divider()

# -----------------------------------
# ABC Inventory Classification
# -----------------------------------

st.subheader("📊 ABC Inventory Classification (Value-Based)")

abc_df = get_abc_inventory(df)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "🟢 A Items",
        (abc_df["ABC_Class"] == "A").sum()
    )

with col2:
    st.metric(
        "🟡 B Items",
        (abc_df["ABC_Class"] == "B").sum()
    )

with col3:
    st.metric(
        "🔴 C Items",
        (abc_df["ABC_Class"] == "C").sum()
    )

abc_summary = (
    abc_df["ABC_Class"]
    .value_counts()
    .reset_index()
)

abc_summary.columns = ["ABC_Class", "Count"]

fig = px.pie(
    abc_summary,
    names="ABC_Class",
    values="Count",
    title="ABC Inventory Distribution"
)

st.plotly_chart(
    fig,
    use_container_width=True,
)

st.dataframe(
    abc_df[
        [
            "SKU",
            "ItemName",
            "Category",
            "InventoryValueUSD",
            "CumulativePct",
            "ABC_Class",
        ]
    ],
    use_container_width=True,
    hide_index=True,
)

st.divider()
# -----------------------------------
# Category Summary
# -----------------------------------

st.subheader("📂 Category Summary")

category_summary = get_category_summary(df)

# KPI Cards

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "📦 Categories",
        len(category_summary)
    )

with col2:
    st.metric(
        "💰 Total Category Value",
        f"${category_summary['Inventory_Value_USD'].sum():,.2f}"
    )

with col3:
    st.metric(
        "📈 Avg. Days of Inventory",
        f"{category_summary['Average_Days'].mean():.1f}"
    )

st.divider()

# Charts

col1, col2 = st.columns(2)

with col1:

    fig = px.bar(
        category_summary,
        x="Category",
        y="Inventory_Value_USD",
        color="Category",
        text_auto=".2s",
        title="Inventory Value by Category"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with col2:

    fig = px.pie(
        category_summary,
        names="Category",
        values="Inventory_Value_USD",
        title="Inventory Value Distribution"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

st.divider()

# Summary Table

st.dataframe(
    category_summary,
    use_container_width=True,
    hide_index=True,
)

st.divider()
# -----------------------------------
# Warehouse Summary
# -----------------------------------

st.divider()

st.subheader("🏭 Warehouse Summary")

warehouse_summary = get_warehouse_summary(df)

# KPI Cards

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "🏭 Warehouses",
        len(warehouse_summary)
    )

with col2:
    st.metric(
        "💰 Total Warehouse Value",
        f"${warehouse_summary['Inventory_Value_USD'].sum():,.2f}"
    )

with col3:
    st.metric(
        "📈 Avg. Days of Inventory",
        f"{warehouse_summary['Average_Days'].mean():.1f}"
    )

st.divider()

# Charts

col1, col2 = st.columns(2)

with col1:

    fig = px.bar(
        warehouse_summary,
        x="Warehouse",
        y="Inventory_Value_USD",
        color="Warehouse",
        text_auto=".2s",
        title="Inventory Value by Warehouse"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with col2:

    fig = px.pie(
        warehouse_summary,
        names="Warehouse",
        values="Inventory_Value_USD",
        title="Warehouse Inventory Distribution"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

st.divider()

# Summary Table

st.dataframe(
    warehouse_summary,
    use_container_width=True,
    hide_index=True,
)
# -----------------------------------
# Supplier Performance Dashboard
# -----------------------------------

st.divider()

st.subheader("🏢 Supplier Performance Dashboard")

supplier_summary = get_supplier_summary(df)

# KPI Cards

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "🏢 Total Suppliers",
        len(supplier_summary)
    )

with col2:
    st.metric(
        "💰 Total Supplier Value",
        f"${supplier_summary['Inventory_Value_USD'].sum():,.2f}"
    )

with col3:
    st.metric(
        "📈 Avg. Days of Inventory",
        f"{supplier_summary['Average_Days'].mean():.1f}"
    )

st.divider()

# Charts

col1, col2 = st.columns(2)

with col1:

    fig = px.bar(
        supplier_summary,
        x="Supplier",
        y="Inventory_Value_USD",
        color="Supplier",
        text_auto=".2s",
        title="Inventory Value by Supplier"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with col2:

    fig = px.pie(
        supplier_summary,
        names="Supplier",
        values="Inventory_Value_USD",
        title="Supplier Inventory Distribution"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

st.divider()

# Summary Table

st.dataframe(
    supplier_summary,
    use_container_width=True,
    hide_index=True,
)
# -----------------------------------
# Inventory Dataset
# -----------------------------------

st.subheader("📋 Inventory Dataset")

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True,
)