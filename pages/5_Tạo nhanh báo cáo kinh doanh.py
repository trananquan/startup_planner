#!/usr/bin/env python
# coding: utf-8

# In[ ]:

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from reportlab.platypus import Image
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from datetime import datetime
import os

# ---------------------------------------------------------
# STREAMLIT CONFIG
# ---------------------------------------------------------
st.set_page_config(page_title="Module 5 – Business Report", layout="wide")
st.title("📊 Tạo nhanh báo cáo kinh doanh")

# ---------------------------------------------------------
# UPLOAD CSV
# ---------------------------------------------------------
st.header("1️⃣💾 Upload dữ liệu kinh doanh (CSV)")

uploaded_file = st.file_uploader(
    "File CSV cần có các cột: Date, Revenue, COGS, Operating_Cost, Marketing_Cost, Other_Cost",
    type=["csv"]
)

if uploaded_file:

   df = pd.read_csv(uploaded_file)
   df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

   required_cols = [
    "Revenue", "COGS", "Operating_Cost",
    "Marketing_Cost", "Other_Cost"
]

   for col in required_cols:
      if col not in df.columns:
        st.error(f"Thiếu cột bắt buộc: {col}")
        st.stop()

# ---------------------------------------------------------
# FINANCIAL CALCULATIONS
# ---------------------------------------------------------
   st.header("1.Tính toán lợi nhuận & chỉ tiêu tài chính")

   df["Total_Cost"] = (
     df["COGS"]
    + df["Operating_Cost"]
    + df["Marketing_Cost"]
    + df["Other_Cost"]
)

   df["Gross_Profit"] = df["Revenue"] - df["COGS"]
   df["Operating_Profit"] = df["Gross_Profit"] - df["Operating_Cost"]
   df["Net_Profit"] = df["Revenue"] - df["Total_Cost"]

# Financial Ratios
   df["Gross_Margin"] = df["Gross_Profit"] / df["Revenue"]
   df["Operating_Margin"] = df["Operating_Profit"] / df["Revenue"]
   df["Net_Margin"] = df["Net_Profit"] / df["Revenue"]
   df["Cost_to_Revenue"] = df["Total_Cost"] / df["Revenue"]

   st.subheader("📄 Bảng dữ liệu sau xử lý")

   df_display = df.copy()
   df_display["Date"] = df_display["Date"].dt.strftime("%d/%m/%Y")

   st.dataframe(df_display, use_container_width=True)

# ---------------------------------------------------------
# KPI SUMMARY
# ---------------------------------------------------------
   st.subheader("📌 Tổng hợp KPI ")

# Các KPI cần tổng hợp
   kpi_list = [
    "Revenue", "Total_Cost", "Net_Profit", "Gross_Margin", "Operating_Margin", "Net_Margin", "Cost_to_Revenue"]

   kpi_summary = []

   for col in kpi_list:
       if col in df.columns:
          kpi_summary.append({
            "KPI": col,
            "Tổng": df[col].sum() if df[col].dtype != 'float64' or 'Margin' not in col else np.nan,
            "Trung bình": df[col].mean(),
            "Giá trị cao nhất": df[col].max(),
            "Giá trị thấp nhất": df[col].min()
        })

   kpi_summary_df = pd.DataFrame(kpi_summary)
   st.table(kpi_summary_df.style.format({
    "Tổng": "{:,.2f}",
    "Trung bình": "{:,.2f}",
    "Giá trị cao nhất": "{:,.2f}",
    "Giá trị thấp nhất": "{:,.2f}"
}))

    # 2️⃣ Chỉ tiêu tài chính bổ sung
    # ----------------------
   st.subheader("🎯Chỉ tiêu tài chính bổ sung")

   additional_metrics = {}

    # Tăng trưởng Revenue
   if "Revenue" in df.columns:
        additional_metrics["Tăng trưởng Revenue (%)"] = (df["Revenue"].iloc[-1] - df["Revenue"].iloc[0]) / df["Revenue"].iloc[0] * 100

    # Tăng trưởng Net Profit
   if "Net_Profit" in df.columns:
        additional_metrics["Tăng trưởng Net Profit (%)"] = (df["Net_Profit"].iloc[-1] - df["Net_Profit"].iloc[0]) / df["Net_Profit"].iloc[0] * 100

    # Marketing/Revenue trung bình
   if "Marketing_Cost" in df.columns and "Revenue" in df.columns:
        additional_metrics["Marketing/Revenue trung bình (%)"] = (df["Marketing_Cost"] / df["Revenue"]).mean() * 100

    # Operating/Revenue trung bình
   if "Operating_Cost" in df.columns and "Revenue" in df.columns:
        additional_metrics["Operating/Revenue trung bình (%)"] = (df["Operating_Cost"] / df["Revenue"]).mean() * 100

    # Burn Rate trung bình
   if "Total_Cost" in df.columns:
        burn_rate = df["Total_Cost"].mean()
        additional_metrics["Burn Rate trung bình"] = burn_rate

    # Runway (tháng)
   if "Cash_Balance" in df.columns and "Total_Cost" in df.columns:
        runway = df["Cash_Balance"].iloc[-1] / burn_rate
        additional_metrics["Runway (tháng)"] = runway

    # Chia 2 cột hiển thị gọn
# Chuyển dict sang DataFrame để hiện bảng
   table_df = pd.DataFrame({
      "Chỉ tiêu": list(additional_metrics.keys()),
      "Giá trị": [
        f"{v:.1f}%" if "%" in k else f"{v:,.2f}"
        for k, v in additional_metrics.items()
    ]
})

# Hiển thị bảng
   st.table(table_df)
# TIME AGGREGATION
# ---------------------------------------------------------
   st.header("2.Phân tích theo thời gian")

   freq = st.selectbox("Chọn kỳ phân tích", ["Monthly", "Yearly"])

   if freq == "Monthly":
      grouped = df.resample("M", on="Date").sum()
   else:
      grouped = df.resample("Y", on="Date").sum()

# ---------------------------------------------------------
# VISUALIZATION
# ---------------------------------------------------------
   st.subheader("📈 Biểu đồ doanh thu – chi phí – lợi nhuận")

   fig1, ax1 = plt.subplots(figsize=(8, 4))
   ax1.plot(grouped.index, grouped["Revenue"], label="Revenue")
   ax1.plot(grouped.index, grouped["Total_Cost"], label="Total Cost")
   ax1.plot(grouped.index, grouped["Net_Profit"], label="Net Profit")
   ax1.legend(fontsize=8)
   ax1.set_xlabel("Time", fontsize=7)
   ax1.set_ylabel("Value", fontsize=7)

   ax1.xaxis.set_major_formatter(mdates.DateFormatter("%m-%Y"))
   ax1.xaxis.set_major_locator(mdates.MonthLocator())
   st.pyplot(fig1)

   chart1_path = "revenue_cost_profit.png"
   fig1.savefig(chart1_path, dpi=150, bbox_inches="tight")
   plt.close(fig1)


   st.subheader("📉 Biểu đồ biên lợi nhuận")

   margin_df = grouped.copy()
   margin_df["Net_Margin"] = grouped["Net_Profit"] / grouped["Revenue"]

   fig2, ax2 = plt.subplots(figsize=(8, 4))
   ax2.plot(margin_df.index, margin_df["Net_Margin"] * 100)
   ax2.set_ylabel("Net Margin (%)", fontsize=7)
   ax2.set_xlabel("Time", fontsize=7)
   ax2.xaxis.set_major_formatter(mdates.DateFormatter("%m-%Y"))
   ax2.xaxis.set_major_locator(mdates.MonthLocator())
   st.pyplot(fig2)

   chart2_path = "net_margin.png"
   fig2.savefig(chart2_path, dpi=150, bbox_inches="tight")
   plt.close(fig2)

st.divider()
# KPI THEO MỤC TIÊU
# ---------------------------------------------------------
st.header("2️⃣🎯So sánh KPI với mục tiêu")

target_file = st.file_uploader(
    "Upload file KPI mục tiêu CSV (cùng cột với dữ liệu gốc)", type=["csv"], key="target"
)

if target_file is None:
    st.info("⬆️ Vui lòng upload file KPI mục tiêu để bắt đầu so sánh.")
else:
    df_target = pd.read_csv(target_file)

    # Tìm các KPI numeric chung giữa file gốc và file mục tiêu
    common_kpi = list(set(df_target.columns).intersection(set(df.columns)))
    
    # Loại bỏ các cột ngày hoặc không phải numeric
    common_kpi = [
        k for k in common_kpi 
        if k.lower() != "date" and np.issubdtype(df[k].dtype, np.number)
    ]
    
    if not common_kpi:
        st.warning("⚠️ Không tìm thấy KPI numeric chung giữa dữ liệu gốc và file mục tiêu.")
    else:
        st.write(f"✅ KPI chung để so sánh: {', '.join(common_kpi)}")

        # -----------------------------
        # Gauge chart 2 cột
        # -----------------------------
        col1, col2 = st.columns(2)

        for i, k in enumerate(common_kpi):
            latest_value = df[k].iloc[-1]
            target_value = df_target[k].iloc[-1]

            # Tính % hoàn thành KPI (không vượt 100%)
            pct_achieved = min(latest_value / target_value * 100, 100) if target_value != 0 else 0

            # Tính tăng tuyệt đối và tương đối
            abs_change = latest_value - target_value
            rel_change = (latest_value - target_value) / target_value * 100 if target_value != 0 else np.nan

            # Chọn cột hiển thị
            col = col1 if i % 2 == 0 else col2
            with col:
                st.markdown(f"**{k}**")
                st.markdown(f"- Thực tế/ Mục tiêu: {latest_value:.2f} / {target_value:.2f} ({pct_achieved:.1f}%)")
                st.markdown(f"- Thay đổi tuyệt đối: {abs_change:.2f}")
                st.markdown(f"- Thay đổi tương đối: {rel_change:.2f}%")

                # Gauge chart
                import plotly.graph_objects as go
                fig_gauge = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=pct_achieved,
                    number={'suffix': "%"},
                    gauge={
                        'axis': {'range': [0, 100]},
                        'bar': {'color': "green" if pct_achieved >= 100 else "orange"},
                        'steps': [
                            {'range': [0, 50], 'color': "red"},
                            {'range': [50, 100], 'color': "yellow"}
                        ]
                    },
                    title={'text': f"{k} đạt KPI (%)"}
                ))

                fig_gauge.update_layout(
                    width=280,
                    height=210,
                    margin=dict(l=10, r=10, t=40, b=10)
                )

                st.plotly_chart(fig_gauge, use_container_width=False)
                
        
        # -----------------------------
        # Stacked column chart tổng quan
        # -----------------------------
        achieved = [min(df[k].iloc[-1], df_target[k].iloc[-1]) for k in common_kpi]
        remaining = [df_target[k].iloc[-1] - min(df[k].iloc[-1], df_target[k].iloc[-1]) for k in common_kpi]

        df_stack = pd.DataFrame({
            "KPI": common_kpi,
            "Đạt được": achieved,
            "Còn thiếu": remaining
        })

        import plotly.express as px
        fig_stack = px.bar(
            df_stack,
            x="KPI",
            y=["Đạt được", "Còn thiếu"],
            title="So sánh KPI thực tế với mục tiêu",
            text_auto=True
        )
        st.plotly_chart(fig_stack, use_container_width=True)

st.divider()


# ==============================
# PDF EXPORT – KPI

st.header("3️⃣📈 Xuất báo cáo PDF KPI")

if st.button("📄 Tạo báo cáo PDF"):

    # Kiểm tra file font
    font_path = "DejaVuSans.ttf"
    if not os.path.exists(font_path):
        st.error("⚠️ File font DejaVuSans.ttf không tìm thấy. Vui lòng đặt cùng thư mục với app.")
        st.stop()

    # Đăng ký font Unicode
    pdfmetrics.registerFont(TTFont('DejaVu', font_path))

    # Tạo file PDF
    pdf_file = "business_report.pdf"
    doc = SimpleDocTemplate(pdf_file, pagesize=A4)

    # Style
    styles = getSampleStyleSheet()
    style_title = ParagraphStyle('Title_vi', parent=styles['Title'], fontName='DejaVu', fontSize=18)
    style_heading = ParagraphStyle('Heading_vi', parent=styles['Heading2'], fontName='DejaVu', fontSize=14)
    style_normal = ParagraphStyle('Normal_vi', parent=styles['Normal'], fontName='DejaVu', fontSize=10)

    elements = []

    # Tiêu đề
    elements.append(Paragraph("BÁO CÁO KẾT QUẢ KINH DOANH", style_title))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"Ngày tạo: {datetime.now().strftime('%d/%m/%Y %H:%M')}", style_normal))
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("1. Bảng chỉ tiêu tổng hợp KPI", style_heading))
    # =========================
    # KPI SUMMARY TABLE
    # =========================
    # Header bọc Paragraph để hiển thị tiếng Việt
    table_data = [
    [
        Paragraph("KPI", style_normal),
        Paragraph("Tổng", style_normal),
        Paragraph("Trung bình", style_normal),
        Paragraph("Giá trị cao nhất", style_normal),
        Paragraph("Giá trị thấp nhất", style_normal)
    ]
]

    for _, row in kpi_summary_df.iterrows():
        table_data.append([
            Paragraph(str(row["KPI"]), style_normal),
            Paragraph(f"{row['Tổng']:,.2f}" if pd.notna(row["Tổng"]) else "—", style_normal),
            Paragraph(f"{row['Trung bình']:,.2f}", style_normal),
            Paragraph(f"{row['Giá trị cao nhất']:,.2f}", style_normal),
            Paragraph(f"{row['Giá trị thấp nhất']:,.2f}", style_normal),
        ])

    tbl = Table(table_data, hAlign='LEFT')
    tbl.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    elements.append(tbl)
    elements.append(Spacer(1, 30))

    
    # Chỉ tiêu KPI bổ sung----------------------

    # Title section
    elements.append(Paragraph("2. Chỉ tiêu tài chính bổ sung", style_heading))
    elements.append(Spacer(1, 10))

    # Chuẩn bị dữ liệu bảng
    table_data = [
        [Paragraph("Chỉ tiêu", style_heading), Paragraph("Giá trị", style_heading)]
    ]

    for k, v in additional_metrics.items():
        if "%" in k:
            val_str = f"{v:.1f}%"
        else:
            val_str = f"{v:,.2f}"
        table_data.append([Paragraph(k, style_normal), Paragraph(val_str, style_normal)])

    # Tạo bảng
    tbl = Table(table_data, colWidths=[250, 100], hAlign='LEFT')
    tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # header màu xám
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),          # căn phải cột giá trị
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black), # vẽ lưới
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('TOPPADDING', (0,0), (-1,0), 6),
    ]))

    elements.append(tbl)
    elements.append(Spacer(1, 20))


    # Charts
    # =========================
    if os.path.exists(chart1_path):
        elements.append(Paragraph("3. Doanh thu – Chi phí – Lợi nhuận ròng", style_heading))
        elements.append(Spacer(1, 10))
        elements.append(Image(chart1_path, width=450, height=250))
        elements.append(Spacer(1, 30))

    if os.path.exists(chart2_path):
        elements.append(Paragraph("Biên lợi nhuận ròng (%)", style_heading))
        elements.append(Spacer(1, 10))
        elements.append(Image(chart2_path, width=450, height=250))

        # So sánh KPI với mục tiêu (nếu có)
    # ----------------------
    if 'df_target' in globals():
        elements.append(Paragraph("4. So sánh KPI với mục tiêu", style_heading))
        elements.append(Spacer(1, 10))

        for k in common_kpi:
            latest_value = df[k].iloc[-1]
            target_value = df_target[k].iloc[-1]
            pct_achieved = min(latest_value / target_value * 100, 100) if target_value != 0 else 0
            abs_change = latest_value - target_value
            rel_change = (latest_value - target_value) / target_value * 100 if target_value != 0 else 0
            
            elements.append(Paragraph(f"{k}"))
            elements.append(Paragraph(f"- Thực tế/Mục tiêu: {latest_value:,.2f} / {target_value:,.2f} ({pct_achieved:.1f}%)", style_normal))
            elements.append(Paragraph(f"- Thay đổi tuyệt đối: {abs_change:,.2f}", style_normal))
            elements.append(Paragraph(f"- Thay đổi tương đối: {rel_change:,.2f}%", style_normal))
            elements.append(Spacer(1, 5))

    
    # ----------------------
# ==============================
# KPI TARGET CHARTS – PDF
    def draw_gauge(pct, title, file_path):
        """
        pct: % hoàn thành (0–100)
        """
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(3.5, 2.2))

        pct = max(0, min(100, pct))

        # Vẽ nền
        ax.barh(0, 100, color="#eeeeee")
        # Vẽ phần đạt được
        ax.barh(0, pct, color="#4CAF50" if pct >= 100 else "#FF9800")

        ax.set_xlim(0, 100)
        ax.set_yticks([])
        ax.set_xticks([0, 50, 100])
        ax.set_xlabel("% hoàn thành")

        ax.set_title(title, fontsize=10)
        ax.text(pct / 2, 0, f"{pct:.1f}%", 
                va="center", ha="center", fontsize=11, color="black")

        for spine in ax.spines.values():
            spine.set_visible(False)

        plt.tight_layout()
        plt.savefig(file_path, dpi=150)
        plt.close()

    def draw_stacked_kpi(df_stack, file_path):
        import matplotlib.pyplot as plt
        import numpy as np

        x = np.arange(len(df_stack))
        achieved = df_stack["Đạt được"]
        remaining = df_stack["Còn thiếu"]

        fig, ax = plt.subplots(figsize=(6, 3.5))
        ax.bar(x, achieved, label="Đạt được")
        ax.bar(x, remaining, bottom=achieved, label="Còn thiếu")

        ax.set_xticks(x)
        ax.set_xticklabels(df_stack["KPI"], rotation=30, ha="right")
        ax.set_title("Tổng hợp các KPI thực tế so với mục tiêu")
        ax.legend()

        plt.tight_layout()
        plt.savefig(file_path, dpi=150)
        plt.close()


    col_files = []
    stack_file = None


    if 'df_target' in globals() and common_kpi:
        elements.append(Paragraph("4.1 So sánh % mức độ hoàn thành KPI so với với mục tiêu", style_heading))
        elements.append(Spacer(1, 10))

        # -------------------------
        # Gauge charts – 2 cột
        # -------------------------
        rows = []
        temp_row = []

        for i, k in enumerate(common_kpi):
            latest_value = df[k].iloc[-1]
            target_value = df_target[k].iloc[-1]

            pct_achieved = (latest_value / target_value * 100) if target_value != 0 else 0
            pct_achieved = min(pct_achieved, 100)

            gauge_path = f"gauge_{k}.png"
            draw_gauge(pct_achieved, k, gauge_path)

            col_files.append(gauge_path)
            temp_row.append(Image(gauge_path, width=240, height=120))

            if len(temp_row) == 2:
                rows.append(temp_row)
                temp_row = []

        if temp_row:
            temp_row.append("")
            rows.append(temp_row)

        from reportlab.platypus import Table
        gauge_table = Table(rows, colWidths=[260, 260], hAlign="CENTER")
        elements.append(gauge_table)
        elements.append(Spacer(1, 20))
        # ----- STACKED BAR -----
        achieved = [min(df[k].iloc[-1], df_target[k].iloc[-1]) for k in common_kpi]
        remaining = [max(df_target[k].iloc[-1] - df[k].iloc[-1], 0) for k in common_kpi]

        df_stack = pd.DataFrame({
            "KPI": common_kpi,
            "Đạt được": achieved,
            "Còn thiếu": remaining
        })

        stack_file = "kpi_stack.png"
        draw_stacked_kpi(df_stack, stack_file)

        elements.append(Image(stack_file, width=450, height=260))
        elements.append(Spacer(1, 20))


    # =========================
    # Xây PDF
    # =========================
    doc.build(elements)

    # Download PDF
    with open(pdf_file, "rb") as f:
        st.download_button(
            "⬇️ Tải báo cáo PDF",
            f,
            file_name="business_report.pdf"
        )

    # Xóa file tạm an toàn
    for f in col_files:
        if os.path.exists(f):
            os.remove(f)
    if stack_file and os.path.exists(stack_file):
        os.remove(stack_file)
    if os.path.exists(chart1_path):
        os.remove(chart1_path)
    if os.path.exists(chart2_path):
        os.remove(chart2_path)
    if os.path.exists(pdf_file):
        os.remove(pdf_file)


