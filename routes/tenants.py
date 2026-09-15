from typing import List

from fastapi import APIRouter

from database import (
    get_connection,
    release_connection,
)

from schemas.tenant import (
    TenantCreate,
    TenantResponse,
)


router = APIRouter(
    prefix="/tenants",
    tags=["Tenants"],
)


# =========================================================
# GET ALL TENANTS
# =========================================================

@router.get(
    "/",
    response_model=List[TenantResponse],
)
def get_tenants():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    unit_id,
                    name,
                    email,
                    phone,
                    created_at
                FROM tenants
                ORDER BY id;
                """
            )

            rows = cursor.fetchall()

            return [
                {
                    "id": row[0],
                    "unit_id": row[1],
                    "name": row[2],
                    "email": row[3],
                    "phone": row[4],
                    "created_at": row[5],
                }
                for row in rows
            ]

    finally:
        release_connection(connection)


# =========================================================
# CREATE TENANT
# =========================================================

@router.post(
    "/",
    response_model=TenantResponse,
    status_code=201,
)
def create_tenant(
    tenant_data: TenantCreate,
):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO tenants (
                    unit_id,
                    name,
                    email,
                    phone
                )
                VALUES (%s, %s, %s, %s)
                RETURNING
                    id,
                    unit_id,
                    name,
                    email,
                    phone,
                    created_at;
                """,
                (
                    tenant_data.unit_id,
                    tenant_data.name,
                    tenant_data.email,
                    tenant_data.phone,
                ),
            )

            row = cursor.fetchone()

            connection.commit()

            return {
                "id": row[0],
                "unit_id": row[1],
                "name": row[2],
                "email": row[3],
                "phone": row[4],
                "created_at": row[5],
            }

    except Exception:
        connection.rollback()
        raise

    finally:
        release_connection(connection)