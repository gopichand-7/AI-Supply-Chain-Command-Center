import streamlit as st
import pandas as pd
import plotly.express as px

from utils.calculations import add_stock_status, calculate_kpis
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
st.markdown("### Executive Dashboard (v0.1)")

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

    st.plotly_chart(fig, use_container_width=True)

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

    st.plotly_chart(fig, use_container_width=True)

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
# Inventory Dataset
# -----------------------------------

st.subheader("📋 Inventory Dataset")

st.dataframe(df, use_container_width=True)