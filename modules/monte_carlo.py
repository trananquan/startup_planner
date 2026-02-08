#!/usr/bin/env python
# coding: utf-8

# In[ ]:

import numpy as np

def monte_carlo_profit(
    n_simulations,
    price_mean, price_std,
    demand_mean, demand_std,
    fixed_cost, variable_cost
):
    price = np.random.normal(price_mean, price_std, n_simulations)
    demand = np.random.normal(demand_mean, demand_std, n_simulations)

    revenue = price * demand
    total_cost = fixed_cost + variable_cost * demand
    profit = revenue - total_cost

    return profit


