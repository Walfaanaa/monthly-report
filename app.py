import streamlit as st
import pandas as pd
import requests
from io import BytesIO

st.set_page_config(page_title="EGSA Member Report", layout="wide")

# ================= LOGO =================

LOGO_URL = "https://raw.githubusercontent.com/Walfaanaa/monthly-report/main/EGSA.png"

st.markdown(
    f"""
    <div style="text-align:center;">
        <img src="{LOGO_URL}" width="250" style="border-radius:10px;">
    </div>
    """,
    unsafe_allow_html=True
)



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
    margin-bottom:15px;
}

.report-box {
    background-color: #1976d2;
    padding: 10px;
    border-radius: 10px;
    margin-top:15px;
}

.summary-box {
    background-color: #2e7d32;
    padding: 10px;
    border-radius: 10px;
    margin-top:15px;
}

div[data-testid="stMetric"] {
    background-color: #2e7d32;
    padding: 15px;
    border-radius: 10px;
}

div[data-testid="stMetric"] label,
div[data-testid="stMetric"] div {
    color:white !important;
}

[data-testid="stDataFrame"] * {
    color:black !important;
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
""",
unsafe_allow_html=True)



# ================= DATA SOURCE =================

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
    
    df["EGSA2027_Half_plan"] = pd.to_numeric(
        df["EGSA2027_Half_plan"],
        errors="coerce"
    ).fillna(0)

    df["EGSA2027_Half_achievement"] = pd.to_numeric(
        df["EGSA2027_Half_achievement"],
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



selected_ids = st.sidebar.multiselect(
    "Select Member ID",
    sorted(df["id"].unique())
)


# ================= FILTER =================

filtered_df = df.copy()

if len(date_range) == 2:

    start = pd.Timestamp(date_range[0])
    end = pd.Timestamp(date_range[1])

    filtered_df = filtered_df[
        (
            filtered_df["business_date"].between(start, end)
        )
        |
        (
            filtered_df["business_date"].isna()
        )
    ]


# ================= MEMBER SUMMARY =================

member_summary = filtered_df.groupby(
    ["id","Name"],
    as_index=False
).agg(

    EGSA2026_27_monthly_payment=
    (
        "EGSA2026_27_monthly_payment",
        "sum"
    ),

    End_2026_achievement=
    (
        "End_2026_achievement",
        "max"
    ),
    EGSA2027_Half_plan=
    (
        "EGSA2027_Half_plan",
        "sum"+168000
    ),
    EGSA2027_Half_achievement=
    (
        "EGSA2027_Half_achievement",
        "sum"+EGSA2026_27_monthly_payment
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
            "End_2026_achievement",
            "EGSA2027_Half_plan",
            "EGSA2027_Half_achievement"
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



total_monthly_payment = (
    member_summary["EGSA2026_27_monthly_payment"].sum()
)


total_achievement = (
    member_summary["End_2026_achievement"].sum()
)

total_half_plan = (
    member_summary["EGSA2027_Half_plan"].sum()
)

total_half_achieved = (
    member_summary["EGSA2027_Half_achievement"].sum()
)

total_collected = (
    total_monthly_payment
    +
    total_achievement
)



expected_amount = (
    TOTAL_MEMBERS
    *
    MONTHLY_TARGET
)



outstanding_amount = (
    expected_amount
    -
    total_monthly_payment
)



paid_members = member_summary[
    member_summary["EGSA2026_27_monthly_payment"] > 0
].shape[0]



unpaid_members = (
    TOTAL_MEMBERS
    -
    paid_members
)



# ================= METRICS =================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Monthly Payment Total",
        f"{total_monthly_payment:,.2f}"
    )

with col2:
    st.metric(
        "Expected Monthly",
        f"{expected_amount:,.2f}"
    )

with col3:
    st.metric(
        "Outstanding Monthly",
        f"{outstanding_amount:,.2f}"
    )

with col4:
    st.metric(
        "Paid Members",
        paid_members
    )


col5, col6, col7, col8 = st.columns(4)

with col5:
    st.metric(
        "End 2026 Achievement",
        f"{total_achievement:,.2f}"
    )

with col6:
    st.metric(
        "EGSA2027_Half_plan",
        f"{total_half_plan:,.2f}"
    )

with col7:
    st.metric(
        "EGSA2027_Half_achievement",
        f"{total_half_achieved:,.2f}"
    )

with col8:
    st.metric(
        "Unpaid Members",
        unpaid_members
    )


col9 = st.columns(1)[0]

with col9:
    st.metric(
        "Total Collected",
        f"{total_collected:,.2f}"
    )

# ================= UNPAID LIST =================

st.markdown("""
<div class="report-box">
<h3>Members Who Did Not Pay Monthly Contribution</h3>
</div>
""",
unsafe_allow_html=True)



unpaid_df = member_summary[
    member_summary["EGSA2026_27_monthly_payment"] == 0
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
