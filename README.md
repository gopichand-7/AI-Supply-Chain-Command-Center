# 📦 AI Supply Chain Command Center

An AI-powered Supply Chain Analytics Dashboard built with **Python**, **Streamlit**, **Plotly**, and **Google Gemini AI**.

This project demonstrates how Artificial Intelligence can enhance supply chain decision-making through interactive dashboards, inventory analytics, and executive-level recommendations.

It is being developed as a portfolio project using an incremental versioning approach, where each release introduces a new, fully tested supply chain capability while maintaining a stable and production-style development workflow.

---

# 🚀 Current Version

**Version:** `v0.1`

## ✅ Implemented Features

- 📊 Executive Inventory Dashboard
- 📈 Inventory KPI Cards
- 📦 Inventory Health Analysis
- 📂 Category-wise Inventory Analysis
- 🏭 Warehouse Distribution Analytics
- 🤖 AI Inventory Advisor powered by Google Gemini
- 📋 Interactive Inventory Dataset Viewer

---

# 🚀 Development Roadmap

The project is being developed incrementally. Each version introduces a new supply chain capability while maintaining a stable and tested codebase.

## ✅ Completed

- [x] **v0.1** — Executive Inventory Dashboard with Google Gemini AI

---

## 🚧 In Progress

- [ ] **v0.2** — Advanced Inventory Analytics
  - Top Critical Inventory
  - Overstock Inventory
  - ABC Inventory Classification
  - Category Summary
  - Warehouse Summary
  - Supplier Summary

---

## 📅 Planned

- [ ] **v0.3** — Supplier Performance Analytics
- [ ] **v0.4** — Procurement Analytics Dashboard
- [ ] **v0.5** — Warehouse Operations Dashboard
- [ ] **v0.6** — Logistics & Transportation Analytics
- [ ] **v0.7** — Demand Forecasting Dashboard
- [ ] **v0.8** — Integrated AI Supply Chain Advisor
- [ ] **v0.9** — Executive Reporting & Insights
- [ ] **v1.0** — AI Supply Chain Command Center

---

# 🛠️ Tech Stack

### Programming Language

- Python 3

### Framework

- Streamlit

### Data Processing

- Pandas

### Data Visualization

- Plotly

### Artificial Intelligence

- Google Gemini AI (`google-genai` SDK)

### File Generation

- ReportLab (PDF Reports)
- OpenPyXL (Excel Export)

### Environment Management

- python-dotenv

### Version Control

- Git
- GitHub

### Development Environment

- Visual Studio Code

---

# 📂 Project Structure

```text
AI-Supply-Chain-Command-Center/
│
├── data/
│   └── inventory_data.csv
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

### Folder Description

| File / Folder | Purpose |
|---------------|---------|
| `app.py` | Main Streamlit application |
| `data/` | Inventory dataset |
| `utils/calculations.py` | Inventory calculations and business logic |
| `utils/ai_inventory_advisor.py` | Google Gemini AI integration |
| `requirements.txt` | Python dependencies |
| `.gitignore` | Files excluded from Git tracking |
| `.env` | Stores the Gemini API key securely |
| `README.md` | Project documentation |

---

# ⚙️ Installation & Setup

## 1. Clone the Repository

```bash
git clone https://github.com/gopichand-7/AI-Supply-Chain-Command-Center.git
```

## 2. Navigate to the Project

```bash
cd AI-Supply-Chain-Command-Center
```

## 3. Create a Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

## 4. Install Dependencies

```bash
pip install -r requirements.txt
```

## 5. Create a `.env` File

Create a file named `.env` in the project root.

```env
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
```

Generate your API key from **Google AI Studio**.

## 6. Run the Application

```bash
streamlit run app.py
```

Open your browser and navigate to:

```
http://localhost:8501
```

---

# ✨ Current Features

## 📊 Executive Inventory Dashboard

Provides an executive-level overview of inventory performance through interactive KPIs.

### Dashboard KPIs

- Total Inventory Value
- Inventory Health
- Low Stock Items
- Overstock Items

---

## 📈 Interactive Analytics

Interactive Plotly visualizations for:

- Category-wise Inventory Distribution
- Warehouse-wise Inventory Distribution

---

## 🤖 AI Inventory Advisor

Generate executive-level inventory recommendations using Google Gemini AI.

The AI analyzes:

- Inventory Health
- Low Stock Risks
- Overstock Risks
- Category Performance
- Warehouse Distribution

The generated report includes:

- Executive Summary
- Key Findings
- Risks
- Recommendations
- Priority Actions

---

## 📋 Inventory Dataset Viewer

Browse the inventory dataset through an interactive Streamlit table for quick analysis.

---

# 🎯 Future Enhancements

The long-term goal of this project is to evolve from an inventory dashboard into a complete AI-powered Supply Chain Decision Support System.

Future releases will introduce:

- 📦 Advanced Inventory Analytics
- 🤝 Supplier Performance Management
- 🛒 Procurement Analytics
- 🏭 Warehouse Operations Dashboard
- 🚚 Logistics & Transportation Analytics
- 📈 Demand Forecasting
- 🤖 Integrated AI Supply Chain Advisor
- 📄 Automated Executive Reports
- 📊 Interactive Business Intelligence Dashboards

The final objective (**v1.0**) is to provide a unified platform that helps supply chain professionals monitor operations, identify risks, optimize inventory, and support data-driven decision-making using Artificial Intelligence.

---

# 👨‍💻 Author

**Gopichand Kollapattu**

- GitHub: https://github.com/gopichand-7
---

# 📄 License

This project is licensed under the **MIT License**.
