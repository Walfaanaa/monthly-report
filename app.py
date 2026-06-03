import streamlit as st
import pandas as pd
import requests
from io import BytesIO

st.set_page_config(
    page_title="Monthly Member Report",
    layout="wide"
)

st.title("Monthly Member Report")

# GitHub Raw Excel URL
DATA_URL = "https://raw.githubusercontent.com/Walfaanaa/monthly-report/main/monthly_report.xlsx"


@st.cache_data
def load_data():
    response = requests.get(DATA_URL)
    response.raise_for_status()

    df = pd.read_excel(
        BytesIO(response.content),
        engine="openpyxl"
    )

    df["business_date"] = pd.to_datetime(
        df["business_date"],
        errors="coerce"
    )

    # Keep records from 25-May-2026 onward
    df = df[
        df["business_date"] >= pd.Timestamp("2026-05-25")
    ]

    return df


df = load_data()

if df.empty:
    st.warning("No records found after 2026-05-25.")
    st.stop()

# Sidebar Month Filter
months = sorted(
    df["business_date"]
      .dt.strftime("%Y-%m")
      .dropna()
      .unique(),
    reverse=True
)

selected_month = st.sidebar.selectbox(
    "Select Month",
    months
)

report = df[
    df["business_date"].dt.strftime("%Y-%m")
    == selected_month
]

# Summary Metrics
st.subheader(f"Summary Report : {selected_month}")

c1, c2, c3 = st.columns(3)

with c1:
    st.metric(
        "Total Members",
        report["id"].nunique()
    )

with c2:
    st.metric(
        "Monthly Payment",
        f"{report['monthly_payment'].sum():,.2f}"
    )

with c3:
    st.metric(
        "Total Payment",
        f"{report['total_payment'].sum():,.2f}"
    )

# Detail Table
st.subheader("Member Details")

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
    ].sort_values(
        "member_rank"
    ),
    use_container_width=True,
    hide_index=True
)

# Top 10 Members
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

# Download Button
csv = report.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Report",
    data=csv,
    file_name=f"monthly_report_{selected_month}.csv",
    mime="text/csv"
)
