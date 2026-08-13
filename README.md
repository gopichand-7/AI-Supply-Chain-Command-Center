# 📦 AI Supply Chain Command Center

An AI-powered Supply Chain Analytics Dashboard built with **Python**, **Streamlit**, **Plotly**, and **Google Gemini AI**.

The project demonstrates how Artificial Intelligence can enhance supply chain decision-making through interactive dashboards, inventory analytics, procurement insights, supplier and warehouse analysis, demand forecasting, and executive-level recommendations generated using Google Gemini.

The application combines data-driven analytics with AI-generated insights to help users monitor supply chain operations, identify risks, analyze inventory performance, and support informed decision-making.

> ⚠️ **Data Disclaimer:** This project uses **synthetic, demonstration-only datasets** created for portfolio and educational purposes. No confidential, proprietary, or real company data is used. All analytics, visualizations, AI-generated insights, and PDF reports are based on the included demonstration dataset or compatible data uploaded by the user.

---

## 🚀 Current Version

**Version:** `v1.0`
**Status:** ✅ Complete

---

## 🌐 Live Application

**AI Supply Chain Command Center:**
https://ai-supply-chain-command-center.streamlit.app

---

## 🖼️ Dashboard Preview

![AI Supply Chain Command Center Dashboard](assets/Screenshot%202026-08-13%20155221.png)

---

## ✅ Implemented Features

- 📊 Executive KPI Dashboard
- 📈 Category-wise Inventory Analytics
- 🏭 Warehouse Distribution Analytics
- 🧠 AI Executive Supply Chain Command Center
- 🚨 Critical Inventory Analysis
- 📦 Overstock Inventory Analysis
- 🤖 AI Inventory Advisor powered by Google Gemini
- 🔤 ABC Inventory Classification
- 📂 Category Analytics
- 🏭 Warehouse Analytics
- 🤝 Supplier Analytics
- 🛒 Procurement Analytics
- 📦 Supplier Management Insights
- 🚚 Warehouse & Logistics Analytics
- 📈 Demand Forecasting Dashboard
- 📄 AI Executive Report Generation
- ⬇️ Markdown Report Download
- 📑 Professional PDF Report Download
- 📋 Interactive Inventory Dataset Viewer
- 📤 Upload Custom Inventory and Procurement Datasets

---

## 🛠️ Tech Stack

| Category | Tools |
|---|---|
| Programming Language | Python 3 |
| Framework | Streamlit |
| Data Processing | Pandas |
| Data Visualization | Plotly |
| Artificial Intelligence | Google Gemini AI (`google-genai`) |
| File Generation | ReportLab (PDF), Markdown export |
| Environment Management | python-dotenv |
| Version Control | Git, GitHub |
| Development Environment | Visual Studio Code |
| Hosting | Streamlit Community Cloud |
| Deployment Environment | Python 3.12 |

---

## 📂 Project Structure

```text
AI-Supply-Chain-Command-Center/
│
├── assets/
│   └── Project screenshots and README preview images
│
├── data/
│   ├── inventory_data.csv
│   └── procurement_data.csv
│
├── utils/
│   ├── calculations.py
│   └── ai_inventory_advisor.py
│
├── app.py
├── requirements.txt
├── .gitignore
├── README.md
└── .env (not included in Git)
```

### Folder / File Reference

| File / Folder | Purpose |
|---|---|
| `app.py` | Main Streamlit application and dashboard |
| `data/inventory_data.csv` | Demonstration inventory dataset |
| `data/procurement_data.csv` | Demonstration procurement dataset |
| `utils/calculations.py` | KPI calculations and supply chain analytics logic |
| `utils/ai_inventory_advisor.py` | Google Gemini AI integration and AI report generation |
| `assets/` | Project screenshots and visual resources |
| `requirements.txt` | Python dependencies |
| `.gitignore` | Files excluded from Git tracking |
| `.env` | Stores the Gemini API key securely (not committed) |
| `README.md` | Project documentation |

---

## ⚙️ Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/gopichand-7/AI-Supply-Chain-Command-Center.git
cd AI-Supply-Chain-Command-Center
```

### 2. Create a virtual environment

**Windows**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure your Gemini API key
Create a `.env` file in the project root:
```env
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
```
Generate a key from **[Google AI Studio](https://aistudio.google.com/apikey)**.

> ⚠️ Never commit your Gemini API key or `.env` file to GitHub.

### 5. Run the application
```bash
streamlit run app.py
```
The app will be available at `http://localhost:8501`.

---

## ☁️ Deployment

The application is deployed on **Streamlit Community Cloud**.

**Configuration**
- Repository: `gopichand-7/AI-Supply-Chain-Command-Center`
- Branch: `main`
- Main file: `app.py`
- Python version: `3.12`

**Secrets** (set in Streamlit Cloud → App Settings → Secrets)
```toml
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
```

**Shipping an update**
```bash
git add .
git commit -m "Your update message"
git push
```
Streamlit Cloud auto-redeploys on push. If it doesn't pick up the change, use the app's **⋮ menu → Reboot app**.

---

## ✨ Feature Details

### 📊 Executive KPI Dashboard
High-level overview of supply chain and inventory performance using interactive KPI cards, derived from the currently selected dataset.

### 📈 Interactive Supply Chain Analytics
Plotly-driven visualizations across category distribution, warehouse distribution, inventory value, ABC classification, supplier performance, procurement activity, warehouse & logistics, and demand.

### 🚨 Critical Inventory Analysis
Flags items where stock levels fall below defined thresholds, helping prioritize replenishment decisions.

### 📦 Overstock Inventory Analysis
Flags items exceeding their maximum stock level, highlighting excess inventory exposure.

### 🔤 ABC Inventory Classification
Segments inventory into **A, B, and C** classes by value to support prioritization.

### 📂 Category / 🏭 Warehouse / 🤝 Supplier / 🛒 Procurement Analytics
Dedicated dashboards breaking down inventory value, distribution, and performance across each dimension.

### 🚚 Warehouse & Logistics Dashboard
Per-warehouse inventory value, procurement spend, and lead time.

### 📈 Demand Forecasting Dashboard
Daily demand analysis and visualization by category to support planning.

---

## 🤖 AI Inventory Advisor

Generates inventory-focused insights using **Google Gemini AI**, covering:
- Executive Summary
- Key Findings
- Risks
- Recommendations
- Priority Actions
- Low-stock and overstock analysis
- Warehouse and supplier-related insights

All relevant metrics are calculated in Python and provided to the AI as verified context — the model interprets pre-computed facts rather than generating its own numbers.

---

## 🧠 AI Executive Supply Chain Command Center

Generates a management-level AI Executive Report covering:

1. Executive Summary
2. Inventory Overview
3. Procurement Overview
4. Supplier Insights
5. Warehouse Insights
6. Demand Insights
7. Risks
8. Opportunities
9. Top 5 Executive Recommendations

Metrics and dataset facts are calculated in Python and supplied as grounding context, and the AI is explicitly instructed to avoid unsupported figures, entities, or causal claims outside the supplied data.

> **Note:** Google's Gemini free tier caps requests at **20 `generate_content` calls per day per model**. A `429 RESOURCE_EXHAUSTED` error means that daily cap has been reached — it resets on a rolling 24-hour window, or can be removed with a paid Gemini API plan.

---

## 📄 Executive Report Downloads

**⬇️ Markdown Download** — the generated AI Executive Report in Markdown format for documentation or reuse.

**📑 Professional PDF Download** — a structured executive PDF covering:
- Executive Overview
- Critical Risks and Financial Exposure
- Procurement and Supplier Performance
- Warehouse and Demand Intelligence
- Strategic Recommendations
- Priority Action Plan
- Executive Conclusion

---

## 📤 Custom Dataset Upload

Use the included demonstration datasets, or upload your own compatible Inventory and Procurement datasets.

**Supported formats:** CSV (`.csv`), Excel (`.xlsx`)

**Inventory dataset columns**
```
SKU, ItemName, Category, Supplier, Warehouse, UnitCostUSD, CurrentStock,
SafetyStock, ReorderLevel, MaxStockLevel, AvgDailyUsage, DaysOfInventory,
InventoryValueUSD, LastRestockDate
```

**Procurement dataset columns**
```
PO_ID, OrderDate, ExpectedDelivery, ActualDelivery, SKU, ItemName, Supplier,
Category, Warehouse, OrderQuantity, UnitCostUSD, TotalOrderValueUSD,
LeadTimeDays, DeliveryDelayDays, OrderStatus, PaymentStatus, Buyer
```

---

## 🎯 Skills Demonstrated

Supply Chain Analytics · Inventory Management Analytics · Procurement Analytics · Supplier Analysis · Warehouse Analytics · Logistics Analytics · Demand Analysis · Python Programming · Pandas Data Analysis · Business KPI Development · Interactive Dashboard Development · Plotly Data Visualization · Streamlit Application Development · Google Gemini AI Integration · Dataset-Grounded AI Workflows · AI-Assisted Business Insights · Executive Reporting · PDF Report Generation · Git and GitHub · Cloud Deployment · Business Decision Support

---

## 👨‍💻 Author

**Gopichand Kollapattu**
GitHub: [github.com/gopichand-7](https://github.com/gopichand-7)

---

## 📄 License

This project is licensed under the **[MIT License](LICENSE)** — free to use, modify, and distribute with attribution.
