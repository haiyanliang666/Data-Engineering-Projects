from __future__ import annotations

import os

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine


def _engine():
    url = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://retail:retail@localhost:5432/retail",
    )
    return create_engine(url)


st.set_page_config(page_title="E-Commerce Sales Dashboard", layout="wide")
st.title("E-Commerce Sales Dashboard")

engine = _engine()

daily_revenue = pd.read_sql("SELECT * FROM vw_daily_revenue ORDER BY full_date", engine)
weekly_revenue = pd.read_sql("SELECT * FROM vw_weekly_revenue ORDER BY year, week", engine)
top_products = pd.read_sql(
    "SELECT * FROM vw_top_products ORDER BY revenue DESC LIMIT 20",
    engine,
)
monthly_growth = pd.read_sql("SELECT * FROM vw_monthly_growth ORDER BY year, month", engine)

left, right = st.columns(2)
with left:
    st.subheader("Daily Revenue")
    st.line_chart(daily_revenue, x="full_date", y="revenue")
with right:
    st.subheader("Weekly Revenue")
    st.bar_chart(weekly_revenue, x="week", y="revenue")

st.subheader("Top Products")
st.dataframe(top_products, use_container_width=True)

st.subheader("Monthly Growth")
st.dataframe(monthly_growth, use_container_width=True)
