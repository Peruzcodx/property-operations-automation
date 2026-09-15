from decimal import Decimal
import csv
import io

import streamlit as st

from api import (
    get_dashboard_summary,
    get_properties,
    get_maintenance,
    get_rent,
)


# =========================================================
# REPORTS PAGE
# =========================================================

def show_reports_page():
    st.title("Reports")
    st.caption("Property operations reporting and data export")

    # =====================================================
    # LOAD DATA
    # =====================================================

    summary = get_dashboard_summary()
    properties = get_properties()
    maintenance = get_maintenance()
    rent = get_rent()

    # =====================================================
    # PORTFOLIO SUMMARY
    # =====================================================

    st.subheader("Portfolio Summary")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Properties",
        summary["properties_count"],
    )

    col2.metric(
        "Units",
        summary["units_count"],
    )

    col3.metric(
        "Tenants",
        summary["tenants_count"],
    )

    col4.metric(
        "Outstanding Rent",
        f"₦{summary['rent']['outstanding']:,.2f}",
    )

    st.divider()

    # =====================================================
    # RENT SUMMARY
    # =====================================================

    st.subheader("Rent Summary")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Paid",
        summary["rent"]["paid"],
    )

    col2.metric(
        "Partial",
        summary["rent"]["partial"],
    )

    col3.metric(
        "Pending",
        summary["rent"]["pending"],
    )

    col4.metric(
        "Outstanding",
        f"₦{summary['rent']['outstanding']:,.2f}",
    )

    st.divider()

    # =====================================================
    # MAINTENANCE SUMMARY
    # =====================================================

    st.subheader("Maintenance Summary")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Open",
        summary["maintenance"]["open"],
    )

    col2.metric(
        "In Progress",
        summary["maintenance"]["in_progress"],
    )

    col3.metric(
        "Resolved",
        summary["maintenance"]["resolved"],
    )

    st.divider()

    # =====================================================
    # OUTSTANDING RENT
    # =====================================================

    st.subheader("Outstanding Rent")

    outstanding_rows = []

    for record in rent:

        rent_amount = Decimal(
            str(record["rent_amount"])
        )

        amount_paid = Decimal(
            str(record["amount_paid"])
        )

        outstanding = rent_amount - amount_paid

        if outstanding > 0:

            outstanding_rows.append(
                {
                    "Rent ID": record["id"],
                    "Unit ID": record["unit_id"],
                    "Tenant ID": record["tenant_id"],
                    "Rent Amount": (
                        f"₦{rent_amount:,.2f}"
                    ),
                    "Amount Paid": (
                        f"₦{amount_paid:,.2f}"
                    ),
                    "Outstanding": (
                        f"₦{outstanding:,.2f}"
                    ),
                    "Due Date": str(
                        record["due_date"]
                    ),
                    "Status": record[
                        "payment_status"
                    ],
                }
            )

    if outstanding_rows:

        st.dataframe(
            outstanding_rows,
            width="stretch",
            hide_index=True,
        )

    else:

        st.success(
            "No outstanding rent."
        )

    st.divider()

    # =====================================================
    # ACTIVE MAINTENANCE
    # =====================================================

    st.subheader("Active Maintenance")

    active_requests = [
        request
        for request in maintenance
        if request["status"] != "Resolved"
    ]

    if active_requests:

        maintenance_rows = []

        for request in active_requests:

            maintenance_rows.append(
                {
                    "Request ID": request["id"],
                    "Unit ID": request["unit_id"],
                    "Description": request[
                        "description"
                    ],
                    "Priority": request[
                        "priority"
                    ],
                    "Contractor": (
                        request[
                            "assigned_contractor"
                        ]
                        or "Not assigned"
                    ),
                    "Status": request[
                        "status"
                    ],
                    "Reported By": request[
                        "reported_by"
                    ],
                }
            )

        st.dataframe(
            maintenance_rows,
            width="stretch",
            hide_index=True,
        )

    else:

        st.success(
            "No active maintenance requests."
        )

    st.divider()

    # =====================================================
    # PROPERTY PORTFOLIO
    # =====================================================

    st.subheader("Property Portfolio")

    property_rows = []

    for property_item in properties:

        property_rows.append(
            {
                "Property": property_item[
                    "property_name"
                ],
                "Address": property_item[
                    "address"
                ],
                "Property Type": property_item[
                    "property_type"
                ],
            }
        )

    st.dataframe(
        property_rows,
        width="stretch",
        hide_index=True,
    )

    st.divider()

    # =====================================================
    # CONSOLIDATED CSV EXPORT
    # =====================================================

    st.subheader("Export Report")

    export_rows = []

    # -----------------------------------------------------
    # RENT RECORDS
    # -----------------------------------------------------

    for record in rent:

        rent_amount = Decimal(
            str(record["rent_amount"])
        )

        amount_paid = Decimal(
            str(record["amount_paid"])
        )

        outstanding = rent_amount - amount_paid

        export_rows.append(
            {
                "Report Type": "Rent",
                "Record ID": record["id"],
                "Unit ID": record["unit_id"],
                "Tenant ID": record["tenant_id"],
                "Description": "",
                "Amount": float(rent_amount),
                "Amount Paid": float(amount_paid),
                "Outstanding": float(outstanding),
                "Status": record[
                    "payment_status"
                ],
                "Priority": "",
                "Date": str(
                    record["due_date"]
                ),
                "Notes": record["notes"] or "",
            }
        )

    # -----------------------------------------------------
    # MAINTENANCE RECORDS
    # -----------------------------------------------------

    for request in maintenance:

        export_rows.append(
            {
                "Report Type": "Maintenance",
                "Record ID": request["id"],
                "Unit ID": request["unit_id"],
                "Tenant ID": "",
                "Description": request[
                    "description"
                ],
                "Amount": "",
                "Amount Paid": "",
                "Outstanding": "",
                "Status": request[
                    "status"
                ],
                "Priority": request[
                    "priority"
                ],
                "Date": str(
                    request["created_at"]
                ),
                "Notes": (
                    request[
                        "resolution_notes"
                    ]
                    or ""
                ),
            }
        )

    # =====================================================
    # CREATE CSV
    # =====================================================

    csv_buffer = io.StringIO()

    fieldnames = [
        "Report Type",
        "Record ID",
        "Unit ID",
        "Tenant ID",
        "Description",
        "Amount",
        "Amount Paid",
        "Outstanding",
        "Status",
        "Priority",
        "Date",
        "Notes",
    ]

    writer = csv.DictWriter(
        csv_buffer,
        fieldnames=fieldnames,
    )

    writer.writeheader()
    writer.writerows(export_rows)

    st.download_button(
        label="Download Consolidated Report",
        data=csv_buffer.getvalue(),
        file_name="property_operations_report.csv",
        mime="text/csv",
        width="stretch",
    )