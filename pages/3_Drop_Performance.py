import streamlit as st
import matplotlib.pyplot as plt
from utils.load_data import load_all_data
from utils.filters import sidebar_filters

st.set_page_config(page_title="Drop Performance — Non-Foya", layout="wide")

st.title("Drop Performance")
st.caption("Compare drops by revenue and demand signals.")

data = load_all_data(data_path="data/mock")
filters = sidebar_filters(data)

orders = data["orders"]

if filters["brand"] != "All":
    orders = orders[orders["brand"] == filters["brand"]]

if filters["date_range"] is not None:
    start, end = filters["date_range"]
    orders = orders[(orders["order_datetime"].dt.date >= start) & (orders["order_datetime"].dt.date <= end)]

unique_orders = orders.drop_duplicates("order_id")

drop_rev = unique_orders.groupby("drop_name")["order_total_usd"].sum().sort_values(ascending=False)
st.subheader("Revenue by drop")
fig = plt.figure()
plt.bar(drop_rev.index.astype(str), drop_rev.values)
plt.xticks(rotation=30, ha="right")
plt.ylabel("Revenue (USD)")
st.pyplot(fig, clear_figure=True)

drop_orders = unique_orders.groupby("drop_name")["order_id"].nunique().sort_values(ascending=False)
st.subheader("Orders by drop")
fig2 = plt.figure()
plt.bar(drop_orders.index.astype(str), drop_orders.values)
plt.xticks(rotation=30, ha="right")
plt.ylabel("Orders")
st.pyplot(fig2, clear_figure=True)
