import os
from google import genai
from dotenv import load_dotenv

# ------------------------------------
# Load Environment Variables
# ------------------------------------

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("Gemini API Key not found.")

# ------------------------------------
# Create Gemini Client
# ------------------------------------

client = genai.Client(api_key=GEMINI_API_KEY)

# ------------------------------------
# AI Inventory Advisor
# ------------------------------------

def generate_inventory_advice(df):

    prompt = f"""
You are an experienced Supply Chain Manager.

Analyze the following inventory summary and provide an executive-level inventory assessment.

Inventory Summary

Total Inventory Value:
${df["InventoryValueUSD"].sum():,.2f}

Inventory Health:
{((df["StockStatus"] == "🟢 Healthy").sum() / len(df)) * 100:.1f}%

Low Stock Items:
{(df["StockStatus"] == "🔴 Low Stock").sum()}

Overstock Items:
{(df["StockStatus"] == "🟡 Overstock").sum()}

Category Summary:
{df.groupby("Category")["InventoryValueUSD"].sum().to_string()}

Warehouse Summary:
{df.groupby("Warehouse")["InventoryValueUSD"].sum().to_string()}

Generate your response using this exact format:

## Executive Summary

## Key Findings

## Risks

## Recommendations

## Priority Actions

Keep the response professional, concise, and suitable for senior management.
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt,
    )

    return response.text