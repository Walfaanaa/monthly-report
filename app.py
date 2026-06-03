import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Monthly Member Report",
    layout="wide"
)

st.title("Monthly Member Report")

# GitHub raw file URL
DATA_URL = "https://raw.githubusercontent.com/yourname/monthly-report/main/monthly_report.csv"

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)
    df["business_date"] = pd.to_datetime(df["business_date"])
    return df

df = load_data()

# Month Filter
months = sorted(
    df["business_date"].dt.strftime("%Y-%m").unique(),
    reverse=True
)

selected_month = st.sidebar.selectbox(
    "Select Month",
    months
)

report = df[
    df["business_date"].dt.strftime("%Y-%m") == selected_month
]

# Summary
c1, c2, c3 = st.columns(3)

c1.metric("Members", report["id"].nunique())
c2.metric("Monthly Payment", f"{report['monthly_payment'].sum():,.0f}")
c3.metric("Total Payment", f"{report['total_payment'].sum():,.0f}")

st.dataframe(
    report[
        [
            "business_date",
            "id",
            "Name",
            "monthly_payment",
            "total_payment",
            "member_rank"
        ]
    ],
    use_container_width=True
)

st.subheader("Top Members")

st.bar_chart(
    report.sort_values(
        "total_payment",
        ascending=False
    ).head(10).set_index("Name")["total_payment"]
)