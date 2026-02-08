#!/usr/bin/env python
# coding: utf-8

# In[ ]:

import numpy as np

def break_even_point(fixed_cost, price, variable_cost):
    contribution_margin = price - variable_cost
    if contribution_margin <= 0:
        return None
    return fixed_cost / contribution_margin


# modules/finance.py
def extended_financial_ratios(
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
):
    ratios = {}

    # --------------------
    # PROFITABILITY
    # --------------------
    ratios["Gross Margin"] = (revenue - cogs) / revenue if revenue else 0
    ratios["Operating Margin"] = (revenue - cogs - operating_cost) / revenue if revenue else 0
    ratios["Net Profit Margin"] = net_profit / revenue if revenue else 0

    # --------------------
    # RETURN
    # --------------------
    ratios["ROA"] = net_profit / total_assets if total_assets else 0
    ratios["ROE"] = net_profit / equity if equity else 0

    # --------------------
    # EFFICIENCY
    # --------------------
    ratios["Asset Turnover"] = revenue / total_assets if total_assets else 0
    ratios["Cost-to-Revenue"] = total_cost / revenue if revenue else 0
    ratios["Operating Cost Ratio"] = operating_cost / revenue if revenue else 0

    # --------------------
    # LIQUIDITY
    # --------------------
    ratios["Current Ratio"] = current_assets / current_liabilities if current_liabilities else float("inf")
    ratios["Cash Ratio"] = cash / current_liabilities if current_liabilities else float("inf")

    # --------------------
    # SOLVENCY / LEVERAGE
    # --------------------
    ratios["Debt-to-Equity"] = total_debt / equity if equity else float("inf")
    ratios["Debt Ratio"] = total_debt / total_assets if total_assets else 0
    ratios["Equity Ratio"] = equity / total_assets if total_assets else 0

    return ratios


def financial_health_assessment(ratios):
    """
    Đánh giá sức khỏe tài chính theo 3 nhóm: Profitability, Liquidity, Leverage/Return
    Tổng điểm tối đa: 10
    """
    score = 0
    assessment = {}

    # --------------------
    # PROFITABILITY / EFFICIENCY
    # --------------------
    gm = ratios.get("Gross Margin", 0)
    ctr = ratios.get("Cost-to-Revenue", 1)

    if gm >= 0.4 and ctr <= 0.7:
        assessment["Profitability"] = "Strong"
        score += 2
    elif gm >= 0.25 and ctr <= 0.9:
        assessment["Profitability"] = "Acceptable"
        score += 1
    else:
        assessment["Profitability"] = "Weak"

    # --------------------
    # LIQUIDITY
    # --------------------
    cr = ratios.get("Current Ratio", 0)
    cash_ratio = ratios.get("Cash Ratio", 0)

    if cr >= 1.5 and cash_ratio >= 0.5:
        assessment["Liquidity"] = "Strong"
        score += 2
    elif cr >= 1 and cash_ratio >= 0.25:
        assessment["Liquidity"] = "Acceptable"
        score += 1
    else:
        assessment["Liquidity"] = "Weak"

    # --------------------
    # LEVERAGE / RISK
    # --------------------
    de = ratios.get("Debt-to-Equity", 0)
    debt_ratio = ratios.get("Debt Ratio", 0)

    if de <= 1 and debt_ratio <= 0.5:
        assessment["Leverage / Risk"] = "Strong"
        score += 2
    elif de <= 2 and debt_ratio <= 0.7:
        assessment["Leverage / Risk"] = "Acceptable"
        score += 1
    else:
        assessment["Leverage / Risk"] = "Weak"

    # --------------------
    # RETURN / EFFICIENCY CAPITAL
    # --------------------
    roe = ratios.get("ROE", 0)
    roa = ratios.get("ROA", 0)

    if roe >= 0.15 and roa >= 0.05:
        assessment["Return on Capital"] = "Strong"
        score += 2
    elif roe >= 0.05 and roa >= 0.02:
        assessment["Return on Capital"] = "Acceptable"
        score += 1
    else:
        assessment["Return on Capital"] = "Weak"

    return assessment, score
