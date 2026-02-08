#!/usr/bin/env python
# coding: utf-8

# In[ ]:

import pandas as pd

def scenario_analysis(initial_cash, scenarios, months=24):
    results = {}

    for name, params in scenarios.items():
        cash = initial_cash
        revenue = params["revenue"]
        growth = params["growth"]
        fixed_cost = params["fixed_cost"]
        var_ratio = params["var_ratio"]

        data = []

        for m in range(1, months + 1):
            cost = fixed_cost + revenue * var_ratio
            net_cf = revenue - cost
            cash += net_cf

            data.append({
                "Month": m,
                "Cash Balance": cash,
                "Revenue": revenue,
                "Net Cash Flow": net_cf
            })

            revenue *= (1 + growth)

        results[name] = pd.DataFrame(data)

    return results



