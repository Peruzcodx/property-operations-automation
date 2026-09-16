from fastapi import FastAPI

from routes.properties import router as properties_router
from routes.units import router as units_router
from routes.tenants import router as tenants_router
from routes.inspections import router as inspections_router
from routes.maintenance import router as maintenance_router
from routes.rent import router as rent_router


app = FastAPI(
    title="Property Operations Automation",
    description="Sample property management operations API",
    version="1.0.0",
)


@app.get("/")
def root():
    return {
        "message": "Property Operations Automation API is running"
    }
@app.get("/health")
def health():
    return {
        "status": "ok"
    }

app.include_router(properties_router)
app.include_router(units_router)
app.include_router(tenants_router)
app.include_router(inspections_router)
app.include_router(maintenance_router)
app.include_router(rent_router)