#!/usr/bin/env python
# coding: utf-8

# In[ ]:


def unit_economics(arpu, cac, churn, gross_margin):
    """
    Tính các chỉ số Unit Economics cơ bản và nâng cao
    """
    ltv = arpu * gross_margin / churn if churn else 0
    ltv_cac = ltv / cac if cac else float("inf")
    payback = cac / (arpu * gross_margin) if (arpu * gross_margin) else float("inf")
    net_unit_profit = ltv - cac
    
    return {
        "ARPU": round(arpu, 2),
        "CAC": round(cac, 2),
        "LTV": round(ltv, 2),
        "LTV/CAC": round(ltv_cac, 2),
        "Payback (tháng)": round(payback, 1),
        "Net Unit Profit": round(net_unit_profit, 2),
        "Churn": churn,
        "Gross Margin": gross_margin
    }


def assess_unit_economics(ue):
    ltv_cac = ue["LTV/CAC"]
    payback = ue["Payback (tháng)"]
    gross_margin = ue["Gross Margin"]
    churn = ue["Churn"]

    if (
        ltv_cac >= 3
        and payback <= 12
        and gross_margin >= 0.5
        and churn <= 0.08
    ):
        assessment = "✅ RẤT KHẢ THI"
        color = "success"

    elif (
        ltv_cac >= 2
        and payback <= 18
        and gross_margin >= 0.3
        and churn <= 0.15
    ):
        assessment = "⚠ CHẤP NHẬN ĐƯỢC (Early-stage)"
        color = "warning"

    else:
        assessment = "❌ RỦI RO CAO"
        color = "error"

    return assessment, color

def unit_economics_recommendations(ue):
    suggestions = []

    ltv_cac = ue["LTV/CAC"]
    payback = ue["Payback (tháng)"]
    churn = ue["Churn"]
    gross_margin = ue["Gross Margin"]
    net_profit = ue["Net Unit Profit"]

    # 1. LTV / CAC
    if ltv_cac < 1:
        suggestions.append("🚨 Mô hình đang đốt tiền trên mỗi khách hàng (LTV < CAC). Cần dừng scale và tái cấu trúc ngay.")
    elif ltv_cac < 3:
        suggestions.append("⚠️ LTV/CAC thấp. Ưu tiên **giảm CAC** (kênh acquisition, tối ưu funnel) trước khi scale.")
    else:
        suggestions.append("✅ LTV/CAC tốt. Có thể xem xét **tăng ngân sách marketing để scale**.")

    # 2. Payback Period
    if payback > 12:
        suggestions.append("⏳ Thời gian hoàn vốn CAC dài (>12 tháng). Rủi ro dòng tiền cao → cần cải thiện retention hoặc pricing.")
    elif payback > 6:
        suggestions.append("⚠️ Payback ở mức trung bình. Theo dõi chặt dòng tiền khi mở rộng.")
    else:
        suggestions.append("⚡ Hoàn vốn CAC nhanh → phù hợp tăng trưởng nhanh.")

    # 3. Churn
    if churn > 0.1:
        suggestions.append("🔥 Churn cao. Cần tập trung vào **product-market fit**, onboarding và customer success.")
    elif churn > 0.05:
        suggestions.append("⚠️ Churn trung bình. Có thể cải thiện bằng loyalty, subscription hoặc upsell.")
    else:
        suggestions.append("💎 Churn thấp. Lợi thế lớn để tăng LTV dài hạn.")

    # 4. Gross Margin
    if gross_margin < 0.4:
        suggestions.append("📉 Biên lợi nhuận thấp. Cần tối ưu chi phí biến đổi hoặc tăng giá trị sản phẩm.")
    elif gross_margin < 0.6:
        suggestions.append("⚠️ Biên lợi nhuận ổn nhưng chưa mạnh. Tăng hiệu quả vận hành & tự động hóa.")
    else:
        suggestions.append("🏆 Biên lợi nhuận cao. Phù hợp mô hình scale bằng vốn.")

    # 5. Net unit profit
    if net_profit < 0:
        suggestions.append("❌ Lợi nhuận đơn vị âm. Tuyệt đối không scale cho tới khi sửa được economics.")
    else:
        suggestions.append("💰 Mỗi khách hàng tạo lợi nhuận ròng. Có thể mở rộng quy mô có kiểm soát.")

    return suggestions



