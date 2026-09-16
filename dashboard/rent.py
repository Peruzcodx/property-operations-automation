
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
    create_rent,
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

    # =====================================================
    # LOAD RENT, UNIT AND TENANT DATA
    # =====================================================

    rent_records = get_rent()
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
    # FIND TENANTS WITHOUT RENT RECORDS
    # =====================================================

    rent_tenant_ids = {
        record["tenant_id"]
        for record in rent_records
    }

    tenants_without_rent = [
        tenant
        for tenant in tenants
        if tenant["id"] not in rent_tenant_ids
    ]

    # =====================================================
    # TENANTS WITHOUT RENT RECORDS
    # =====================================================

    if tenants_without_rent:

        st.subheader("Tenants Without Rent Records")

        st.caption(
            "These tenants do not currently have a rent record."
        )

        for tenant in tenants_without_rent:

            unit_name = unit_map.get(
                tenant["unit_id"],
                f"Unit {tenant['unit_id']}",
            )

            with st.container(border=True):

                col1, col2, col3 = st.columns(
                    [3, 2, 1]
                )

                with col1:

                    st.markdown(
                        f"**{tenant['name']}**"
                    )

                    st.caption(
                        f"Tenant ID: {tenant['id']}"
                    )

                with col2:

                    st.write(
                        f"Unit: {unit_name}"
                    )

                    st.write(
                        f"Email: {tenant['email']}"
                    )

                with col3:

                    if st.button(
                        "＋ Add Record",
                        key=f"add_rent_{tenant['id']}",
                        type="primary",
                        width="stretch",
                    ):
                        st.session_state[
                            "add_rent_for_tenant"
                        ] = tenant["id"]

                        st.rerun()

    # =====================================================
    # ADD RENT RECORD
    # =====================================================

    add_rent_tenant_id = st.session_state.get(
        "add_rent_for_tenant"
    )

    if add_rent_tenant_id is not None:

        selected_tenant = next(
            (
                tenant
                for tenant in tenants
                if tenant["id"] == add_rent_tenant_id
            ),
            None,
        )

        if selected_tenant:

            selected_unit = next(
                (
                    unit
                    for unit in units
                    if unit["id"]
                    == selected_tenant["unit_id"]
                ),
                None,
            )

            st.divider()

            st.subheader("Add Rent Record")

            st.write(
                f"Tenant: **{selected_tenant['name']}**"
            )

            st.write(
                f"Unit: **{selected_unit['unit_name']}**"
                if selected_unit
                else (
                    f"Unit ID: "
                    f"{selected_tenant['unit_id']}"
                )
            )

            with st.form(
                f"add_rent_form_{selected_tenant['id']}"
            ):

                rent_amount = st.number_input(
                    "Rent Amount",
                    min_value=0.0,
                    step=1000.0,
                )

                due_date = st.date_input(
                    "Due Date"
                )

                amount_paid = st.number_input(
                    "Amount Paid",
                    min_value=0.0,
                    value=0.0,
                    step=1000.0,
                )

                payment_date = st.date_input(
                    "Payment Date",
                    value=None,
                )

                notes = st.text_area(
                    "Notes",
                    placeholder="Optional",
                )

                col1, col2 = st.columns(2)

                with col1:

                    submitted = (
                        st.form_submit_button(
                            "Create Rent Record",
                            type="primary",
                            width="stretch",
                        )
                    )

                with col2:

                    cancelled = (
                        st.form_submit_button(
                            "Cancel",
                            width="stretch",
                        )
                    )

            if cancelled:

                st.session_state.pop(
                    "add_rent_for_tenant",
                    None,
                )

                st.rerun()

            if submitted:

                if rent_amount <= 0:

                    st.error(
                        "Rent amount must be greater than zero."
                    )

                else:

                    try:

                        created = create_rent(
                            unit_id=selected_tenant[
                                "unit_id"
                            ],
                            tenant_id=selected_tenant[
                                "id"
                            ],
                            rent_amount=Decimal(
                                str(rent_amount)
                            ),
                            due_date=due_date.isoformat(),
                            amount_paid=Decimal(
                                str(amount_paid)
                            ),
                            payment_date=(
                                payment_date.isoformat()
                                if payment_date
                                else None
                            ),
                            notes=(
                                notes.strip()
                                if notes.strip()
                                else None
                            ),
                        )

                        st.session_state.pop(
                            "add_rent_for_tenant",
                            None,
                        )

                        st.success(
                            f"Rent record #{created['id']} "
                            "was created successfully."
                        )

                        st.rerun()

                    except Exception as error:

                        st.error(
                            f"Could not create rent record: "
                            f"{error}"
                        )

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

            outstanding = (
                rent_amount - amount_paid
            )

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

        export_df = pd.DataFrame(
            export_rows
        )

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

        if rent_records:

            st.info(
                "No rent records match this filter."
            )

        else:

            st.info(
                "No rent records found."
            )

        return

    for record in filtered_records:

        payment_status = record[
            "payment_status"
        ]

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

        outstanding = (
            rent_amount - amount_paid
        )

        unit_name = unit_map.get(
            record["unit_id"],
            f"Unit {record['unit_id']}",
        )

        tenant_name = tenant_map.get(
            record["tenant_id"],
            f"Tenant {record['tenant_id']}",
        )

        with st.container(border=True):

            top_left, top_right = st.columns(
                [3, 1]
            )

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
                    f"Due: "
                    f"{format_date(record['due_date'])}"
                )

            # =================================================
            # AMOUNTS
            # =================================================

            amount_col1, amount_col2, amount_col3 = (
                st.columns(3)
            )

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

                    submitted = (
                        st.form_submit_button(
                            "Update Payment",
                            type="primary",
                        )
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
