import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Monthly Member Report",
    layout="wide"
)

st.title("Monthly Member Report")

# GitHub raw Excel file URL
DATA_URL = "https://raw.githubusercontent.com/Walfaanaa/monthly-report/main/monthly_report.xlsx"

@st.cache_data
def load_data():
    df = pd.read_excel(DATA_URL)

    # Convert date column
    df["business_date"] = pd.to_datetime(
        df["business_date"],
        errors="coerce"
    )

    return df

df = load_data()

# Month Filter
months = sorted(
    df["business_date"].dt.strftime("%Y-%m").dropna().unique(),
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

c1.metric(
    "Members",
    report["id"].nunique()
)

c2.metric(
    "Monthly Payment",
    f"{report['monthly_payment'].sum():,.0f}"
)

c3.metric(
    "Total Payment",
    f"{report['total_payment'].sum():,.0f}"
)

st.subheader(f"Report for {selected_month}")

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

st.subheader("Top 10 Members by Total Payment")

top_members = (
    report.sort_values(
        "total_payment",
        ascending=False
    )
    .head(10)
    .set_index("Name")["total_payment"]
)

st.bar_chart(top_members)
