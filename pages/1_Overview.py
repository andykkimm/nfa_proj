import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from utils.load_data import load_all_data
from utils.filters import sidebar_filters
from utils.kpis import compute_kpis

st.set_page_config(page_title="Overview — Non-Foya", layout="wide")

st.title("Overview")
st.caption("High-level trends and breakdowns.")

data = load_all_data(data_path="data/mock")
filters = sidebar_filters(data)

orders = data["orders"]
products = data["products"]
inventory = data["inventory"]

if filters["brand"] != "All":
    orders = orders[orders["brand"] == filters["brand"]]
    products = products[products["brand"] == filters["brand"]]
    inventory = inventory[inventory["brand"] == filters["brand"]]

if filters["date_range"] is not None:
    start, end = filters["date_range"]
    orders = orders[(orders["order_datetime"].dt.date >= start) & (orders["order_datetime"].dt.date <= end)]

if filters["drop_name"] != "All":
    orders = orders[orders["drop_name"] == filters["drop_name"]]

if filters["category"] != "All":
    orders = orders[orders["product_category"] == filters["category"]]

if filters["product_name"] != "All":
    orders = orders[orders["product_name"] == filters["product_name"]]

kpis = compute_kpis(orders, products, inventory)
c1, c2, c3, c4 = st.columns(4)
c1.metric("Revenue", f"${kpis['revenue']:,.0f}")
c2.metric("Orders", f"{kpis['orders']:,}")
c3.metric("Avg Order Value", f"${kpis['aov']:,.2f}")
c4.metric("Repeat Customer Rate", f"{kpis['repeat_rate']*100:,.1f}%")

st.divider()

st.subheader("Revenue over time")
unique_orders = orders.drop_duplicates("order_id")
daily = unique_orders.groupby(unique_orders["order_datetime"].dt.date)["order_total_usd"].sum().reset_index()
daily.columns = ["date", "revenue_usd"]

fig = plt.figure()
plt.plot(pd.to_datetime(daily["date"]), daily["revenue_usd"])
plt.xlabel("Date")
plt.ylabel("Revenue (USD)")
st.pyplot(fig, clear_figure=True)

st.subheader("Revenue by category (order-level)")
cat = unique_orders.merge(orders[["order_id","product_category"]].drop_duplicates(), on="order_id", how="left")
cat_rev = cat.groupby("product_category")["order_total_usd"].sum().sort_values(ascending=False)

fig2 = plt.figure()
plt.bar(cat_rev.index.astype(str), cat_rev.values)
plt.xticks(rotation=30, ha="right")
plt.ylabel("Revenue (USD)")
st.pyplot(fig2, clear_figure=True)
