from typing import List
from datetime import datetime

from fastapi import (
    APIRouter,
    HTTPException,
)

from database import (
    get_connection,
    release_connection,
)

from schemas.maintenance import (
    MaintenanceCreate,
    MaintenanceUpdate,
    MaintenanceResponse,
)


router = APIRouter(
    prefix="/maintenance",
    tags=["Maintenance"],
)


# =========================================================
# GET ALL MAINTENANCE REQUESTS
# =========================================================

@router.get(
    "/",
    response_model=List[MaintenanceResponse],
)
def get_maintenance_requests():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    unit_id,
                    inspection_id,
                    description,
                    reported_by,
                    priority,
                    assigned_contractor,
                    status,
                    created_at,
                    resolved_at,
                    resolution_notes
                FROM maintenance_requests
                ORDER BY created_at DESC, id DESC;
                """
            )

            rows = cursor.fetchall()

            return [
                {
                    "id": row[0],
                    "unit_id": row[1],
                    "inspection_id": row[2],
                    "description": row[3],
                    "reported_by": row[4],
                    "priority": row[5],
                    "assigned_contractor": row[6],
                    "status": row[7],
                    "created_at": row[8],
                    "resolved_at": row[9],
                    "resolution_notes": row[10],
                }
                for row in rows
            ]

    finally:
        release_connection(connection)


# =========================================================
# CREATE MAINTENANCE REQUEST
# =========================================================

@router.post(
    "/",
    response_model=MaintenanceResponse,
    status_code=201,
)
def create_maintenance_request(
    maintenance_data: MaintenanceCreate,
):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO maintenance_requests (
                    unit_id,
                    inspection_id,
                    description,
                    reported_by,
                    priority,
                    assigned_contractor
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING
                    id,
                    unit_id,
                    inspection_id,
                    description,
                    reported_by,
                    priority,
                    assigned_contractor,
                    status,
                    created_at,
                    resolved_at,
                    resolution_notes;
                """,
                (
                    maintenance_data.unit_id,
                    maintenance_data.inspection_id,
                    maintenance_data.description,
                    maintenance_data.reported_by,
                    maintenance_data.priority,
                    maintenance_data.assigned_contractor,
                ),
            )

            row = cursor.fetchone()

            connection.commit()

            return {
                "id": row[0],
                "unit_id": row[1],
                "inspection_id": row[2],
                "description": row[3],
                "reported_by": row[4],
                "priority": row[5],
                "assigned_contractor": row[6],
                "status": row[7],
                "created_at": row[8],
                "resolved_at": row[9],
                "resolution_notes": row[10],
            }

    except Exception:
        connection.rollback()
        raise

    finally:
        release_connection(connection)


# =========================================================
# UPDATE MAINTENANCE REQUEST
# =========================================================

@router.patch(
    "/{maintenance_id}",
    response_model=MaintenanceResponse,
)
def update_maintenance_request(
    maintenance_id: int,
    maintenance_data: MaintenanceUpdate,
):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE maintenance_requests
                SET
                    priority = COALESCE(
                        CAST(%s AS VARCHAR(20)),
                        priority
                    ),
                    assigned_contractor = COALESCE(
                        CAST(%s AS VARCHAR(150)),
                        assigned_contractor
                    ),
                    status = COALESCE(
                        CAST(%s AS VARCHAR(20)),
                        status
                    ),
                    resolution_notes = COALESCE(
                        CAST(%s AS TEXT),
                        resolution_notes
                    ),
                    resolved_at = CASE
                        WHEN CAST(%s AS VARCHAR(20)) = 'Resolved'
                            THEN COALESCE(
                                resolved_at,
                                NOW()
                            )
                        ELSE resolved_at
                    END
                WHERE id = %s
                RETURNING
                    id,
                    unit_id,
                    inspection_id,
                    description,
                    reported_by,
                    priority,
                    assigned_contractor,
                    status,
                    created_at,
                    resolved_at,
                    resolution_notes;
                """,
                (
                    maintenance_data.priority,
                    maintenance_data.assigned_contractor,
                    maintenance_data.status,
                    maintenance_data.resolution_notes,
                    maintenance_data.status,
                    maintenance_id,
                ),
            )

            row = cursor.fetchone()

            if row is None:
                raise HTTPException(
                    status_code=404,
                    detail="Maintenance request not found",
                )

            connection.commit()

            return {
                "id": row[0],
                "unit_id": row[1],
                "inspection_id": row[2],
                "description": row[3],
                "reported_by": row[4],
                "priority": row[5],
                "assigned_contractor": row[6],
                "status": row[7],
                "created_at": row[8],
                "resolved_at": row[9],
                "resolution_notes": row[10],
            }

    except Exception:
        connection.rollback()
        raise

    finally:
        release_connection(connection)