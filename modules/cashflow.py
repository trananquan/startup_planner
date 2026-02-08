#!/usr/bin/env python
# coding: utf-8

# In[ ]:

import pandas as pd

def cash_flow_forecast(
    initial_cash,
    monthly_revenue,
    monthly_growth,
    fixed_cost,
    variable_cost_ratio,
    months=24
):
    data = []
    cash = initial_cash
    revenue = monthly_revenue

    for m in range(1, months + 1):
        variable_cost = revenue * variable_cost_ratio
        total_cost = fixed_cost + variable_cost
        net_cash_flow = revenue - total_cost
        cash += net_cash_flow

        data.append({
            "Month": m,
            "Revenue": revenue,
            "Total Cost": total_cost,
            "Net Cash Flow": net_cash_flow,
            "Cash Balance": cash
        })

        revenue *= (1 + monthly_growth)

    return pd.DataFrame(data)


def calculate_runway(initial_cash, burn_rate):
    if burn_rate >= 0:
        return float("inf")
    return initial_cash / abs(burn_rate)



