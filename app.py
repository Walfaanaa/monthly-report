import streamlit as st
import pandas as pd
import requests
from io import BytesIO

st.set_page_config(page_title="EGSA Member Report", layout="wide")


# ================= CSS =================
st.markdown("""
<style>

[data-testid="stAppViewContainer"] {
    background-color: white;
}

section[data-testid="stSidebar"] {
    background-color: #6a0dad;
}

section[data-testid="stSidebar"] * {
    color: white !important;
}

[data-testid="stDateInput"] input {
    color: black !important;
    -webkit-text-fill-color: black !important;
    font-weight: bold !important;
}

.stMultiSelect div {
    color: black !important;
}

.header-box {
    background-color: #d32f2f;
    padding: 15px;
    border-radius: 10px;
}

.report-box {
    background-color: #1976d2;
    padding: 10px;
    border-radius: 10px;
}

.summary-box {
    background-color: #2e7d32;
    padding: 10px;
    border-radius: 10px;
}

div[data-testid="stMetric"] {
    background-color: #2e7d32;
    padding: 15px;
    border-radius: 10px;
}

div[data-testid="stMetric"] label,
div[data-testid="stMetric"] div {
    color: white !important;
}

[data-testid="stDataFrame"] * {
    color: black !important;
}

h1,h2,h3 {
    color:white;
}

</style>
""", unsafe_allow_html=True)


# ================= HEADER =================
st.markdown("""
<div class="header-box">
<h1>EGSA 2026/27 Member Report Dashboard</h1>
</div>
""", unsafe_allow_html=True)


# ================= DATA =================

DATA_URL = "https://raw.githubusercontent.com/Walfaanaa/monthly-report/main/EGSA2026_27_Monthly_report.xlsx"


@st.cache_data
def load_data():

    response = requests.get(DATA_URL)
    response.raise_for_status()

    df = pd.read_excel(
        BytesIO(response.content),
        engine="openpyxl"
    )

    df.columns = df.columns.str.strip()

    df["business_date"] = pd.to_datetime(
        df["business_date"],
        errors="coerce"
    )

    df["id"] = df["id"].astype(str)

    df["EGSA2026_27_monthly_payment"] = pd.to_numeric(
        df["EGSA2026_27_monthly_payment"],
        errors="coerce"
    ).fillna(0)

    df["End_2026_achievement"] = pd.to_numeric(
        df["End_2026_achievement"],
        errors="coerce"
    ).fillna(0)


    return df


df = load_data()


# ================= SIDEBAR =================

st.sidebar.header("Filters")


date_range = st.sidebar.date_input(
    "Business Date Range",
    value=[
        df["business_date"].min(),
        df["business_date"].max()
    ]
)


member_list = sorted(df["id"].unique())


selected_ids = st.sidebar.multiselect(
    "Select Member ID",
    member_list
)


# ================= FILTER =================

filtered_df = df.copy()


if len(date_range)==2:

    filtered_df = filtered_df[
        (filtered_df["business_date"] >= pd.Timestamp(date_range[0]))
        &
        (filtered_df["business_date"] <= pd.Timestamp(date_range[1]))
    ]



# ================= MEMBER SUMMARY =================

member_summary = filtered_df.groupby(
    ["id","Name"],
    as_index=False
).agg(

    EGSA2026_27_monthly_payment=(
        "EGSA2026_27_monthly_payment",
        "sum"
    ),

    End_2026_achievement=(
        "End_2026_achievement",
        "max"
    )

)


if selected_ids:

    member_summary = member_summary[
        member_summary["id"].isin(selected_ids)
    ]



# ================= REPORT =================

st.markdown("""
<div class="report-box">
<h3>Member Payment Report</h3>
</div>
""",
unsafe_allow_html=True)



st.dataframe(

    member_summary[
        [
        "id",
        "Name",
        "EGSA2026_27_monthly_payment",
        "End_2026_achievement"
        ]
    ],

    use_container_width=True,
    hide_index=True

)



# ================= SUMMARY =================


st.markdown("""
<div class="summary-box">
<h3>Summary</h3>
</div>
""",
unsafe_allow_html=True)



TOTAL_MEMBERS = df["id"].nunique()

MONTHLY_TARGET = 1000


col1,col2,col3 = st.columns(3)


with col1:

    st.metric(
        "Total Collected",
        f"{member_summary['EGSA2026_27_monthly_payment'].sum():,.2f}"
    )


with col2:

    expected = TOTAL_MEMBERS * MONTHLY_TARGET

    st.metric(
        "Expected Amount",
        f"{expected:,.2f}"
    )


with col3:

    unpaid = (
        expected -
        member_summary["EGSA2026_27_monthly_payment"].sum()
    )

    st.metric(
        "Outstanding Amount",
        f"{unpaid:,.2f}"
    )



col4,col5,col6 = st.columns(3)


with col4:

    st.metric(
        "No. of Members",
        TOTAL_MEMBERS
    )


with col5:

    paid_members = (
        member_summary[
            member_summary[
                "EGSA2026_27_monthly_payment"
            ]>0
        ]
        .shape[0]
    )


    st.metric(
        "Paid Members",
        paid_members
    )


with col6:

    st.metric(
        "Unpaid Members",
        TOTAL_MEMBERS-paid_members
    )



# ================= UNPAID MEMBERS =================


st.markdown("""
<div class="report-box">
<h3>Members Who Did Not Pay</h3>
</div>
""",
unsafe_allow_html=True)



unpaid_df = member_summary[
    member_summary[
        "EGSA2026_27_monthly_payment"
    ]==0
]


st.dataframe(

    unpaid_df[
        [
        "id",
        "Name"
        ]
    ],

    use_container_width=True,
    hide_index=True

)
