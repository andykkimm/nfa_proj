import streamlit as st
import matplotlib.pyplot as plt
from utils.load_data import load_all_data
from utils.filters import sidebar_filters

st.set_page_config(page_title="Customers — Non-Foya", layout="wide")

st.title("Customers")
st.caption("Repeat purchase behavior and customer health signals.")

data = load_all_data(data_path="data/mock")
filters = sidebar_filters(data)

orders = data["orders"]

if filters["brand"] != "All":
    orders = orders[orders["brand"] == filters["brand"]]

if filters["date_range"] is not None:
    start, end = filters["date_range"]
    orders = orders[(orders["order_datetime"].dt.date >= start) & (orders["order_datetime"].dt.date <= end)]

unique_orders = orders.drop_duplicates("order_id").copy()

cust_orders = unique_orders.groupby("customer_id")["order_id"].nunique().reset_index(name="num_orders")
repeat_rate = (cust_orders["num_orders"] >= 2).mean() if len(cust_orders) else 0.0

c1, c2 = st.columns(2)
c1.metric("Unique customers", f"{cust_orders.shape[0]:,}")
c2.metric("Repeat customer rate", f"{repeat_rate*100:,.1f}%")

st.subheader("Orders per customer")
counts = cust_orders["num_orders"].value_counts().sort_index()

fig = plt.figure()
plt.bar(counts.index.astype(str), counts.values)
plt.xlabel("Orders per customer")
plt.ylabel("Customers")
st.pyplot(fig, clear_figure=True)
