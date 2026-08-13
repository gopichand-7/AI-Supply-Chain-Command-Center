import streamlit as st
import pandas as pd
import plotly.express as px

from io import BytesIO
from datetime import datetime
import html

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
    Table,
    TableStyle,
    KeepTogether,
)

from utils.calculations import (
    add_stock_status,
    calculate_kpis,
    get_top_critical_inventory,
    get_overstock_inventory,
    get_abc_inventory,
    get_category_summary,
    get_warehouse_summary,
    get_supplier_summary,
    get_supplier_management_summary,
    calculate_procurement_kpis,
    get_warehouse_logistics_summary,
    get_demand_forecast_summary,
)



from utils.ai_inventory_advisor import (
    generate_inventory_advice,
    generate_executive_supply_chain_summary,
)

# -----------------------------------
# Executive PDF Report Generator
# -----------------------------------

def create_executive_pdf(report_text, df, procurement_df):

    buffer = BytesIO()

    # ------------------------------
    # Palette (matches the sample PDF)
    # ------------------------------
    navy = colors.HexColor("#17324D")
    teal = colors.HexColor("#1F7A8C")
    gold = colors.HexColor("#D99A34")
    danger = colors.HexColor("#C0392B")
    info_blue = colors.HexColor("#2E70A0")
    light_blue = colors.HexColor("#EAF2F5")
    light_gray = colors.HexColor("#F5F7FA")
    dark_text = colors.HexColor("#263238")
    muted_text = colors.HexColor("#6B7280")
    border_gray = colors.HexColor("#CBD5E1")

    danger_hex, gold_hex, info_hex, teal_hex = "#C0392B", "#B5791F", "#2E70A0", "#1F7A8C"

    # ------------------------------
    # Footer drawn on every page
    # ------------------------------
    def footer(canvas_obj, doc_obj):
        canvas_obj.saveState()
        canvas_obj.setFont("Helvetica", 7.5)
        canvas_obj.setFillColor(muted_text)
        canvas_obj.drawString(42, 24, "AI Supply Chain Command Center \u2022 Executive Intelligence")
        canvas_obj.drawRightString(A4[0] - 42, 24, f"Page {doc_obj.page}")
        canvas_obj.restoreState()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=42,
        leftMargin=42,
        topMargin=40,
        bottomMargin=50,
        title="AI Executive Supply Chain Report",
        author="AI Supply Chain Command Center",
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ExecutiveTitle", parent=styles["Title"], fontName="Helvetica-Bold",
        fontSize=24, leading=30, textColor=navy, alignment=TA_CENTER, spaceAfter=12,
    )
    cover_subtitle_style = ParagraphStyle(
        "CoverSubtitle", parent=styles["Normal"], fontName="Helvetica",
        fontSize=11, leading=16, textColor=muted_text, alignment=TA_CENTER, spaceAfter=20,
    )
    section_style = ParagraphStyle(
        "SectionStyle", parent=styles["Heading2"], fontName="Helvetica-Bold",
        fontSize=15, leading=19, textColor=navy, spaceBefore=8, spaceAfter=10,
    )
    subheader_style = ParagraphStyle(
        "SubheaderStyle", parent=styles["Heading3"], fontName="Helvetica-Bold",
        fontSize=11.5, leading=15, textColor=navy, spaceBefore=10, spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "BodyStyle", parent=styles["BodyText"], fontName="Helvetica",
        fontSize=9.5, leading=14, textColor=dark_text, spaceAfter=7,
    )
    small_style = ParagraphStyle(
        "SmallStyle", parent=styles["Normal"], fontName="Helvetica",
        fontSize=8, leading=11, textColor=muted_text,
    )
    card_title_style = ParagraphStyle(
        "CardTitle", parent=styles["Normal"], fontName="Helvetica-Bold",
        fontSize=10, leading=13, textColor=navy, alignment=TA_CENTER,
    )
    card_body_style = ParagraphStyle(
        "CardBody", parent=styles["Normal"], fontName="Helvetica",
        fontSize=8, leading=11, textColor=dark_text, alignment=TA_CENTER,
    )
    kpi_value_style = ParagraphStyle(
        "KpiValue", parent=styles["Normal"], fontName="Helvetica-Bold",
        fontSize=15, leading=18, textColor=navy, alignment=TA_CENTER,
    )
    kpi_label_style = ParagraphStyle(
        "KpiLabel", parent=styles["Normal"], fontName="Helvetica",
        fontSize=8, leading=10, textColor=muted_text, alignment=TA_CENTER,
    )
    table_header_style = ParagraphStyle(
        "TableHeader", parent=styles["Normal"], fontName="Helvetica-Bold",
        fontSize=8.5, leading=11, textColor=colors.white,
    )
    table_cell_style = ParagraphStyle(
        "TableCell", parent=styles["Normal"], fontName="Helvetica",
        fontSize=8.5, leading=11, textColor=dark_text,
    )
    reco_title_style = ParagraphStyle(
        "RecoTitle", parent=styles["Normal"], fontName="Helvetica-Bold",
        fontSize=10, leading=13, textColor=navy,
    )

    page_width = A4[0] - 84  # usable width inside margins

    # ------------------------------
    # Small helpers
    # ------------------------------
    def money(v):
        try:
            v = float(v)
        except (TypeError, ValueError):
            return "$0.00"
        if abs(v) >= 1_000_000:
            return f"${v/1_000_000:.2f}M"
        return f"${v:,.2f}"

    def build_kpi_grid(items, cols=3):
        """items: list of (label, value) tuples."""
        rows = []
        for i in range(0, len(items), cols):
            chunk = items[i:i + cols]
            value_row = [Paragraph(v, kpi_value_style) for _, v in chunk]
            label_row = [Paragraph(l, kpi_label_style) for l, _ in chunk]
            while len(value_row) < cols:
                value_row.append("")
                label_row.append("")
            rows.append(value_row)
            rows.append(label_row)
        col_w = page_width / cols
        t = Table(rows, colWidths=[col_w] * cols)
        cmds = [
            ("BOX", (0, 0), (-1, -1), 0.6, border_gray),
            ("INNERGRID", (0, 0), (-1, -1), 0.4, border_gray),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ]
        for r in range(0, len(rows), 2):
            cmds.append(("BACKGROUND", (0, r), (-1, r + 1), light_blue if (r // 2) % 2 == 0 else light_gray))
        t.setStyle(TableStyle(cmds))
        return t

    def build_data_table(headers, rows, col_widths):
        header_cells = [Paragraph(h, table_header_style) for h in headers]
        data = [header_cells]
        for row in rows:
            data.append([c if isinstance(c, Paragraph) else Paragraph(str(c), table_cell_style) for c in row])
        t = Table(data, colWidths=col_widths, repeatRows=1)
        cmds = [
            ("BACKGROUND", (0, 0), (-1, 0), navy),
            ("BOX", (0, 0), (-1, -1), 0.6, border_gray),
            ("INNERGRID", (0, 0), (-1, -1), 0.4, border_gray),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]
        for i in range(1, len(data)):
            if i % 2 == 0:
                cmds.append(("BACKGROUND", (0, i), (-1, i), light_gray))
        t.setStyle(TableStyle(cmds))
        return t

    def priority_label(p):
        color_hex = {"CRITICAL": danger_hex, "HIGH": gold_hex, "MEDIUM": info_hex}.get(p, "#263238")
        return Paragraph(f'<font color="{color_hex}"><b>{p}</b></font>', table_cell_style)

    def three_card_row(titles, bodies):
        data = [
            [Paragraph(f"<b>{t}</b>", card_title_style) for t in titles],
            [Paragraph(b, card_body_style) for b in bodies],
        ]
        t = Table(data, colWidths=[page_width / 3] * 3)
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), navy),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("BACKGROUND", (0, 1), (-1, 1), light_gray),
            ("BOX", (0, 0), (-1, -1), 0.6, border_gray),
            ("INNERGRID", (0, 0), (-1, -1), 0.4, border_gray),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 12),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ]))
        return t

    story = []

    # =====================================================================
    # PAGE 1 — COVER
    # =====================================================================
    story.append(Spacer(1, 0.55 * inch))
    story.append(Paragraph(
        "AI SUPPLY CHAIN COMMAND CENTER",
        ParagraphStyle("BrandStyle", parent=styles["Normal"], fontName="Helvetica-Bold",
                        fontSize=10, textColor=teal, alignment=TA_CENTER, spaceAfter=18),
    ))
    story.append(Paragraph("Executive Supply Chain Report", title_style))
    story.append(Paragraph("Inventory \u2022 Procurement \u2022 Suppliers \u2022 Warehouses \u2022 Demand", cover_subtitle_style))
    story.append(Spacer(1, 0.35 * inch))
    story.append(three_card_row(
        ["STABILIZE", "PROTECT", "OPTIMIZE"],
        [
            "Address critical stock exposure and inventory risk.",
            "Improve procurement execution and supplier reliability.",
            "Reduce excess inventory and improve working capital.",
        ],
    ))
    story.append(Spacer(1, 0.55 * inch))
    generated_date = datetime.now().strftime("%d %B %Y")
    story.append(Paragraph(f"Generated: {generated_date}", small_style))
    story.append(Paragraph("Internal Business Use \u2022 AI-Generated Management Analysis", small_style))
    story.append(PageBreak())

    # =====================================================================
    # DATA PREP (all computed from the live dataframes)
    # =====================================================================
    total_skus = len(df)
    total_inventory_value = float(df["InventoryValueUSD"].sum()) if total_skus else 0.0

    if "DaysOfInventory" in df.columns:
        df["_Coverage"] = df["DaysOfInventory"]
    else:
        df["_Coverage"] = df["CurrentStock"] / df["AvgDailyUsage"].replace(0, pd.NA)

    out_of_stock = df[df["CurrentStock"] <= 0]
    low_stock = df[(df["CurrentStock"] > 0) & (df["CurrentStock"] <= df["ReorderLevel"])]
    overstock = df[df["CurrentStock"] > df["MaxStockLevel"]]
    healthy_count = max(total_skus - len(out_of_stock) - len(low_stock) - len(overstock), 0)
    healthy_pct = (healthy_count / total_skus * 100) if total_skus else 0

    total_pos = len(procurement_df)
    delayed_pos = procurement_df[procurement_df["OrderStatus"].astype(str).str.contains("Delay", case=False, na=False)]
    pending_pos = procurement_df[procurement_df["PaymentStatus"].astype(str).str.contains("Pending", case=False, na=False)]
    delayed_pct = (len(delayed_pos) / total_pos * 100) if total_pos else 0
    pending_pct = (len(pending_pos) / total_pos * 100) if total_pos else 0

    # =====================================================================
    # PAGE 2 — 01 EXECUTIVE OVERVIEW
    # =====================================================================
    story.append(Paragraph("01 EXECUTIVE OVERVIEW", section_style))
    story.append(Paragraph("Executive Summary", subheader_style))

    notes = []
    if len(out_of_stock) > 0:
        notes.append(f"{len(out_of_stock)} SKU(s) completely out of stock")
    if len(low_stock) > 0:
        notes.append(f"{len(low_stock)} item(s) with low coverage")
    if len(overstock) > 0:
        notes.append(f"{len(overstock)} item(s) in overstock")
    stock_note = ("Stock conditions include " + ", ".join(notes) + ". ") if notes else "Stock conditions are within healthy thresholds. "

    summary_text = (
        f"The business holds {money(total_inventory_value)} in inventory value across {total_skus} SKUs. "
        f"{stock_note}"
        f"Procurement performance shows {delayed_pct:.1f}% of purchase orders delayed "
        f"and {pending_pct:.1f}% pending payment."
    )
    story.append(Paragraph(summary_text, body_style))
    story.append(Spacer(1, 6))

    kpi_items = [
        ("Total SKUs", f"{total_skus}"),
        ("Inventory Value", money(total_inventory_value)),
        ("Healthy Items", f"{healthy_count} ({healthy_pct:.0f}%)"),
        ("Low Stock", f"{len(low_stock)}"),
        ("Overstock", f"{len(overstock)}"),
        ("Delayed POs", f"{len(delayed_pos)}"),
    ]
    story.append(build_kpi_grid(kpi_items, cols=3))
    story.append(Spacer(1, 16))

    story.append(Paragraph("Management Attention Path", subheader_style))
    story.append(three_card_row(
        ["01 STABILIZE", "02 PROTECT", "03 OPTIMIZE"],
        [
            "Resolve stock-out and low-stock exposure.",
            "Recover procurement execution and payment flow.",
            "Reduce excess stock and improve policy controls.",
        ],
    ))

    # =====================================================================
    # PAGE 3 — 02 CRITICAL RISKS & FINANCIAL EXPOSURE
    # =====================================================================
    story.append(Spacer(1, 20))
    story.append(KeepTogether([
        Paragraph("02 CRITICAL RISKS & FINANCIAL EXPOSURE", section_style),
        Paragraph("Critical Stock Exposure", subheader_style),
    ]))

    critical = pd.concat([out_of_stock, low_stock]).drop_duplicates(subset="SKU")
    critical = critical.sort_values("_Coverage", ascending=True).head(6)

    if len(critical) > 0:
        rows = []
        for _, r in critical.iterrows():
            coverage = r["_Coverage"]
            coverage_txt = "0.0 days" if pd.isna(coverage) else f"{coverage:.1f} days"
            if r["CurrentStock"] <= 0:
                pr = "CRITICAL"
            elif not pd.isna(coverage) and coverage < 3:
                pr = "HIGH"
            else:
                pr = "MEDIUM"
            rows.append([r["SKU"], r["ItemName"], int(r["CurrentStock"]), coverage_txt, priority_label(pr)])
        story.append(build_data_table(
            ["SKU", "Item", "Current Stock", "Coverage", "Priority"],
            rows,
            [65, 190, 75, 75, page_width - 65 - 190 - 75 - 75],
        ))
    else:
        story.append(Paragraph("No SKUs currently below reorder level.", body_style))

    story.append(Spacer(1, 14))
    story.append(Paragraph("Top Excess Inventory by Value", subheader_style))

    if len(overstock) > 0:
        exc = overstock.copy()
        exc["ExcessUnits"] = exc["CurrentStock"] - exc["MaxStockLevel"]
        exc["ExcessValue"] = exc["ExcessUnits"] * exc["UnitCostUSD"]
        exc = exc.sort_values("ExcessValue", ascending=False).head(5)
        rows = [[r["SKU"], r["ItemName"], int(r["ExcessUnits"]), money(r["ExcessValue"])] for _, r in exc.iterrows()]
        story.append(build_data_table(
            ["SKU", "Item", "Excess Units", "Excess Value"],
            rows,
            [65, 220, 100, page_width - 65 - 220 - 100],
        ))
    else:
        story.append(Paragraph("No SKUs currently exceed maximum stock level.", body_style))

    story.append(Spacer(1, 10))
    why_text = (
        f"Stock continuity: {len(out_of_stock)} SKU(s) out of stock and {len(low_stock)} with low coverage. "
        f"Working capital: {len(overstock)} overstock item(s) should be reviewed before additional replenishment."
    )
    story.append(Paragraph("Why This Matters", subheader_style))
    story.append(Paragraph(why_text, body_style))

    # =====================================================================
    # PAGE 4 — 03 PROCUREMENT & SUPPLIER PERFORMANCE
    # =====================================================================
    story.append(Spacer(1, 20))
    story.append(KeepTogether([
        Paragraph("03 PROCUREMENT & SUPPLIER PERFORMANCE", section_style),
        Paragraph("Procurement Snapshot", subheader_style),
    ]))
    story.append(Paragraph(
        f"{delayed_pct:.1f}% of purchase orders are delayed and {pending_pct:.1f}% are in pending-payment status. "
        "This is a material execution risk that can affect supply continuity.",
        body_style,
    ))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Supplier Performance Snapshot", subheader_style))

    supplier_inv = df.groupby("Supplier").agg(
        SKUs=("SKU", "nunique"), InventoryValue=("InventoryValueUSD", "sum")
    ).reset_index()
    po_counts = procurement_df.groupby("Supplier").agg(POs=("PO_ID", "count")).reset_index()
    delayed_counts = delayed_pos.groupby("Supplier").agg(Delayed=("PO_ID", "count")).reset_index()

    supplier_perf = supplier_inv.merge(po_counts, on="Supplier", how="left").merge(delayed_counts, on="Supplier", how="left")
    supplier_perf[["POs", "Delayed"]] = supplier_perf[["POs", "Delayed"]].fillna(0).astype(int)
    supplier_perf = supplier_perf.sort_values("Delayed", ascending=False).head(6)

    rows = [
        [r["Supplier"], int(r["SKUs"]), money(r["InventoryValue"]), int(r["POs"]), int(r["Delayed"])]
        for _, r in supplier_perf.iterrows()
    ]
    story.append(build_data_table(
        ["Supplier", "SKUs", "Inventory Value", "POs", "Delayed"],
        rows,
        [150, 55, 130, 65, page_width - 150 - 55 - 130 - 65],
    ))

    # =====================================================================
    # PAGE 5 — 04 WAREHOUSE & DEMAND INTELLIGENCE
    # =====================================================================
    story.append(Spacer(1, 20))
    story.append(KeepTogether([
        Paragraph("04 WAREHOUSE & DEMAND INTELLIGENCE", section_style),
        Paragraph("Network View", subheader_style),
    ]))

    wh = df.groupby("Warehouse").agg(
        SKUs=("SKU", "nunique"),
        InventoryValue=("InventoryValueUSD", "sum"),
        AvgDays=("_Coverage", "mean"),
    ).reset_index()
    low_by_wh = low_stock.groupby("Warehouse").size().rename("Low")
    over_by_wh = overstock.groupby("Warehouse").size().rename("Overstock")
    wh = wh.merge(low_by_wh, on="Warehouse", how="left").merge(over_by_wh, on="Warehouse", how="left")
    wh[["Low", "Overstock"]] = wh[["Low", "Overstock"]].fillna(0).astype(int)
    wh = wh.sort_values("InventoryValue", ascending=False)

    rows = [
        [r["Warehouse"], int(r["SKUs"]), money(r["InventoryValue"]),
         f"{r['AvgDays']:.1f}" if not pd.isna(r["AvgDays"]) else "-", int(r["Low"]), int(r["Overstock"])]
        for _, r in wh.iterrows()
    ]
    story.append(build_data_table(
        ["Warehouse", "SKUs", "Inventory Value", "Avg Days", "Low", "Overstock"],
        rows,
        [130, 50, 120, 65, 45, page_width - 130 - 50 - 120 - 65 - 45],
    ))
    story.append(Spacer(1, 12))

    total_daily_demand = float(df["AvgDailyUsage"].sum())
    avg_daily_per_sku = float(df["AvgDailyUsage"].mean()) if total_skus else 0.0
    story.append(Paragraph("Demand Insight", subheader_style))
    story.append(Paragraph(
        f"Total daily demand is {total_daily_demand:,.1f} units, averaging {avg_daily_per_sku:.1f} units per SKU. "
        "Warehouse and category coverage vary enough to support targeted replenishment policies rather than "
        "one uniform stock rule.",
        body_style,
    ))

    # =====================================================================
    # PAGE 6 — 05 STRATEGIC RECOMMENDATIONS + 06 PRIORITY ACTION PLAN
    # =====================================================================
    story.append(Spacer(1, 20))
    story.append(Paragraph("05 STRATEGIC RECOMMENDATIONS", section_style))

    top_delay_supplier = supplier_perf.iloc[0]["Supplier"] if len(supplier_perf) and supplier_perf.iloc[0]["Delayed"] > 0 else None
    wh_sorted_risk = wh.copy()
    wh_sorted_risk["RiskCount"] = wh_sorted_risk["Low"] + wh_sorted_risk["Overstock"]
    top_risk_wh = wh_sorted_risk.sort_values("RiskCount", ascending=False).iloc[0]["Warehouse"] if len(wh_sorted_risk) else None

    recos = [
        ("01 Stabilize Critical Stock", "Immediately expedite or reorder the stock-out and next lowest-coverage items."),
        ("02 Audit Pending Payments", f"Investigate {len(pending_pos)} pending-payment orders and their effect on supplier execution."),
        ("03 Reduce High-Value Overstock", "Review replenishment triggers and maximum stock limits for major excess items."),
        ("04 Engage Delayed Suppliers", f"Conduct formal performance reviews with {top_delay_supplier or 'the suppliers'} driving the largest delay counts."),
        ("05 Rebalance Warehouse Parameters", f"Review {top_risk_wh or 'top-risk warehouses'} for stock balancing and item-level safety stock settings."),
    ]
    for t, b in recos:
        story.append(KeepTogether([
            Paragraph(t, reco_title_style),
            Paragraph(b, body_style),
        ]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("06 PRIORITY ACTION PLAN", section_style))
    action_rows = [
        ["P1", "Resolve stock-out and critical low-stock exposure", "0\u20137 days"],
        ["P2", "Review delayed POs and pending payments", "0\u20137 days"],
        ["P3", "Review replenishment for major overstock items", "7\u201330 days"],
        ["P4", "Conduct supplier performance reviews", "7\u201330 days"],
        ["P5", "Revisit inventory and warehouse parameters", "30+ days"],
    ]
    story.append(build_data_table(
        ["Priority", "Action", "Time Horizon"],
        action_rows,
        [55, page_width - 55 - 110, 110],
    ))

    # =====================================================================
    # 07 EXECUTIVE CONCLUSION
    # =====================================================================
    story.append(Spacer(1, 20))
    story.append(Paragraph("07 EXECUTIVE CONCLUSION", section_style))

    attention_needed = len(out_of_stock) > 0 or delayed_pct > 30 or len(overstock) > total_skus * 0.15
    assessment = "attention required" if attention_needed else "stable"
    story.append(Paragraph(f"<b>Overall assessment: {assessment}.</b>", body_style))
    story.append(Paragraph(
        "Management should first stabilize critical supply, then resolve procurement friction, and finally "
        "optimize inventory policies to reduce recurrence. The combination of stock-out risk, purchase order "
        "delays, and excess inventory makes sequencing of action important.",
        body_style,
    ))
    story.append(Spacer(1, 14))
    story.append(Paragraph("Report Information", subheader_style))
    story.append(Paragraph(
        "AI Supply Chain Command Center \u2022 Inventory, Procurement, Suppliers, Warehouses and Demand \u2022 "
        "Data-backed metrics with AI-assisted executive interpretation \u2022 "
        f"Generated {datetime.now().strftime('%d %B %Y, %I:%M %p')}",
        small_style,
    ))

    doc.build(story, onFirstPage=footer, onLaterPages=footer)

    buffer.seek(0)

    return buffer.getvalue()

# -----------------------------------
# Page Configuration
# -----------------------------------

st.set_page_config(
    page_title="AI Supply Chain Command Center",
    page_icon="📦",
    layout="wide"
)

# Hide the default "Limit 200MB per file • CSV, XLSX" helper text under file uploaders
st.markdown(
    """
    <style>
    [data-testid="stFileUploaderDropzoneInstructions"] small {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------
# Title
# -----------------------------------

st.title("📦 AI Supply Chain Command Center")
st.markdown("### Executive Dashboard (v1.0)")

st.divider()

# -----------------------------------
# Dataset Manager
# -----------------------------------

st.subheader("📂 Dataset Manager")

data_source = st.radio(
    "Choose Dataset",
    (
        "📊 Use Sample Dataset",
        "📤 Upload Your Inventory and Procurement Files",
    ),
)

if data_source == "📊 Use Sample Dataset":

    st.success(
    "Explore the dashboard using the built-in sample datasets."
)

    col1, col2 = st.columns(2)

    with col1:
        with open("data/inventory_data.csv", "rb") as file:
            st.download_button(
                "⬇ Download Sample Inventory Dataset",
                file,
                file_name="inventory_data.csv",
                mime="text/csv",
                use_container_width=True,
            )

    with col2:
        with open("data/procurement_data.csv", "rb") as file:
            st.download_button(
                "⬇ Download Sample Procurement Dataset",
                file,
                file_name="procurement_data.csv",
                mime="text/csv",
                use_container_width=True,
            )

else:

    st.info(
        """
Upload **both** datasets to generate dashboards and AI insights.

Supported Formats

• CSV (.csv)

• Excel (.xlsx)

Google Sheets:
Export as CSV or Excel before uploading.
"""
    )

    col1, col2 = st.columns(2)

    with col1:

        inventory_file = st.file_uploader(
            "📦 Inventory Dataset",
            type=["csv", "xlsx"],
        )

    with col2:

        procurement_file = st.file_uploader(
            "🛒 Procurement Dataset",
            type=["csv", "xlsx"],
        )

    with st.expander("📋 Required Dataset Columns"):

        st.markdown("### Inventory Dataset")

        st.code("""
SKU
ItemName
Category
Supplier
Warehouse
UnitCostUSD
CurrentStock
SafetyStock
ReorderLevel
MaxStockLevel
AvgDailyUsage
DaysOfInventory
InventoryValueUSD
LastRestockDate
""")

        st.markdown("### Procurement Dataset")

        st.code("""
PO_ID
OrderDate
ExpectedDelivery
ActualDelivery
SKU
ItemName
Supplier
Category
Warehouse
OrderQuantity
UnitCostUSD
TotalOrderValueUSD
LeadTimeDays
DeliveryDelayDays
OrderStatus
PaymentStatus
Buyer
""")

st.divider()

# -----------------------------------
# Load Data
# -----------------------------------

try:

    if data_source == "📊 Use Sample Dataset":

        df = pd.read_csv("data/inventory_data.csv")
        trend_df = pd.DataFrame()
        procurement_df = pd.read_csv("data/procurement_data.csv")

    else:

        if inventory_file is None or procurement_file is None:

            st.warning(
                "Please upload both Inventory and Procurement datasets."
            )

            st.stop()

        if inventory_file.name.endswith(".csv"):
            df = pd.read_csv(inventory_file)
        else:
            df = pd.read_excel(inventory_file)

        if procurement_file.name.endswith(".csv"):
            procurement_df = pd.read_csv(procurement_file)
        else:
            procurement_df = pd.read_excel(procurement_file)

        trend_df = pd.DataFrame()

        st.success(
            f"✅ Inventory Dataset Loaded ({len(df)} records)"
        )

        st.success(
            f"✅ Procurement Dataset Loaded ({len(procurement_df)} records)"
        )

    if not trend_df.empty:
        trend_df["Date"] = pd.to_datetime(
            trend_df["Date"]
        )

    df = add_stock_status(df)

    kpis = calculate_kpis(df)

    procurement_kpis = calculate_procurement_kpis(
        procurement_df
    )

    warehouse_logistics = get_warehouse_logistics_summary(
        df,
        procurement_df,
    )

    demand_summary = get_demand_forecast_summary(
        df
    )

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
# AI Executive Supply Chain Command Center
# -----------------------------------

st.subheader("🧠 AI Executive Supply Chain Command Center")

st.write(
    "Generate an executive-level supply chain report using Google Gemini AI."
)

# -----------------------------------
# Initialize Executive Report
# -----------------------------------

if "executive_report" not in st.session_state:
    st.session_state.executive_report = None


# -----------------------------------
# Generate Executive Report
# -----------------------------------

if st.button("Generate Executive AI Report"):

    with st.spinner("Generating executive report..."):

        try:

            st.session_state.executive_report = (
                generate_executive_supply_chain_summary(
                    df,
                    procurement_df,
                )
            )

            st.success("Executive report generated successfully.")

        except Exception as e:

            st.error(f"AI Report Failed: {e}")


# -----------------------------------
# Display Executive Report and Download Options
# -----------------------------------

if st.session_state.executive_report:

    st.markdown(st.session_state.executive_report.replace("$", "\\$"))

    st.markdown("### 📥 Download Report")

    col1, col2 = st.columns(2)

    # -----------------------------------
    # Markdown Download
    # -----------------------------------

    with col1:

        st.download_button(
            label="⬇️ Download Markdown",
            data=st.session_state.executive_report,
            file_name="executive_supply_chain_report.md",
            mime="text/markdown",
            use_container_width=True,
        )


    # -----------------------------------
    # Professional PDF Download
    # -----------------------------------

    with col2:

        pdf_data = create_executive_pdf(
        st.session_state.executive_report,
        df,
        procurement_df,
)

        st.download_button(
            label="📄 Download Professional PDF",
            data=pdf_data,
            file_name="AI_Executive_Supply_Chain_Report.pdf",
            mime="application/pdf",
            use_container_width=True,
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

            st.markdown(advice.replace("$", "\\$"))

        except Exception as e:

            st.error(f"AI Analysis Failed: {e}")

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

st.divider()

# -----------------------------------
# Supplier Performance Dashboard
# -----------------------------------

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

st.divider()

# -----------------------------------
# Supplier Management Dashboard
# -----------------------------------

st.subheader("🤝 Supplier Management Dashboard")

supplier_mgmt = get_supplier_management_summary(df)

# KPI Cards

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "🏢 Total Suppliers",
        len(supplier_mgmt)
    )

with col2:
    st.metric(
        "📦 Total SKUs",
        supplier_mgmt["Total_SKUs"].sum()
    )

with col3:
    st.metric(
        "💰 Total Inventory Value",
        f"${supplier_mgmt['Inventory_Value_USD'].sum():,.2f}"
    )

with col4:
    st.metric(
        "📅 Latest Restock",
        supplier_mgmt["Last_Restock_Date"].max()
    )

st.divider()

col1, col2 = st.columns(2)

with col1:

    fig = px.bar(
        supplier_mgmt,
        x="Supplier",
        y="Inventory_Value_USD",
        color="Supplier",
        text_auto=".2s",
        title="Inventory Value by Supplier"
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        key="supplier_management_bar"
    )

with col2:

    fig = px.pie(
        supplier_mgmt,
        names="Supplier",
        values="Inventory_Value_USD",
        title="Supplier Inventory Distribution"
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        key="supplier_management_pie"
    )

st.divider()

st.dataframe(
    supplier_mgmt,
    use_container_width=True,
    hide_index=True,
)

st.divider()

# -----------------------------------
# Procurement Analytics Dashboard
# -----------------------------------

st.subheader("🛒 Procurement Analytics Dashboard")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "📄 Purchase Orders",
        procurement_kpis["Total Purchase Orders"]
    )

with col2:
    st.metric(
        "💰 Procurement Spend",
        f"${procurement_kpis['Total Procurement Spend']:,.2f}"
    )

with col3:
    st.metric(
        "📦 Avg Order Value",
        f"${procurement_kpis['Average Order Value']:,.2f}"
    )

with col4:
    st.metric(
        "🚚 Avg Lead Time",
        f"{procurement_kpis['Average Lead Time']:.1f} Days"
    )

st.divider()

col1, col2 = st.columns(2)

with col1:

    supplier_spend = (
        procurement_df.groupby("Supplier")["TotalOrderValueUSD"]
        .sum()
        .reset_index()
    )

    fig = px.bar(
        supplier_spend,
        x="Supplier",
        y="TotalOrderValueUSD",
        color="Supplier",
        text_auto=".2s",
        title="Procurement Spend by Supplier"
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        key="procurement_supplier_bar"
    )

with col2:

    category_spend = (
        procurement_df.groupby("Category")["TotalOrderValueUSD"]
        .sum()
        .reset_index()
    )

    fig = px.pie(
        category_spend,
        names="Category",
        values="TotalOrderValueUSD",
        title="Procurement Spend by Category"
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        key="procurement_category_pie"
    )

st.divider()

st.subheader("📋 Procurement Orders")

st.dataframe(
    procurement_df,
    use_container_width=True,
    hide_index=True,
)

st.divider()

# -----------------------------------
# Warehouse & Logistics Dashboard
# -----------------------------------

st.subheader("🏭 Warehouse & Logistics Dashboard")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "🏭 Total Warehouses",
        len(warehouse_logistics)
    )

with col2:
    st.metric(
        "💰 Inventory Value",
        f"${warehouse_logistics['Inventory_Value_USD'].sum():,.2f}"
    )

with col3:
    st.metric(
        "🚚 Procurement Spend",
        f"${warehouse_logistics['Procurement_Spend'].sum():,.2f}"
    )

with col4:
    st.metric(
        "⏱ Avg Lead Time",
        f"{warehouse_logistics['Average_Lead_Time'].mean():.1f} Days"
    )

st.divider()

col1, col2 = st.columns(2)

with col1:

    fig = px.bar(
        warehouse_logistics,
        x="Warehouse",
        y="Inventory_Value_USD",
        color="Warehouse",
        text_auto=".2s",
        title="Inventory Value by Warehouse"
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        key="warehouse_logistics_bar"
    )

with col2:

    fig = px.pie(
        warehouse_logistics,
        names="Warehouse",
        values="Procurement_Spend",
        title="Procurement Spend by Warehouse"
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        key="warehouse_logistics_pie"
    )

st.divider()

st.subheader("📋 Warehouse Logistics Summary")

st.dataframe(
    warehouse_logistics,
    use_container_width=True,
    hide_index=True,
)

st.divider()

# -----------------------------------
# Demand Forecasting Dashboard
# -----------------------------------

st.subheader("📈 Demand Forecasting Dashboard")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "📦 Categories",
        len(demand_summary)
    )

with col2:
    st.metric(
        "📈 Total Daily Demand",
        f"{demand_summary['Total_Daily_Demand'].sum():.1f}"
    )

with col3:
    st.metric(
        "📊 Avg Daily Demand",
        f"{demand_summary['Average_Daily_Demand'].mean():.1f}"
    )

with col4:
    st.metric(
        "💰 Inventory Value",
        f"${demand_summary['Inventory_Value_USD'].sum():,.2f}"
    )

st.divider()

col1, col2 = st.columns(2)

with col1:

    fig = px.bar(
        demand_summary,
        x="Category",
        y="Total_Daily_Demand",
        color="Category",
        text_auto=".2s",
        title="Daily Demand by Category"
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        key="demand_bar"
    )

with col2:

    fig = px.pie(
        demand_summary,
        names="Category",
        values="Inventory_Value_USD",
        title="Inventory Value by Category"
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        key="demand_pie"
    )

st.divider()

st.subheader("📋 Demand Forecast Summary")

st.dataframe(
    demand_summary,
    use_container_width=True,
    hide_index=True,
)

st.divider()

# -----------------------------------
# Inventory Dataset
# -----------------------------------

st.subheader("📋 Inventory Dataset")

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True,
)