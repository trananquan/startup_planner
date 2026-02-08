#!/usr/bin/env python
# coding: utf-8

# In[ ]:

import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Strategy & Market Fit", layout="wide")

st.header("🧭 Phân tích chiến lược & mức độ phù hợp thị trường")

# =====================================================
# 1️⃣ MARKET SIZE: TAM - SAM - SOM
# =====================================================
st.subheader("1️⃣ Mô hình phân tích dung lượng thị trường (TAM – SAM – SOM)")

col1, col2 = st.columns(2)

with col1:
    total_customers = st.number_input("Tổng số khách hàng tiềm năng (TAM – số lượng)",min_value=0)
    arpu = st.number_input("Doanh thu trung bình mỗi khách hàng / năm (ARPU)",min_value=0.0)

with col2:
    sam_ratio = st.slider("Tỷ lệ phân khúc mục tiêu (SAM %)",0, 100, 30) / 100
    som_ratio = st.slider("Thị phần có thể đạt được (SOM %)",0, 100, 10) / 100

# Market size calculation
TAM = total_customers * arpu
SAM = TAM * sam_ratio
SOM = SAM * som_ratio

st.subheader("📊 Kết quả ước tính dung lượng thị trường")

c1, c2, c3 = st.columns(3)
c1.metric("TAM – Tổng thị trường", f"${TAM:,.0f}")
c2.metric("SAM – Thị trường mục tiêu", f"${SAM:,.0f}")
c3.metric("SOM – Thị phần khả thi", f"${SOM:,.0f}")

# Visualization
df_market = pd.DataFrame({"Phân loại": ["TAM", "SAM", "SOM"],"Giá trị": [TAM, SAM, SOM]})
fig_market = px.bar(df_market,x="Phân loại",y="Giá trị",title="So sánh quy mô TAM – SAM – SOM")

st.plotly_chart(fig_market, use_container_width=True)

st.divider()
# =====================================================
# 2️⃣ PRODUCT – MARKET FIT (PMF) | INVESTOR-GRADE

st.subheader("2️⃣ Đánh giá mức độ phù hợp thị trường của sản phẩm (PMF)")
st.caption("PMF được đánh giá theo 3 trụ cột: Giá trị sử dụng – Cảm xúc khách hàng – Hiệu quả kinh tế")

# =====================================================
# 🔹 1. VALUE FIT – HÀNH VI SỬ DỤNG
# =====================================================
st.subheader("🔹 Value Fit – Giá trị sử dụng thực tế")

col1, col2 = st.columns(2)

with col1:
    retention_90d = st.slider("Tỷ lệ giữ chân sau 90 ngày (%)",0, 100, 40) / 100

with col2:
    repeat_usage = st.slider("Tỷ lệ người dùng quay lại thường xuyên (%)",0, 100, 50) / 100

value_fit_score = (0.6 * retention_90d + 0.4 * repeat_usage) * 100

st.metric("Điểm Value Fit", f"{value_fit_score:.1f}/100")

# 🔹 2. EMOTIONAL FIT – SEAN ELLIS PMF TEST

st.subheader("🔹 Emotional Fit – Sean Ellis Test")
st.caption("Nếu không thể sử dụng sản phẩm này nữa, khách hàng sẽ cảm thấy thế nào?")

col3, col4 = st.columns(2)

with col3:
     very_disappointed = st.slider("Rất thất vọng (%)",0, 100, 30) / 100
with col4:
     somewhat_disappointed = st.slider("Hơi thất vọng (%)",0, 100, 40) / 100

not_disappointed = max(0,1 - very_disappointed - somewhat_disappointed)

emotional_fit_score = very_disappointed * 100

st.metric("Điểm Emotional Fit",f"{emotional_fit_score:.1f}/100")

# 🔹 3. ECONOMIC FIT – HIỆU QUẢ KINH TẾ

st.subheader("🔹 Economic Fit – Hiệu quả kinh tế")

col5, col6 = st.columns(2)

with col5:
    organic_revenue_growth = st.slider("Tăng trưởng doanh thu tự nhiên (%)",0, 100, 10) / 100

with col6:
    ltv_cac_ratio = st.slider("Tỷ lệ LTV / CAC",0.0, 10.0, 2.5)

economic_fit_score = (0.5 * organic_revenue_growth +0.5 * min(ltv_cac_ratio / 3, 1)) * 100

st.metric("Điểm Economic Fit", f"{economic_fit_score:.1f}/100")

# =====================================================
# 🎯 4. PMF MASTER SCORE
# =====================================================
st.subheader("🎯 Tổng hợp Product–Market Fit")

PMF_master_score = (0.4 * value_fit_score +0.35 * emotional_fit_score +0.25 * economic_fit_score)

st.metric("PMF Score tổng hợp", f"{PMF_master_score:.1f}/100")

# 🚦 5. PMF VERDICT ENGINE
# =====================================================
if emotional_fit_score >= 40 and value_fit_score >= 60 and economic_fit_score >= 60:
    st.success("🚀 STRONG PMF – Có thể scale có kiểm soát")
    pmf_stage = "Scale-ready"
elif value_fit_score >= 50 and emotional_fit_score >= 30:
    st.warning("🟡 PARTIAL PMF – Cần tối ưu sản phẩm trước khi scale")
    pmf_stage = "Optimize"
else:
    st.error("🔴 WEAK PMF – Chưa phù hợp thị trường")
    pmf_stage = "Fix"

# 🧭 6. ACTIONABLE STRATEGIC INSIGHTS
st.subheader("🧭 Gợi ý hành động chiến lược")

actions = []

if retention_90d < 0.4:
    actions.append("🔧 Cải thiện core value và onboarding để tăng retention")

if very_disappointed < 0.4:
    actions.append("🎯 Làm rõ ICP và pain point chính của khách hàng")

if ltv_cac_ratio < 3:
    actions.append("💰 Tối ưu pricing, packaging hoặc giảm CAC")

if organic_revenue_growth < 0.05:
    actions.append("📣 Đẩy mạnh referral, word-of-mouth và usage loop")

if not actions:
    actions.append("✅ Có thể bắt đầu scale từng kênh với ngân sách kiểm soát")

for action in actions:
    st.write(action)

st.divider()
# 3️⃣ HIỆU QUẢ CHIẾN LƯỢC TĂNG TRƯỞNG – GROWTH ENGINE
# =====================================================
st.subheader(" 3️⃣ Hiệu quả chiến lược tăng trưởng (Growth Strategy)")

# -------- Sliders đơn giản --------
col1, col2 = st.columns(2)

with col1:
    revenue_growth_rate = st.slider("Tăng trưởng doanh thu hàng tháng (%)", 0, 100, 10) / 100
    organic_ratio = st.slider("Tỷ lệ tăng trưởng tự nhiên (Organic %)", 0, 100, 60) / 100

with col2:
    cac_growth_rate = st.slider("Tốc độ tăng CAC (%)", 0, 100, 5) / 100
    burn_rate_pressure = st.slider("Áp lực burn rate (0 = thấp, 100 = cao)", 0, 100, 50) / 100

# -------- Tính score tổng hợp --------
# Growth Score = Weighted sum 3 trục: Quality, Efficiency, Risk
growth_master_score = (
    0.4*(0.6*revenue_growth_rate + 0.4*organic_ratio)*100 +  # Growth Quality
    0.4*min(revenue_growth_rate/max(cac_growth_rate,0.01),1)*100 +  # Efficiency
    0.2*(1-burn_rate_pressure)*100  # Risk control
)

st.metric("Growth Strategy Score", f"{growth_master_score:.1f}/100")

# -------- Verdict đơn giản --------
if growth_master_score >= 70:
    st.success("🚀 Tăng trưởng hiệu quả – Có thể scale")
    growth_stage = "Scale"
elif growth_master_score >= 50:
    st.warning("🟡 Tăng trưởng trung bình – Cần tối ưu")
    growth_stage = "Optimize"
else:
    st.error("🔴 Tăng trưởng rủi ro – Không nên scale")
    growth_stage = "Hold"

# -------- Actionable Insights --------
st.markdown("#### 🧭 Gợi ý hành động tăng trưởng")
growth_actions = []

if organic_ratio < 0.5:
    growth_actions.append("📣 Tăng referral & organic growth")
if cac_growth_rate > revenue_growth_rate:
    growth_actions.append("💸 CAC tăng nhanh hơn doanh thu – tối ưu funnel")
if burn_rate_pressure > 0.6:
    growth_actions.append("🔥 Kiểm soát burn rate trước khi scale")
if not growth_actions:
    growth_actions.append("✅ Chiến lược tăng trưởng ổn định")

for a in growth_actions:
    st.write(a)
