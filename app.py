import streamlit as st
import pandas as pd

from database import create_database, save_review, get_audit_logs

# Initialize the database
create_database()

# Page configuration
st.set_page_config(
    page_title="Fund Reconciliation System",
    page_icon="🏦",
    layout="wide"
)

# Load financial records
bank_df = pd.read_csv("bank_statement.csv")
ledger_df = pd.read_csv("fund_ledger.csv")

# Match transactions
matched = bank_df.merge(
    ledger_df,
    on=["date", "description", "amount", "type"],
    how="inner"
)

# Compare transactions
comparison = bank_df.merge(
    ledger_df,
    on=["date", "description", "type"],
    how="outer",
    suffixes=("_bank", "_ledger"),
    indicator=True
)

# Find discrepancies
amount_mismatch = comparison[
    (comparison["_merge"] == "both") &
    (comparison["amount_bank"] != comparison["amount_ledger"])
]

missing_ledger = comparison[
    comparison["_merge"] == "left_only"
]

missing_bank = comparison[
    comparison["_merge"] == "right_only"
]

total_discrepancies = (
    len(amount_mismatch) +
    len(missing_ledger) +
    len(missing_bank)
)

# Initialize review log
if "audit_log" not in st.session_state:
    st.session_state.audit_log = []

# Dashboard heading
st.title("🏦 Fund Ledger & Reconciliation System")

if total_discrepancies == 0:
    st.success("All transactions are reconciled successfully!")
else:
    st.warning(
        f"Attention required: {total_discrepancies} discrepancies "
        "need financial review."
    )

st.write(
    "A financial reconciliation tool that compares bank statements "
    "with internal fund ledger records."
)

st.divider()

# Financial summary
st.subheader("Financial Reconciliation Summary")

# Financial totals
bank_total = bank_df["amount"].sum()
ledger_total = ledger_df["amount"].sum()

financial_difference = bank_total - ledger_total

st.subheader("Financial Position")

col1, col2, col3 = st.columns(3)

col1.metric("Bank Total", f"₹{bank_total:,.2f}")
col2.metric("Ledger Total", f"₹{ledger_total:,.2f}")
col3.metric(
    "Financial Difference",
    f"₹{financial_difference:,.2f}"
)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Bank Transactions", len(bank_df))
col2.metric("Ledger Transactions", len(ledger_df))
col3.metric("Matched Transactions", len(matched))
col4.metric("Total Discrepancies", total_discrepancies)

st.divider()

# Matched transactions
st.subheader("🔎 Filter Reconciliation Results")

filter_option = st.selectbox(
    "Select transaction category",
    [
        "All Transactions",
        "Matched Transactions",
        "Amount Mismatches",
        "Missing from Fund Ledger",
        "Missing from Bank Statement"
    ]
)

if filter_option == "All Transactions":
    st.subheader("All Matched Transactions")
    st.dataframe(matched, use_container_width=True)

elif filter_option == "Matched Transactions":
    st.subheader("Matched Transactions")
    st.dataframe(matched, use_container_width=True)

elif filter_option == "Amount Mismatches":
    st.subheader("Amount Mismatches")
    st.dataframe(
        amount_mismatch[
            ["description", "amount_bank", "amount_ledger"]
        ],
        use_container_width=True
    )

elif filter_option == "Missing from Fund Ledger":
    st.subheader("Missing from Fund Ledger")
    st.dataframe(
        missing_ledger[["description", "amount_bank"]],
        use_container_width=True
    )

elif filter_option == "Missing from Bank Statement":
    st.subheader("Missing from Bank Statement")
    st.dataframe(
        missing_bank[["description", "amount_ledger"]],
        use_container_width=True
    )

# Amount mismatches
st.subheader("⚠️ Amount Mismatches")

st.dataframe(
    amount_mismatch[
        ["description", "amount_bank", "amount_ledger"]
    ],
    use_container_width=True
)

# Missing from ledger
st.subheader("❌ Missing from Fund Ledger")

st.dataframe(
    missing_ledger[
        ["description", "amount_bank"]
    ],
    use_container_width=True
)

# Missing from bank
st.subheader("❌ Missing from Bank Statement")

st.dataframe(
    missing_bank[
        ["description", "amount_ledger"]
    ],
    use_container_width=True
)

st.divider()

st.subheader("📊 Reconciliation Overview")

chart_data = pd.DataFrame({
    "Status": ["Matched", "Discrepancies"],
    "Transactions": [
        len(matched),
        total_discrepancies
    ]
})

st.bar_chart(
    chart_data,
    x="Status",
    y="Transactions",
    color="Status"
)

# Download Reconciliation Report

st.divider()

st.subheader("📥 Download Reconciliation Report")

report = comparison.copy()

csv_report = report.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Full Reconciliation Report",
    data=csv_report,
    file_name="fund_reconciliation_report.csv",
    mime="text/csv"
)

# Transaction Review Section

st.divider()

st.subheader("📝 Transaction Review")

with st.form("review_form"):

    transaction_name = st.text_input(
        "Transaction Description",
        placeholder="Example: Legal Fees"
    )

    review_action = st.selectbox(
        "Review Status",
        [
            "Under Investigation",
            "Verified",
            "Correction Required"
        ]
    )

    reviewer_note = st.text_area(
        "Review Notes",
        placeholder="Enter your investigation findings..."
    )

    submitted = st.form_submit_button("Save Review")

    if submitted:
        if transaction_name.strip():

            save_review(
                transaction_name,
                review_action,
                reviewer_note
            )

            st.success("Review saved permanently!")

        else:
            st.error("Please enter a transaction description.")

# Display permanent audit log

st.subheader("📋 Permanent Audit Log")

audit_df = get_audit_logs()

if not audit_df.empty:
    st.dataframe(audit_df, use_container_width=True)
else:
    st.info("No transaction reviews recorded yet.")

# Display audit log

st.subheader("📋 Audit Log")

if st.session_state.audit_log:
    audit_df = pd.DataFrame(st.session_state.audit_log)
    st.dataframe(audit_df, use_container_width=True)
else:
    st.info("No transaction reviews recorded yet.")