#!/usr/bin/env python
# coding: utf-8

# In[ ]:

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from modules.finance import break_even_point
from modules.monte_carlo import monte_carlo_profit
from modules.cashflow import cash_flow_forecast, calculate_runway
from modules.finance import extended_financial_ratios, financial_health_assessment

st.title("📊 Tính toán & Lập kế hoạch tài chính")

st.subheader("1️⃣ Phân tích điểm hòa vốn")

fixed_cost = st.number_input("Chi phí cố định", 0.0)
price = st.number_input("Giá bán mỗi sp", 0.0)
variable_cost = st.number_input("Chi phí biến đổi mỗi sp", 0.0)

# Tính toán BEP
bep = None
show_warning = False

if price > 0 and variable_cost >= 0 and fixed_cost >= 0:
    if price > variable_cost:
        bep = fixed_cost / (price - variable_cost)
    else:
        show_warning = True  # Biên lợi nhuận ≤ 0

# Hiển thị kết quả nếu đã tính
if bep:
    st.success(f"Số lượng tại điểm hòa vốn: {bep:.2f} đơn vị")

    # Vẽ biểu đồ
    q = np.linspace(0, bep * 1.5, 100)
    revenue = price * q
    total_cost = fixed_cost + variable_cost * q
    fixed_cost_line = np.full_like(q, fixed_cost)

    fig, ax = plt.subplots()
    ax.plot(q, revenue, label="Tổng doanh thu")
    ax.plot(q, total_cost, label="Tổng chi phí")
    ax.plot(q, fixed_cost_line, linestyle="--", label="Chi phí cố định")
    ax.scatter(bep, price * bep, color="red")
    ax.axvline(bep, linestyle=":", alpha=0.7)
    ax.axhline(price * bep, linestyle=":", alpha=0.7)

    ax.set_xlabel("Số lượng bán ra")
    ax.set_ylabel("Chi phí / Doanh thu")
    ax.set_title("Phân tích điểm hòa vốn")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

elif show_warning:
    st.warning("⚠️ Giá bán phải lớn hơn chi phí biến đổi mỗi sản phẩm để đạt điểm hòa vốn.")

st.divider()

st.subheader("2️⃣ Mô phỏng Monte Carlo (Rủi ro lợi nhuận)")

n = st.slider("Số lần mô phỏng", 100, 10000, 1000)

profit_sim = monte_carlo_profit(
    n,
    price_mean=price,
    price_std=price*0.1,
    demand_mean=bep if bep else 100,
    demand_std=20,
    fixed_cost=fixed_cost,
    variable_cost=variable_cost
)

st.line_chart(np.sort(profit_sim))
st.metric("Lợi nhuận kì vọng", f"{profit_sim.mean():,.0f}")
st.metric("Khả năng thua lỗ", f"{(profit_sim<0).mean()*100:.2f}%")
st.divider()

st.subheader("3️⃣ Phân tích chỉ tiêu và sức khỏe tài chính")

col1, col2 = st.columns(2)

# --------------------
# COLUMN 1: Performance / Operational
# --------------------
with col1:
    st.markdown("### 📈 Hiệu quả kinh doanh")
    revenue = st.number_input("Doanh thu", 0.0)
    cogs = st.number_input("Giá vốn hàng bán (COGS)", 0.0)
    operating_cost = st.number_input("Chi phí hoạt động", 0.0)

    total_cost = cogs + operating_cost
    net_profit = revenue - total_cost
    st.caption(f"Lợi nhuận ròng (auto): {net_profit:,.0f}")

# --------------------
# COLUMN 2: Balance Sheet / Liquidity / Leverage
# --------------------
with col2:
    st.markdown("### 🧾 Cân đối kế toán & rủi ro")
    total_assets = st.number_input("Tổng tài sản", 0.0)
    equity = st.number_input("Vốn chủ sở hữu", 0.0)
    current_assets = st.number_input("Tài sản ngắn hạn", 0.0)
    current_liabilities = st.number_input("Nợ ngắn hạn", 0.0)
    cash = st.number_input("Tiền mặt", 0.0)
    total_debt = st.number_input("Tổng nợ", 0.0)

# --------------------
# TÍNH RATIOS
# --------------------
if st.button("📌 Tính chỉ tiêu & Đánh giá sức khỏe tài chính"):

    ratios = extended_financial_ratios(
        revenue,
        cogs,
        operating_cost,
        total_cost,
        net_profit,
        total_assets,
        equity,
        current_assets,
        current_liabilities,
        cash,
        total_debt
    )

    assessment, score = financial_health_assessment(ratios)

    # --------------------
    # HIỂN THỊ RATIOS
    # --------------------
    st.subheader("📊 Các chỉ tiêu tài chính")
    st.json(ratios)

    # --------------------
    # HIỂN THỊ HEALTH ASSESSMENT
    # --------------------
    st.subheader("🧠 Đánh giá sức khỏe tài chính")
    for k, v in assessment.items():
        if v == "Strong":
            st.success(f"{k}: {v}")
        elif v == "Acceptable":
            st.warning(f"{k}: {v}")
        else:
            st.error(f"{k}: {v}")

    st.metric("🏁 Điểm số sức khỏe tài chính", f"{score} / 10")
st.divider()

# Cashflow forecast
st.subheader("4️⃣ Dự báo dòng tiền & Tốc độ tiêu tiền hàng tháng 💸")

col1, col2 = st.columns(2)
with col1:
     initial_cash = st.number_input("Tiền mặt ban đầu (VND)", 0.0)
     monthly_revenue = st.number_input("Doanh thu hàng tháng", 0.0)
     monthly_growth = st.slider("Tỷ lệ tăng trưởng doanh thu hàng tháng", -0.2, 0.5, 0.05)
with col2:
     fixed_cost = st.number_input("Chi phí cố định hàng tháng", 0.0)
     variable_cost_ratio = st.slider("Tỷ lệ chi phí biến đổi", 0.0, 1.0, 0.3)
     months = st.slider("Khoảng thời gian dự báo (tháng)", 6, 60, 24)

df_cf = cash_flow_forecast(
    initial_cash,
    monthly_revenue,
    monthly_growth,
    fixed_cost,
    variable_cost_ratio,
    months
)

df_display = df_cf.rename(columns={
    "Month": "Tháng",
    "Revenue": "Doanh thu",
    "Total Cost": "Tổng chi phí",
    "Net Cash Flow": "Dòng tiền ròng",
    "Cash Balance": "Số dư tiền mặt"
})

st.dataframe(df_display)
#Vẽ biểu đồ Cash Balance
st.line_chart(df_display.set_index("Tháng")[["Số dư tiền mặt"]])

avg_burn = df_cf["Net Cash Flow"].mean()
runway = calculate_runway(initial_cash, avg_burn)

st.metric("Tiêu tiền hàng tháng trung bình", f"{avg_burn:,.0f}")
#st.metric("Estimated Runway (months)", "∞ (Không cần gọi vốn để tồn tại)" if runway == float("inf") else f"{runway:.1f}")
label = "∞ (Không cần gọi vốn để tồn tại)" if runway == float("inf") else f"{runway:.1f}"
st.markdown(f"<p style='font-size:18px'><b>Ước tính Runway (tháng):</b> {label}</p>", unsafe_allow_html=True)
