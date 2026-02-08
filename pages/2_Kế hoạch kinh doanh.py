#!/usr/bin/env python
# coding: utf-8

# In[ ]:

import streamlit as st
import pandas as pd
from modules.business import unit_economics, assess_unit_economics
from modules.business import unit_economics_recommendations
from modules.scenario import scenario_analysis

st.title("📈 Tính toán và lập kế hoạch kinh doanh")

st.subheader("1️⃣ Tính toán các chỉ tiêu kinh doanh")

# INPUT
arpu = st.number_input("Doanh thu mỗi người dùng (ARPU)", 0.0)
cac = st.number_input("Chi phí giành khách hàng (CAC)", 0.0)
churn = st.number_input("Tỷ lệ rời bỏ (0–1)", 0.01)
gross_margin = st.slider("Biên lợi nhuận gộp (Gross Margin)", 0.0, 1.0, 0.6)

# Khởi tạo ue = None
ue = None
recommendations = []

# NÚT TÍNH TOÁN
if st.button("📌 Tính toán Unit Economics"):

    # Tính toán các chỉ số
    ue = unit_economics(arpu, cac, churn, gross_margin)
    recommendations = unit_economics_recommendations(ue)
    # Hiển thị bảng
    label_map = {
        "ARPU": "Doanh thu mỗi khách hàng (ARPU)",
        "CAC": "Chi phí thu hút khách hàng (CAC)",
        "LTV": "Giá trị vòng đời khách hàng (LTV)",
        "LTV/CAC": "Tỷ lệ LTV / CAC",
        "Payback (months)": "Thời gian hoàn vốn CAC (tháng)",
        "Net Unit Profit": "Lợi nhuận ròng trên mỗi khách hàng",
        "Churn": "Tỷ lệ rời bỏ hàng tháng",
        "Gross Margin": "Biên lợi nhuận gộp"
    }
    df_ue = pd.DataFrame.from_dict(ue, orient="index", columns=["Giá trị"]).rename(index=label_map)
    st.subheader("📊 Kết quả Unit Economics")
    st.table(df_ue)

    # Đánh giá mô hình kinh doanh
    assessment, color = assess_unit_economics(ue)
    st.subheader("🧠 Đánh giá mô hình kinh doanh")
    if color == "success":
        st.success(assessment)
    elif color == "warning":
        st.warning(assessment)
    else:
        st.error(assessment)

    # Biểu đồ minh họa LTV / CAC
    st.subheader("📈 Minh họa LTV / CAC")
    st.bar_chart({"LTV": [ue["LTV"]], "CAC": [ue["CAC"]]})

    # =========================
    # Gợi ý chiến lược
    # =========================
st.subheader("2️⃣ Gợi ý chiến lược dựa trên kết quả phân tích")

if recommendations:
    for rec in recommendations:
        if rec.startswith("✅"):
            st.success(rec)
        elif rec.startswith("⚠️") or rec.startswith("⏳"):
            st.warning(rec)
        else:
            st.info(rec)
else:
    st.info("Nhấn nút '📌 Tính toán Unit Economics' để xem gợi ý")

# Scenario analysis
st.divider()
st.subheader("3️⃣ Phân tích kịch bản kinh doanh (Xấu nhất / Trung bình / Tốt nhất) 📊")

initial_cash = st.number_input("Tiền mặt ban đầu", 0.0)
months = st.slider("Khoảng thời gian kịch bản (tháng)", 6, 48, 24)

# ===== INPUT SCENARIOS =====
scenarios = {}

# ================= BEST CASE =================
st.markdown("### 🚀 Kịch bản tốt nhất")

col1, col2 = st.columns(2)

with col1:
    best_revenue = st.number_input("Doanh thu (Tốt nhất)", 0.0, key="best_rev")
    best_growth = st.slider("Tỷ lệ tăng trưởng (Tốt nhất)", 0.0, 0.5, 0.15, key="best_g")

with col2:
    best_fixed_cost = st.number_input("Chi phí cố định (Tốt nhất)", 0.0, key="best_fc")
    best_var_ratio = st.slider("Tỷ lệ chi phí biến đổi (Tốt nhất)", 0.0, 1.0, 0.25, key="best_v")

scenarios["Kịch bản tốt nhất 🚀"] = {
    "revenue": best_revenue,
    "growth": best_growth,
    "fixed_cost": best_fixed_cost,
    "var_ratio": best_var_ratio
}

# ================= BASE CASE =================
st.markdown("### ⚖️ Kịch bản trung bình")

col1, col2 = st.columns(2)

with col1:
    base_revenue = st.number_input("Doanh thu (Trung bình)", 0.0, key="base_rev")
    base_growth = st.slider("Tỷ lệ tăng trưởng (Trung bình)", -0.1, 0.3, 0.05, key="base_g")

with col2:
    base_fixed_cost = st.number_input("Chi phí cố định (Trung bình)", 0.0, key="base_fc")
    base_var_ratio = st.slider("Tỷ lệ chi phí biến đổi (Trung bình)", 0.0, 1.0, 0.30, key="base_v")

scenarios["Kịch bản trung bình ⚖️"] = {
    "revenue": base_revenue,
    "growth": base_growth,
    "fixed_cost": base_fixed_cost,
    "var_ratio": base_var_ratio
}

# ================= WORST CASE =================
st.markdown("### 🧨 Kịch bản xấu nhất")

col1, col2 = st.columns(2)

with col1:
    worst_revenue = st.number_input("Doanh thu (Xấu nhất)", 0.0, key="worst_rev")
    worst_growth = st.slider("Tỷ lệ tăng trưởng (Xấu nhất)", -0.3, 0.1, -0.10, key="worst_g")

with col2:
    worst_fixed_cost = st.number_input("Chi phí cố định (Xấu nhất)", 0.0, key="worst_fc")
    worst_var_ratio = st.slider("Tỷ lệ chi phí biến đổi (Xấu nhất)", 0.0, 1.0, 0.40, key="worst_v")

scenarios["Kịch bản xấu nhất 🧨"] = {
    "revenue": worst_revenue,
    "growth": worst_growth,
    "fixed_cost": worst_fixed_cost,
    "var_ratio": worst_var_ratio
}

# ===== RUN SCENARIO =====
results = scenario_analysis(initial_cash, scenarios, months)

# ===== COMBINE INTO ONE DATAFRAME =====
combined_df = pd.DataFrame({"Month": range(1, months + 1)})

for name, df in results.items():
    combined_df[name] = df["Cash Balance"].values

combined_df.set_index("Month", inplace=True)

# ===== PLOT ONE CHART – THREE LINES =====
st.line_chart(combined_df)
