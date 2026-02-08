#!/usr/bin/env python
# coding: utf-8

# In[ ]:

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import os

from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
)
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

# =========================
# STREAMLIT CONFIG
# =========================
st.set_page_config(page_title="Tạo nhanh báo cáo tài chính", layout="wide")
st.title("📊 TẠO NHANH BÁO CÁO TÀI CHÍNH")

# =========================
# UPLOAD DATA
# =========================
st.header("1️⃣ Upload dữ liệu tài chính")

data_file = st.file_uploader(
    "File CSV / Excel bao gồm trường data (Date, Revenue, COGS, Operating_Expense, Financial_Expense, Tax, "
    "Short_Term_Debt, Long_Term_Debt, Total_Assets, Equity, Accounts_Receivable, Inventory)",
    type=["csv", "xlsx"]
)

if data_file:
    df = pd.read_csv(data_file) if data_file.name.endswith(".csv") else pd.read_excel(data_file)
    df["Date"] = pd.to_datetime(df["Date"])

    # =========================
    # INCOME STATEMENT
    # =========================
    df["Gross_Profit"] = df["Revenue"] - df["COGS"]
    df["Operating_Profit"] = df["Gross_Profit"] - df["Operating_Expense"]
    df["EBT"] = df["Operating_Profit"] - df["Financial_Expense"]
    df["Net_Profit"] = df["EBT"] - df["Tax"]

    df["Gross_Margin"] = df["Gross_Profit"] / df["Revenue"]
    df["Operating_Margin"] = df["Operating_Profit"] / df["Revenue"]
    df["Net_Margin"] = df["Net_Profit"] / df["Revenue"]

    # =========================
    # BALANCE SHEET
    # =========================
    df["Total_Debt"] = df.get("Short_Term_Debt", 0) + df.get("Long_Term_Debt", 0)

    # =========================
    # FINANCIAL RATIOS
    # =========================
    ratios = {
        "Current Ratio": (df["Total_Assets"] / df["Short_Term_Debt"]).mean() if "Short_Term_Debt" in df else np.nan,
        "Debt to Equity": (df["Total_Debt"] / df["Equity"]).mean() if "Equity" in df else np.nan,
        "Debt to Asset": (df["Total_Debt"] / df["Total_Assets"]).mean(),
        "ROA": (df["Net_Profit"] / df["Total_Assets"]).mean(),
        "ROE": (df["Net_Profit"] / df["Equity"]).mean() if "Equity" in df else np.nan,
        "Asset Turnover": (df["Revenue"] / df["Total_Assets"]).mean(),
        "Receivable Turnover": (df["Revenue"] / df["Accounts_Receivable"]).mean() if "Accounts_Receivable" in df else np.nan,
        "Inventory Turnover": (df["COGS"] / df["Inventory"]).mean() if "Inventory" in df else np.nan,
    }

    ratio_df = pd.DataFrame({
        "Chỉ tiêu": ratios.keys(),
        "Giá trị": ratios.values()
    })

    st.subheader("📄 Dữ liệu sau xử lý")
    st.dataframe(df, use_container_width=True)

    # KPI ACTUAL DICTIONARY
    # =========================
    kpi_actual = {}

    # KPI mức độ (lấy kỳ cuối)
    for col in df.columns:
        if col not in ["Date"] and np.issubdtype(df[col].dtype, np.number):
            kpi_actual[col] = df[col].iloc[-1]

    # KPI là ratios
    for k, v in ratios.items():
        # Chuẩn hoá tên cho giống file target
        kpi_actual[k.replace(" ", "_")] = v

    # =========================
    # KPI SUMMARY
    # =========================
    st.header("2️⃣ Tổng hợp KPI")

    kpi_cols = [
        "Revenue", "Gross_Profit", "Operating_Profit", "Net_Profit",
        "Total_Assets", "Total_Debt", "Equity",
        "Gross_Margin", "Net_Margin"
    ]

    kpi_summary = []
    for k in kpi_cols:
        if k in df:
            kpi_summary.append({
                "KPI": k,
                "Tổng": df[k].sum() if "Margin" not in k else np.nan,
                "Trung bình": df[k].mean(),
                "Max": df[k].max(),
                "Min": df[k].min()
            })

    kpi_df = pd.DataFrame(kpi_summary)
    st.table(kpi_df)

    st.subheader("📊 Tỷ số tài chính")
    st.table(ratio_df)

    # =========================
    # VISUALIZATION
    # =========================
    def draw_gauge(value, title, path):
        fig, ax = plt.subplots(figsize=(3,3))
        ax.axis('off')

        value = min(max(value, 0), 150)

        wedges, _ = ax.pie(
            [value, 100 - value],
            startangle=180,
            colors=["#4CAF50" if value >= 100 else "#FFC107", "#EEEEEE"],
            wedgeprops={'width': 0.3},
            counterclock=False
        )

        ax.text(0, -0.1, f"{value:.1f}%", ha='center', va='center', fontsize=14, fontweight='bold')
        ax.text(0, -0.35, title, ha='center', va='center', fontsize=9)

        plt.savefig(path, dpi=150, bbox_inches="tight")
        plt.close()


    st.header("3️⃣ Biểu đồ tài chính")

    fig1, ax1 = plt.subplots(figsize=(8,4))
    ax1.plot(df["Date"], df["Revenue"], label="Revenue")
    ax1.plot(df["Date"], df["Net_Profit"], label="Net Profit")
    ax1.legend()
    ax1.set_title("Biểu đồ doanh thu và lợi nhuận ròng")
    st.pyplot(fig1)

    chart_path = "chart_profit.png"
    fig1.savefig(chart_path, dpi=150)
    plt.close()

    fig2, ax2 = plt.subplots(figsize=(8,4))
    ax2.stackplot(
        df["Date"],
        df["COGS"],
        df["Operating_Expense"],
        df["Financial_Expense"],
        labels=["COGS", "Operating Expense", "Financial Expense"]
    )
    ax2.legend(loc="upper left")
    ax2.set_title("Cơ cấu chi phí theo thời gian")
    st.pyplot(fig2)

    chart_cost_path = "chart_cost_structure.png"
    fig2.savefig(chart_cost_path, dpi=150)
    plt.close()

    fig3, ax3 = plt.subplots(figsize=(8,4))
    ax3.plot(df["Date"], df["Gross_Margin"] * 100, label="Gross Margin (%)")
    ax3.plot(df["Date"], df["Net_Margin"] * 100, label="Net Margin (%)")
    ax3.legend()
    ax3.set_title("Biên lợi nhuận theo thời gian")
    st.pyplot(fig3)

    chart_margin_path = "chart_margin.png"
    fig3.savefig(chart_margin_path, dpi=150)
    plt.close()

    if "Equity" in df.columns:
        fig4, ax4 = plt.subplots(figsize=(8,4))
        ax4.plot(df["Date"], df["Total_Debt"], label="Total Debt")
        ax4.plot(df["Date"], df["Equity"], label="Equity")
        ax4.legend()
        ax4.set_title("Cơ cấu nguồn vốn")
        st.pyplot(fig4)

        chart_capital_path = "chart_capital_structure.png"
        fig4.savefig(chart_capital_path, dpi=150)
        plt.close()


# =========================
    # KPI TARGET COMPARISON – FULL AUTO
    # =========================
    st.header("4️⃣ So sánh với chỉ tiêu mục tiêu")

    target_file = st.file_uploader(
        "Upload file KPI mục tiêu (1 dòng – nhiều cột)",
        type=["csv", "xlsx"]
    )

    compare_df = None

    if target_file:
        df_target = (
            pd.read_csv(target_file)
            if target_file.name.endswith(".csv")
            else pd.read_excel(target_file)
        )

        results = []

        for kpi in df_target.columns:
            target_value = df_target[kpi].iloc[0]

            if kpi in kpi_actual:
                actual_value = kpi_actual[kpi]
                pct = actual_value / target_value * 100 if target_value != 0 else np.nan
                gap = actual_value - target_value

                results.append({
                    "KPI": kpi,
                    "Thực tế": actual_value,
                    "Mục tiêu": target_value,
                    "Chênh lệch": gap,
                    "% Hoàn thành": pct
                })
            else:
                results.append({
                    "KPI": kpi,
                    "Thực tế": "N/A",
                    "Mục tiêu": target_value,
                    "Chênh lệch": "N/A",
                    "% Hoàn thành": "Không có dữ liệu"
                })

        compare_df = pd.DataFrame(results)
        st.dataframe(compare_df, use_container_width=True)

    st.header("📟 Mức độ hoàn thành KPI")

    gauge_paths = []

    if compare_df is not None:
        cols = st.columns(2)

        for i, row in compare_df.iterrows():
            if isinstance(row["% Hoàn thành"], (int, float)):

                gauge_path = f"gauge_{row['KPI']}.png"
                draw_gauge(row["% Hoàn thành"], row["KPI"], gauge_path)
                gauge_paths.append(gauge_path)

                with cols[i % 2]:
                    st.image(gauge_path, width=200)
    
    if compare_df is not None:
        fig_stack, ax_stack = plt.subplots(figsize=(8,4))

        labels = compare_df["KPI"].astype(str).tolist()
        actual = pd.to_numeric(compare_df["Thực tế"], errors="coerce").fillna(0)
        target = pd.to_numeric(compare_df["Mục tiêu"], errors="coerce").fillna(0)

        # 🔴 BỎ ÂM TRIỆT ĐỂ
        actual = actual.abs()
        target = target.abs()

        achieved = np.minimum(actual, target)
        remaining = np.maximum(target - achieved, 0)

        x = np.arange(len(labels))

        ax_stack.bar(x, achieved, label="Đã đạt")
        ax_stack.bar(x, remaining, bottom=achieved, label="Còn thiếu")

        ax_stack.set_xticks(x)
        ax_stack.set_xticklabels(labels, rotation=45, ha="right")

        ax_stack.set_title("Tổng hợp mức độ hoàn thành KPI")
        ax_stack.legend()

        st.pyplot(fig_stack)

        stack_chart_path = "chart_kpi_stack.png"
        fig_stack.savefig(stack_chart_path, dpi=150, bbox_inches="tight")
        plt.close()

        
    # =========================
    # EXPORT PDF
    # =========================
    st.header("5️⃣ Xuất báo cáo PDF")

    if st.button("📄 Tạo báo cáo PDF"):
        pdfmetrics.registerFont(TTFont("DejaVu", "DejaVuSans.ttf"))

        pdf_file = "financial_report.pdf"
        doc = SimpleDocTemplate(pdf_file, pagesize=A4)
        styles = getSampleStyleSheet()

        # =========================
        # Style
        # =========================
        style_title = ParagraphStyle(
            'Title_vi', parent=styles['Title'],
            fontName='DejaVu', fontSize=18
        )
        style_heading = ParagraphStyle(
            'Heading_vi', parent=styles['Heading2'],
            fontName='DejaVu', fontSize=14
        )
        style_normal = ParagraphStyle(
            'Normal_vi', parent=styles['Normal'],
            fontName='DejaVu', fontSize=10
        )

        elements = []
        elements.append(Paragraph("BÁO CÁO TÀI CHÍNH TỔNG HỢP", style_title))
        elements.append(Spacer(1, 10))
        elements.append(
            Paragraph(
                f"Ngày lập: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
                style_normal
            )
        )
        elements.append(Spacer(1, 20))

        # =========================
        # TABLE FUNCTION
        # =========================
        def add_table(df, title):
            elements.append(Paragraph(title, style_heading))
            elements.append(Spacer(1, 6))

            table_data = [df.columns.tolist()] + df.fillna("").astype(str).values.tolist()
            tbl = Table(table_data, repeatRows=1)

            tbl.setStyle(TableStyle([
                ('FONTNAME', (0,0), (-1,-1), 'DejaVu'),
                ('FONTSIZE', (0,0), (-1,0), 10),
                ('FONTSIZE', (0,1), (-1,-1), 9),
                ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
                ('ALIGN', (1,1), (-1,-1), 'RIGHT'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('GRID', (0,0), (-1,-1), 0.5, colors.black),
                ('BOTTOMPADDING', (0,0), (-1,0), 6),
                ('TOPPADDING', (0,0), (-1,0), 6),
            ]))

            elements.append(tbl)
            elements.append(Spacer(1, 15))

        # =========================
        # TABLES
        # =========================
        add_table(kpi_df, "1. Tổng hợp KPI")
        add_table(ratio_df, "2. Tỷ số tài chính")

        if compare_df is not None:
            add_table(compare_df, "3. So sánh với chỉ tiêu mục tiêu")

        # =========================
        # FINANCIAL CHARTS
        # =========================
        elements.append(Paragraph("4. Phân tích đồ thị tài chính", style_heading))
        elements.append(Spacer(1, 10))

        for p in [chart_path, chart_margin_path, chart_cost_path, chart_capital_path]:
            if p and os.path.exists(p):
                elements.append(Image(p, width=420, height=240))
                elements.append(Spacer(1, 12))

        # =========================
        # KPI GAUGE CHARTS
        # =========================
        if compare_df is not None and len(gauge_paths) > 0:
            elements.append(Paragraph("5. Mức độ hoàn thành các chỉ tiêu KPI", style_heading))
            elements.append(Spacer(1, 10))

            for i in range(0, len(gauge_paths), 2):
                row_imgs = []

                for p in gauge_paths[i:i+2]:
                    if os.path.exists(p):
                        row_imgs.append(Image(p, width=200, height=200))

                if row_imgs:
                    elements.append(Table([row_imgs], colWidths=[230]*len(row_imgs)))
                    elements.append(Spacer(1, 12))

        # =========================
        # STACKED KPI SUMMARY
        # =========================
        if stack_chart_path and os.path.exists(stack_chart_path):
            elements.append(Paragraph("6. Tổng hợp KPI: Đã đạt và Còn thiếu", style_heading))
            elements.append(Spacer(1, 10))
            elements.append(Image(stack_chart_path, width=420, height=240))
            elements.append(Spacer(1, 15))

        # =========================
        # BUILD PDF
        # =========================
        doc.build(elements)

        with open(pdf_file, "rb") as f:
            st.download_button(
                "⬇️ Tải PDF",
                f,
                file_name="financial_report.pdf"
            )

        # =========================
        # CLEAN TEMP FILES
        # =========================
        for p in (
            [chart_path, chart_margin_path, chart_cost_path, chart_capital_path]
            + gauge_paths
            + [stack_chart_path]
        ):
            if p and os.path.exists(p):
                os.remove(p)

        os.remove(pdf_file)
