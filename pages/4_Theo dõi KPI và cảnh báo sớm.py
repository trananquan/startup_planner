#!/usr/bin/env python
# coding: utf-8

# In[ ]:

# =====================================================
# PAGE 4 – KPI DYNAMIC COMPARISON (VIỆT HÓA)
# =====================================================
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.title("📈 Theo dõi KPI & cảnh báo sớm")
st.header("1️⃣💾 Theo dõi KPI đa chỉ tiêu")

uploaded_file = st.file_uploader("Tải lên file CSV", type=["csv"])

if uploaded_file:
    # ==============================
    # LOAD DATA
    # ==============================
    df = pd.read_csv(uploaded_file, parse_dates=["date"])
    df = df.sort_values("date").reset_index(drop=True)

    st.subheader("📄 Dữ liệu gốc")
    st.dataframe(df)

    # ==============================
    # PHÁT HIỆN CÁC TRƯỜNG DỮ LIỆU SỐ
    # ==============================
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    if not numeric_cols:
        st.error("❌ File không có trường dữ liệu dạng số để phân tích.")
        st.stop()

    # ==============================
    # LỰA CHỌN KPI
    # ==============================
    st.subheader("📊 Chọn KPI để phân tích")

    kpi = st.selectbox("Chọn trường dữ liệu", numeric_cols)

    # ==============================
    # BIỂU ĐỒ KPI
    # ==============================
    fig = px.line(
        df,
        x="date",
        y=kpi,
        markers=True,
        title=f"{kpi} theo thời gian"
    )
    st.plotly_chart(fig, use_container_width=True)

    # ==============================
    # BẢNG SO SÁNH GIỮA CÁC GIAI ĐOẠN
    # ==============================
    st.subheader("🔁 Bảng so sánh giữa các giai đoạn")

    period = st.selectbox(
        "Chọn chu kỳ so sánh",
        [1, 3, 6, 12],
        format_func=lambda x: f"{x} kỳ gần nhất"
    )

    df["Giá trị trước"] = df[kpi].shift(period)
    df["Tăng tuyệt đối"] = df[kpi] - df["Giá trị trước"]
    df["Tăng tương đối (%)"] = df["Tăng tuyệt đối"] / df["Giá trị trước"].replace(0, np.nan) * 100
    comparison_table = df[["date", kpi, "Giá trị trước", "Tăng tuyệt đối", "Tăng tương đối (%)"]].rename(columns={"date": "Ngày"})

    st.write("📋 Bảng so sánh tăng trưởng")
    st.dataframe(comparison_table.style.format({
        kpi: "{:.2f}",
        "Giá trị liền trước": "{:.2f}",
        "Tăng tuyệt đối": "{:.2f}",
        "Tăng tương đối (%)": "{:.2f}%"
    }))

    # ==============================
    # BẢNG KPI SUMMARY
    # ==============================
    st.subheader("📌 Bảng tóm tắt KPI")

    summary = pd.DataFrame({
        "Giá trị mới nhất": [df[kpi].iloc[-1]],
        "Trung bình": [df[kpi].mean()],
        "Tốt nhất": [df[kpi].max()],
        "Tệ nhất": [df[kpi].min()]
    }, index=[kpi])

    st.table(summary.style.format("{:.2f}"))

    # ==============================
    # CẢNH BÁO SỚM
    # ==============================
    st.subheader("🚨 Cảnh báo sớm")

    alerts = []

    latest = df[kpi].iloc[-1]
    avg = df[kpi].mean()

    if latest < avg:
        alerts.append(f"📉 {kpi} hiện tại thấp hơn mức trung bình lịch sử.")

    if "Tăng tương đối (%)" in df.columns:
        recent_change = df["Tăng tương đối (%)"].iloc[-1]
        if recent_change < 0:
            alerts.append(f"🔻 {kpi} đang giảm so với kỳ trước ({recent_change:.2f}%).")

    if alerts:
        for a in alerts:
            st.error(a)
    else:
        st.success("✅ Không có tín hiệu cảnh báo nghiêm trọng.")

# ==============================
# MULTI-KPI COMPARISON
# ==============================
    st.subheader("📊 So sánh giữa các chỉ tiêu KPI")

    multi_kpi = st.multiselect(
    "Chọn các chỉ tiêu KPI để so sánh",
    numeric_cols,
    default=[kpi]
    )

    if multi_kpi:
    # Vẽ biểu đồ nhiều KPI
       fig_multi = px.line(
        df,
        x="date",
        y=multi_kpi,
        markers=True,
        title="So sánh nhiều KPI theo thời gian"
    )
       fig_multi.update_layout(xaxis_title="Ngày")
       st.plotly_chart(fig_multi, use_container_width=True)

# ==============================
# KPI THEO MỤC TIÊU
# ==============================
st.header("2️⃣🎯 So sánh KPI với mục tiêu")

target_file = st.file_uploader("Upload KPI mục tiêu CSV (cùng cột KPI)", type=["csv"], key="target")

if target_file:
    df_target = pd.read_csv(target_file)
    
    # Tự động map các KPI chung
    common_kpi = list(set(df_target.columns).intersection(set(numeric_cols)))
    
    if not common_kpi:
        st.warning("⚠️ Không tìm thấy KPI chung giữa dữ liệu gốc và file mục tiêu.")
    else:
        st.write(f"✅ KPI chung để so sánh: {', '.join(common_kpi)}")

        # Chia cột 2 cột
        col1, col2 = st.columns(2)

        for i, k in enumerate(common_kpi):
            latest_value = df[k].iloc[-1]
            target_value = df_target[k].iloc[-1]
            pct_achieved = min(latest_value / target_value * 100, 100)

            # Chọn cột
            col = col1 if i % 2 == 0 else col2

            with col:
                st.markdown(f"**{k}**: {latest_value:.2f} / {target_value:.2f} ({pct_achieved:.1f}%)")

                import plotly.graph_objects as go
                fig_gauge = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=pct_achieved,
                    number={'suffix': "%"},
                    gauge={'axis': {'range': [0, 100]},
                           'bar': {'color': "green" if pct_achieved >= 100 else "orange"},
                           'steps': [
                               {'range': [0, 50], 'color': "red"},
                               {'range': [50, 100], 'color': "yellow"}
                           ]},
                    title={'text': f"{k} đạt KPI (%)"}
                ))
                st.plotly_chart(fig_gauge, use_container_width=True)
        # ==============================
        # Stacked column chart cho tất cả KPI
        # ==============================
        achieved = [min(df[k].iloc[-1], df_target[k].iloc[-1]) for k in common_kpi]
        remaining = [df_target[k].iloc[-1] - min(df[k].iloc[-1], df_target[k].iloc[-1]) for k in common_kpi]

        df_stack = pd.DataFrame({
            "KPI": common_kpi,
            "Đạt được": achieved,
            "Còn thiếu": remaining
        })

        fig_stack = px.bar(
            df_stack,
            x="KPI",
            y=["Đạt được", "Còn thiếu"],
            title="So sánh KPI hiện tại với mục tiêu",
            text_auto=True
        )
        st.plotly_chart(fig_stack, use_container_width=True)

