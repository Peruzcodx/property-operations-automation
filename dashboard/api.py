

import os

)
API_BASE_URL = "http://127.0.0.1:8000"


# =========================================================
# READ OPERATIONS
# =========================================================

@st.cache_data(ttl=30)
def get_properties():
    response = requests.get(
        f"{API_BASE_URL}/properties/",
        timeout=10,
    )
    response.raise_for_status()

    data = response.json()

    return data["properties"]


@st.cache_data(ttl=30)
def get_property(property_id: int):
    response = requests.get(
        f"{API_BASE_URL}/properties/{property_id}",
        timeout=10,
    )
    response.raise_for_status()

    return response.json()


@st.cache_data(ttl=30)
def get_units():
    response = requests.get(
        f"{API_BASE_URL}/units/",
        timeout=10,
    )
    response.raise_for_status()

    return response.json()


@st.cache_data(ttl=30)
def get_tenants():
    response = requests.get(
        f"{API_BASE_URL}/tenants/",
        timeout=10,
    )
    response.raise_for_status()

    return response.json()


@st.cache_data(ttl=30)
def get_inspections():
    response = requests.get(
        f"{API_BASE_URL}/inspections/",
        timeout=10,
    )
    response.raise_for_status()

    return response.json()


@st.cache_data(ttl=15)
def get_maintenance():
    response = requests.get(
        f"{API_BASE_URL}/maintenance/",
        timeout=10,
    )
    response.raise_for_status()

    return response.json()


@st.cache_data(ttl=30)
def get_rent():
    response = requests.get(
        f"{API_BASE_URL}/rent/",
        timeout=10,
    )
    response.raise_for_status()

    return response.json()


@st.cache_data(ttl=15)
def get_property_overview(property_id: int):
    response = requests.get(
        f"{API_BASE_URL}/properties/{property_id}/overview",
        timeout=10,
    )
    response.raise_for_status()

    return response.json()


# =========================================================
# PROPERTY-SPECIFIC READ OPERATIONS
#
# These are still available for other dashboard pages.
# The property detail page now uses get_property_overview()
# instead of making multiple API requests.
# =========================================================

def get_units_by_property(property_id: int):
    units = get_units()

    return [
        unit
        for unit in units
        if unit["property_id"] == property_id
    ]


def get_tenants_by_property(property_id: int):
    units = get_units_by_property(property_id)

    unit_ids = {
        unit["id"]
        for unit in units
    }

    tenants = get_tenants()

    return [
        tenant
        for tenant in tenants
        if tenant["unit_id"] in unit_ids
    ]


def get_inspections_by_property(property_id: int):
    units = get_units_by_property(property_id)

    unit_ids = {
        unit["id"]
        for unit in units
    }

    inspections = get_inspections()

    return [
        inspection
        for inspection in inspections
        if inspection["unit_id"] in unit_ids
    ]


def get_maintenance_by_property(property_id: int):
    units = get_units_by_property(property_id)

    unit_ids = {
        unit["id"]
        for unit in units
    }

    maintenance = get_maintenance()

    return [
        request
        for request in maintenance
        if request["unit_id"] in unit_ids
    ]


def get_rent_by_property(property_id: int):
    units = get_units_by_property(property_id)

    unit_ids = {
        unit["id"]
        for unit in units
    }

    rent = get_rent()

    return [
        record
        for record in rent
        if record["unit_id"] in unit_ids
    ]


# =========================================================
# CREATE OPERATIONS
# =========================================================

def create_property(
    property_name: str,
    address: str,
    property_type: str,
):
    response = requests.post(
        f"{API_BASE_URL}/properties/",
        json={
            "property_name": property_name,
            "address": address,
            "property_type": property_type,
        },
        timeout=10,
    )

    response.raise_for_status()

    st.cache_data.clear()

    return response.json()


def create_unit(
    property_id: int,
    unit_name: str,
):
    response = requests.post(
        f"{API_BASE_URL}/units/",
        json={
            "property_id": property_id,
            "unit_name": unit_name,
        },
        timeout=10,
    )

    response.raise_for_status()

    st.cache_data.clear()

    return response.json()


def create_tenant(
    unit_id: int,
    name: str,
    email: str,
    phone: str,
):
    response = requests.post(
        f"{API_BASE_URL}/tenants/",
        json={
            "unit_id": unit_id,
            "name": name,
            "email": email,
            "phone": phone,
        },
        timeout=10,
    )

    response.raise_for_status()

    st.cache_data.clear()

    return response.json()


def create_inspection(
    unit_id: int,
    inspection_type: str,
    inspection_date: str,
    inspector: str,
    condition_notes: str | None = None,
    flagged_issue: str | None = None,
):
    response = requests.post(
        f"{API_BASE_URL}/inspections/",
        json={
            "unit_id": unit_id,
            "inspection_type": inspection_type,
            "inspection_date": inspection_date,
            "inspector": inspector,
            "condition_notes": condition_notes,
            "flagged_issue": flagged_issue,
        },
        timeout=10,
    )

    response.raise_for_status()

    st.cache_data.clear()

    return response.json()


def create_maintenance_request(
    unit_id: int,
    inspection_id: int,
    description: str,
    reported_by: str,
    priority: str,
    assigned_contractor: str | None = None,
):
    response = requests.post(
        f"{API_BASE_URL}/maintenance/",
        json={
            "unit_id": unit_id,
            "inspection_id": inspection_id,
            "description": description,
            "reported_by": reported_by,
            "priority": priority,
            "assigned_contractor": assigned_contractor,
        },
        timeout=10,
    )

    response.raise_for_status()

    st.cache_data.clear()

    return response.json()


def create_rent(
    unit_id: int,
    tenant_id: int,
    rent_amount,
    due_date: str,
    amount_paid=0,
    payment_date: str | None = None,
    notes: str | None = None,
):
    response = requests.post(
        f"{API_BASE_URL}/rent/",
        json={
            "unit_id": unit_id,
            "tenant_id": tenant_id,
            "rent_amount": str(rent_amount),
            "due_date": due_date,
            "amount_paid": str(amount_paid),
            "payment_date": payment_date,
            "notes": notes,
        },
        timeout=10,
    )

    response.raise_for_status()

    st.cache_data.clear()

    return response.json()


# =========================================================
# UPDATE OPERATIONS
# =========================================================

def update_maintenance_request(
    maintenance_id: int,
    priority: str | None = None,
    assigned_contractor: str | None = None,
    status: str | None = None,
    resolution_notes: str | None = None,
):
    response = requests.patch(
        f"{API_BASE_URL}/maintenance/{maintenance_id}",
        json={
            "priority": priority,
            "assigned_contractor": assigned_contractor,
            "status": status,
            "resolution_notes": resolution_notes,
        },
        timeout=10,
    )

    response.raise_for_status()

    st.cache_data.clear()

    return response.json()


def update_rent(
    rent_id: int,
    amount_paid=None,
    payment_date: str | None = None,
    notes: str | None = None,
):
    response = requests.patch(
        f"{API_BASE_URL}/rent/{rent_id}",
        json={
            "amount_paid": (
                str(amount_paid)
                if amount_paid is not None
                else None
            ),
            "payment_date": payment_date,
            "notes": notes,
        },
        timeout=10,
    )

    response.raise_for_status()

    st.cache_data.clear()

    return response.json()

@st.cache_data(ttl=15)
def get_dashboard_summary():
    response = requests.get(
        f"{API_BASE_URL}/properties/dashboard-summary",
        timeout=10,
    )

    response.raise_for_status()

    return response.json()