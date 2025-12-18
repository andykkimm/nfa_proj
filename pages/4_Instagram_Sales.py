import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from utils.load_data import load_all_data
from utils.filters import sidebar_filters

st.set_page_config(page_title="Instagram → Sales — Non-Foya", layout="wide")

st.title("Instagram → Sales Impact")
st.caption("How IG activity aligns with sales over time (descriptive, not causal).")

data = load_all_data(data_path="data/mock")
filters = sidebar_filters(data)

orders = data["orders"]
ig_posts = data["ig_posts"]

if filters["brand"] != "All":
    orders = orders[orders["brand"] == filters["brand"]]
    ig_posts = ig_posts[ig_posts["brand"] == filters["brand"]]

if filters["date_range"] is not None:
    start, end = filters["date_range"]
    orders = orders[(orders["order_datetime"].dt.date >= start) & (orders["order_datetime"].dt.date <= end)]
    ig_posts = ig_posts[(ig_posts["post_datetime"].dt.date >= start) & (ig_posts["post_datetime"].dt.date <= end)]

unique_orders = orders.drop_duplicates("order_id")
sales_daily = unique_orders.groupby(unique_orders["order_datetime"].dt.date)["order_total_usd"].sum().reset_index()
sales_daily.columns = ["date", "revenue_usd"]

ig_daily = ig_posts.groupby(ig_posts["post_datetime"].dt.date)[["reach","impressions","likes","saves","shares"]].sum().reset_index()
ig_daily.columns = ["date","reach","impressions","likes","saves","shares"]

merged = pd.merge(sales_daily, ig_daily, on="date", how="left").fillna(0)

st.subheader("Revenue vs Reach (daily)")
fig = plt.figure()
plt.plot(pd.to_datetime(merged["date"]), merged["revenue_usd"], label="Revenue")
plt.plot(pd.to_datetime(merged["date"]), merged["reach"], label="Reach")
plt.xlabel("Date")
plt.legend()
st.pyplot(fig, clear_figure=True)

st.subheader("Correlation with revenue")
corrs = merged[["revenue_usd","reach","impressions","likes","saves","shares"]].corr(numeric_only=True)["revenue_usd"].drop("revenue_usd").sort_values(ascending=False)
st.dataframe(corrs.reset_index().rename(columns={"index":"metric","revenue_usd":"corr_with_revenue"}), hide_index=True, use_container_width=True)

st.warning("Reminder: correlation does NOT prove Instagram caused sales. Use this to form hypotheses and test campaigns.")
