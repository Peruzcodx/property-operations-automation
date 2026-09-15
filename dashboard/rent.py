from datetime import datetime
from decimal import Decimal
import io

import pandas as pd
import streamlit as st

from api import (
    get_rent,
    get_units,
    get_tenants,
    update_rent,
)


# =========================================================
# DATE FORMATTING
# =========================================================

def format_date(value):
    if not value:
        return "Not recorded"

    try:
        return datetime.fromisoformat(
            str(value)
        ).strftime("%b %d, %Y")
    except ValueError:
        return str(value)


# =========================================================
# RENT PAGE
# =========================================================

def show_rent_page():
    st.title("Rent")
    st.caption("Rent and payment management")

    rent_records = get_rent()

    if not rent_records:
        st.info("No rent records found.")
        return

    # =====================================================
    # LOAD UNIT AND TENANT NAMES
    # =====================================================

    units = get_units()
    tenants = get_tenants()

    unit_map = {
        unit["id"]: unit["unit_name"]
        for unit in units
    }

    tenant_map = {
        tenant["id"]: tenant["name"]
        for tenant in tenants
    }

    # =====================================================
    # SUMMARY
    # =====================================================

    paid_records = [
        record
        for record in rent_records
        if record["payment_status"] == "Paid"
    ]

    partial_records = [
        record
        for record in rent_records
        if record["payment_status"] == "Partial"
    ]

    pending_records = [
        record
        for record in rent_records
        if record["payment_status"] == "Pending"
    ]

    outstanding_total = sum(
        (
            Decimal(str(record["rent_amount"]))
            - Decimal(str(record["amount_paid"]))
        )
        for record in rent_records
    )

    # =====================================================
    # KPI CARDS
    # =====================================================

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric(
        "Total Records",
        len(rent_records),
    )

    col2.metric(
        "Paid",
        len(paid_records),
    )

    col3.metric(
        "Partial",
        len(partial_records),
    )

    col4.metric(
        "Pending",
        len(pending_records),
    )

    col5.metric(
        "Outstanding",
        f"₦{outstanding_total:,.2f}",
    )

    st.divider()

    # =====================================================
    # FILTER
    # =====================================================

    left, right = st.columns([3, 1])

    with left:
        status_filter = st.selectbox(
            "Filter by payment status",
            [
                "All",
                "Paid",
                "Partial",
                "Pending",
            ],
        )

    filtered_records = rent_records

    if status_filter != "All":
        filtered_records = [
            record
            for record in rent_records
            if record["payment_status"] == status_filter
        ]

    # =====================================================
    # CSV EXPORT
    # =====================================================

    with right:

        export_rows = []

        for record in filtered_records:

            rent_amount = Decimal(
                str(record["rent_amount"])
            )

            amount_paid = Decimal(
                str(record["amount_paid"])
            )

            outstanding = rent_amount - amount_paid

            export_rows.append(
                {
                    "Rent ID": record["id"],
                    "Unit": unit_map.get(
                        record["unit_id"],
                        f"Unit {record['unit_id']}",
                    ),
                    "Tenant": tenant_map.get(
                        record["tenant_id"],
                        f"Tenant {record['tenant_id']}",
                    ),
                    "Rent Amount": float(rent_amount),
                    "Due Date": format_date(
                        record["due_date"]
                    ),
                    "Amount Paid": float(amount_paid),
                    "Outstanding": float(outstanding),
                    "Payment Date": format_date(
                        record["payment_date"]
                    ),
                    "Payment Status": record[
                        "payment_status"
                    ],
                    "Notes": record["notes"] or "",
                }
            )

        export_df = pd.DataFrame(export_rows)

        csv_buffer = io.StringIO()

        export_df.to_csv(
            csv_buffer,
            index=False,
        )

        st.download_button(
            label="Download CSV",
            data=csv_buffer.getvalue(),
            file_name="rent_records.csv",
            mime="text/csv",
            width="stretch",
        )

    # =====================================================
    # RENT RECORDS
    # =====================================================

    st.subheader("Rent Records")

    if not filtered_records:
        st.info("No rent records match this filter.")
        return

    for record in filtered_records:

        payment_status = record["payment_status"]

        if payment_status == "Paid":
            status_label = "🟢 Paid"
        elif payment_status == "Partial":
            status_label = "🟡 Partial"
        else:
            status_label = "🔴 Pending"

        rent_amount = Decimal(
            str(record["rent_amount"])
        )

        amount_paid = Decimal(
            str(record["amount_paid"])
        )

        outstanding = rent_amount - amount_paid

        unit_name = unit_map.get(
            record["unit_id"],
            f"Unit {record['unit_id']}",
        )

        tenant_name = tenant_map.get(
            record["tenant_id"],
            f"Tenant {record['tenant_id']}",
        )

        with st.container(border=True):

            top_left, top_right = st.columns([3, 1])

            with top_left:

                st.markdown(
                    f"### Rent Record #{record['id']}"
                )

                st.write(
                    f"Unit: {unit_name}"
                )

                st.write(
                    f"Tenant: {tenant_name}"
                )

            with top_right:

                st.markdown(
                    f"**{status_label}**"
                )

                st.write(
                    f"Due: {format_date(record['due_date'])}"
                )

            # =================================================
            # AMOUNTS
            # =================================================

            amount_col1, amount_col2, amount_col3 = st.columns(3)

            with amount_col1:
                st.write(
                    f"Rent: ₦{rent_amount:,.2f}"
                )

            with amount_col2:
                st.write(
                    f"Paid: ₦{amount_paid:,.2f}"
                )

            with amount_col3:
                st.write(
                    f"Outstanding: ₦{outstanding:,.2f}"
                )

            # =================================================
            # PAYMENT INFORMATION
            # =================================================

            st.write(
                "Payment date: "
                f"{format_date(record['payment_date'])}"
            )

            if record["notes"]:
                st.write(
                    f"Notes: {record['notes']}"
                )

            # =================================================
            # UPDATE PAYMENT
            # =================================================

            with st.expander("Update Payment"):

                with st.form(
                    key=f"rent_form_{record['id']}"
                ):

                    new_amount_paid = st.number_input(
                        "Amount paid",
                        min_value=0.0,
                        value=float(amount_paid),
                        step=1000.0,
                    )

                    new_payment_date = st.date_input(
                        "Payment date",
                        value=(
                            record["payment_date"]
                            if record["payment_date"]
                            else None
                        ),
                    )

                    new_notes = st.text_area(
                        "Notes",
                        value=record["notes"] or "",
                    )

                    submitted = st.form_submit_button(
                        "Update Payment",
                        type="primary",
                    )

                    if submitted:

                        try:
                            update_rent(
                                rent_id=record["id"],
                                amount_paid=Decimal(
                                    str(new_amount_paid)
                                ),
                                payment_date=(
                                    str(new_payment_date)
                                    if new_payment_date
                                    else None
                                ),
                                notes=(
                                    new_notes
                                    if new_notes.strip()
                                    else None
                                ),
                            )

                            st.success(
                                "Payment updated successfully."
                            )

                            st.rerun()

                        except Exception as error:
                            st.error(
                                f"Update failed: {error}"
                            )