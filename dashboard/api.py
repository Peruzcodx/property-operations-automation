import os
import requests
import streamlit as st


try:
    API_BASE_URL = st.secrets["API_BASE_URL"]
except (KeyError, st.errors.StreamlitSecretNotFoundError):
    API_BASE_URL = os.getenv(
        "API_BASE_URL",
        "http://127.0.0.1:8000",
    )


API_TIMEOUT = 30


def api_request(
    method: str,
    endpoint: str,
    **kwargs,
):
    try:
        response = requests.request(
            method,
            f"{API_BASE_URL}{endpoint}",
            timeout=API_TIMEOUT,
            **kwargs,
        )

        response.raise_for_status()

        return response

    except requests.exceptions.Timeout:
        st.warning(
            "The backend is taking longer than usual to respond. "
            "Please try again in a moment."
        )
        return None

    except requests.exceptions.ConnectionError:
        st.warning(
            "The backend is currently unavailable. "
            "Please try again in a moment."
        )
        return None

    except requests.exceptions.RequestException as exc:
        st.error(
            f"Unable to complete the request: {exc}"
        )
        return None
# =========================================================
# READ OPERATIONS
# =========================================================
@st.cache_data(ttl=30)
def get_properties():
    response = api_request(
        "GET",
        "/properties/",
    )

    if response is None:
        return []

    data = response.json()

    return data["properties"]
@st.cache_data(ttl=30)
def get_property(property_id: int):

    response = api_request(
        "GET",
        f"/properties/{property_id}",
      
    )

    if response is None:
        return None

    return response.json()


@st.cache_data(ttl=30)
def get_units():

    response = api_request(
        "GET",
        "/units/",
        
    )

    if response is None:
        return []

    return response.json()


@st.cache_data(ttl=30)
def get_tenants():

    response = api_request(
        "GET",
        "/tenants/",
      
    )

    if response is None:
        return []

    return response.json()


@st.cache_data(ttl=30)
def get_inspections():

    response = api_request(
        "GET",
        "/inspections/",
       
    )

    if response is None:
        return []

    return response.json()


@st.cache_data(ttl=15)
def get_maintenance():

    response = api_request(
        "GET",
        "/maintenance/",
     
    )

    if response is None:
        return []

    return response.json()


@st.cache_data(ttl=30)
def get_rent():

    response = api_request(
        "GET",
        "/rent/",
        
    )

    if response is None:
        return []

    return response.json()


@st.cache_data(ttl=15)
def get_property_overview(property_id: int):

    response = api_request(
        "GET",
        f"/properties/{property_id}/overview",
        
    )

    if response is None:
        return None

    return response.json()


# =========================================================
# PROPERTY-SPECIFIC READ OPERATIONS
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

    response = api_request(
        "POST",
        "/properties/",
        json={
            "property_name": property_name,
            "address": address,
            "property_type": property_type,
        },
    )

    if response is None:
        return None

    st.cache_data.clear()

    return response.json()


def create_unit(
    property_id: int,
    unit_name: str,
):

    response = api_request(
        "POST",
        "/units/",
        json={
            "property_id": property_id,
            "unit_name": unit_name,
        },
    )

    if response is None:
        return None

    st.cache_data.clear()

    return response.json()


def create_tenant(
    unit_id: int,
    name: str,
    email: str,
    phone: str,
):

    response = api_request(
        "POST",
        "/tenants/",
        json={
            "unit_id": unit_id,
            "name": name,
            "email": email,
            "phone": phone,
        },
    )

    if response is None:
        return None

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

    response = api_request(
        "POST",
        "/inspections/",
        json={
            "unit_id": unit_id,
            "inspection_type": inspection_type,
            "inspection_date": inspection_date,
            "inspector": inspector,
            "condition_notes": condition_notes,
            "flagged_issue": flagged_issue,
        },
    )

    if response is None:
        return None

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

    response = api_request(
        "POST",
        "/maintenance/",
        json={
            "unit_id": unit_id,
            "inspection_id": inspection_id,
            "description": description,
            "reported_by": reported_by,
            "priority": priority,
            "assigned_contractor": assigned_contractor,
        },
    )

    if response is None:
        return None

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

    response = api_request(
        "POST",
        "/rent/",
        json={
            "unit_id": unit_id,
            "tenant_id": tenant_id,
            "rent_amount": str(rent_amount),
            "due_date": due_date,
            "amount_paid": str(amount_paid),
            "payment_date": payment_date,
            "notes": notes,
        },
    )

    if response is None:
        return None

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

    response = api_request(
        "PATCH",
        f"/maintenance/{maintenance_id}",
        json={
            "priority": priority,
            "assigned_contractor": assigned_contractor,
            "status": status,
            "resolution_notes": resolution_notes,
        },
    )

    if response is None:
        return None

    st.cache_data.clear()

    return response.json()


def update_rent(
    rent_id: int,
    amount_paid=None,
    payment_date: str | None = None,
    notes: str | None = None,
):

    response = api_request(
        "PATCH",
        f"/rent/{rent_id}",
        json={
            "amount_paid": (
                str(amount_paid)
                if amount_paid is not None
                else None
            ),
            "payment_date": payment_date,
            "notes": notes,
        },
    )

    if response is None:
        return None

    st.cache_data.clear()

    return response.json()


# =========================================================
# DASHBOARD SUMMARY
# =========================================================

@st.cache_data(ttl=15)
def get_dashboard_summary():

    response = api_request(
        "GET",
        "/properties/dashboard-summary",
    )

    if response is None:
        return {
            "properties_count": 0,
            "units_count": 0,
            "tenants_count": 0,
            "maintenance": {
                "open": 0,
                "in_progress": 0,
                "resolved": 0,
            },
            "rent": {
                "paid": 0,
                "partial": 0,
                "pending": 0,
                "outstanding": 0,
            },
        }

    return response.json()