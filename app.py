import streamlit as st
import pandas as pd
from html import escape

from database import (
    create_database,
    add_transaction,
    get_transactions,
    delete_transaction,
    clear_transactions,
)
from categorizer import categorize_transaction


# ==================================================
# PAGE SETTINGS
# ==================================================

st.set_page_config(
    page_title="MoneyLeak",
    page_icon="💸",
    layout="wide",
)

create_database()


# ==================================================
# THEME
# ==================================================

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

dark_mode = st.toggle(
    "Dark mode",
    value=st.session_state.dark_mode,
)

st.session_state.dark_mode = dark_mode

EMERALD = "#0B6B50"
GOLD = "#C9A227"

if dark_mode:
    BACKGROUND = "#0D1914"
    CARD = "#17271F"
    TEXT = "#F8F3E7"
    MUTED = "#AAB8AF"
    BORDER = "#304638"
else:
    BACKGROUND = "#F8F3E7"
    CARD = "#FFFDF7"
    TEXT = "#17271F"
    MUTED = "#66756B"
    BORDER = "#E5DDCA"


st.markdown(
    f"""
    <style>
        .stApp {{
            background: {BACKGROUND};
            color: {TEXT};
        }}

        .block-container {{
            max-width: 1250px;
            padding-top: 2rem;
            padding-bottom: 4rem;
        }}

        [data-testid="stHeader"] {{
            background: transparent;
        }}

        h1, h2, h3, p, label {{
            color: {TEXT};
        }}

        .brand {{
            color: {GOLD};
            font-size: 36px;
            font-weight: 800;
            letter-spacing: -1px;
        }}

        .subtitle {{
            color: {MUTED};
            font-size: 15px;
            margin-bottom: 25px;
        }}

        .metric-card {{
            background: {CARD};
            border: 1px solid {BORDER};
            border-radius: 18px;
            padding: 25px;
            margin-bottom: 15px;
        }}

        .metric-label {{
            color: {MUTED};
            font-size: 13px;
            font-weight: 600;
            margin-bottom: 10px;
        }}

        .metric-value {{
            color: {TEXT};
            font-size: 29px;
            font-weight: 800;
        }}

        .gold-line {{
            height: 2px;
            background: {GOLD};
            margin: 20px 0 30px;
        }}

        div.stButton > button[kind="primary"] {{
            background: {EMERALD};
            border-color: {EMERALD};
            color: white;
        }}

        div.stButton > button {{
            border-radius: 10px;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ==================================================
# HEADER
# ==================================================

st.markdown(
    '<div class="brand">MoneyLeak</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">Know where your money goes.</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="gold-line"></div>',
    unsafe_allow_html=True,
)


# ==================================================
# DASHBOARD
# ==================================================

transactions = get_transactions()

total_spent = sum(
    max(float(transaction[3]), 0)
    for transaction in transactions
)

transaction_count = len(transactions)

unknown_count = sum(
    1
    for transaction in transactions
    if transaction[4] == "Unknown"
)

st.title("Financial overview")

col1, col2, col3 = st.columns(3)

metrics = [
    ("TOTAL SPENT", f"KSh {total_spent:,.2f}"),
    ("TRANSACTIONS", str(transaction_count)),
    ("UNKNOWN MERCHANTS", str(unknown_count)),
]

for column, (label, value) in zip(
    [col1, col2, col3],
    metrics,
):
    with column:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ==================================================
# CSV UPLOAD
# ==================================================

st.divider()
st.header("Import transactions")

st.caption(
    "Upload a CSV containing date, description and amount."
)

sample_csv = (
    "date,description,amount\n"
    "2026-09-20,Uber Kenya,850\n"
    "2026-09-21,Naivas Supermarket,2450\n"
    "2026-09-22,Netflix,1100\n"
)

st.download_button(
    "Download sample CSV",
    data=sample_csv,
    file_name="sample_transactions.csv",
    mime="text/csv",
)

uploaded_file = st.file_uploader(
    "Choose a CSV file",
    type=["csv"],
)

if uploaded_file is not None:

    try:
        df = pd.read_csv(uploaded_file)

        df.columns = (
            df.columns
            .str.strip()
            .str.lower()
        )

        required = {"date", "description", "amount"}
        missing = required - set(df.columns)

        if missing:
            st.error(
                "Missing columns: " + ", ".join(sorted(missing))
            )

        else:
            preview = df[
                ["date", "description", "amount"]
            ].copy()

            preview["amount"] = pd.to_numeric(
                preview["amount"],
                errors="coerce",
            )

            preview["date"] = pd.to_datetime(
                preview["date"],
                errors="coerce",
            )

            preview["description"] = (
                preview["description"]
                .fillna("")
                .astype(str)
                .str.strip()
            )

            valid = (
                preview["date"].notna()
                & preview["amount"].notna()
                & preview["amount"].ge(0)
                & preview["description"].ne("")
            )

            clean_df = preview.loc[valid].copy()

            clean_df["date"] = (
                clean_df["date"]
                .dt.strftime("%Y-%m-%d")
            )

            clean_df["category"] = (
                clean_df["description"]
                .apply(categorize_transaction)
            )

            st.write(
                f"**{len(clean_df)} valid transactions found.**"
            )

            skipped = len(df) - len(clean_df)

            if skipped:
                st.warning(
                    f"{skipped} invalid rows will be skipped."
                )

            st.dataframe(
                clean_df,
                use_container_width=True,
                hide_index=True,
            )

            if st.button(
                "Import transactions",
                type="primary",
                disabled=clean_df.empty,
            ):
                for row in clean_df.itertuples(
                    index=False
                ):
                    add_transaction(
                        row.date,
                        row.description,
                        float(row.amount),
                        row.category,
                    )

                st.session_state["import_message"] = (
                    f"Imported {len(clean_df)} transactions."
                )

                st.rerun()

    except Exception as error:
        st.error(f"CSV error: {error}")

if "import_message" in st.session_state:
    st.success(
        st.session_state.pop("import_message")
    )


# ==================================================
# SPENDING BY CATEGORY
# ==================================================

transactions = get_transactions()

if transactions:
    st.divider()
    st.header("Spending by category")

    chart_df = pd.DataFrame(
        transactions,
        columns=[
            "id",
            "date",
            "description",
            "amount",
            "category",
        ],
    )

    category_totals = (
        chart_df
        .assign(
            amount=chart_df["amount"].clip(lower=0)
        )
        .groupby("category")["amount"]
        .sum()
        .sort_values(ascending=False)
    )

    st.bar_chart(category_totals)


# ==================================================
# TRANSACTION MANAGEMENT
# ==================================================

st.divider()
st.header("Manage transactions")

transactions = get_transactions()

if not transactions:
    st.info(
        "No transactions yet. Upload a CSV to get started."
    )

else:
    st.caption(
        f"{len(transactions)} saved transactions"
    )

    for transaction in transactions:
        transaction_id = transaction[0]
        date = transaction[1]
        description = transaction[2]
        amount = transaction[3]
        category = transaction[4]

        col1, col2, col3 = st.columns(
            [4, 2, 1],
            vertical_alignment="center",
        )

        with col1:
            st.markdown(
                f"**{escape(str(description))}**"
            )
            st.caption(str(date))

        with col2:
            st.write(f"**KSh {amount:,.2f}**")
            st.caption(str(category))

        with col3:
            if st.button(
                "Delete",
                key=f"delete_{transaction_id}",
            ):
                delete_transaction(transaction_id)
                st.rerun()

        st.divider()


# ==================================================
# CLEAR OLD TEST DATA
# ==================================================

with st.expander("Clear all transactions"):

    st.warning(
        "This permanently deletes all saved transactions."
    )

    confirm = st.checkbox(
        "I understand that this cannot be undone."
    )

    if st.button(
        "Delete all transactions",
        disabled=not confirm,
    ):
        deleted = clear_transactions()

        st.session_state["delete_message"] = (
            f"Deleted {deleted} transactions."
        )

        st.rerun()

if "delete_message" in st.session_state:
    st.success(
        st.session_state.pop("delete_message")
    )