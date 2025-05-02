from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.security import OAuth2PasswordBearer  # noqa: F401

from uptime_monitor.database import Base, engine, User  # noqa: F401
from monitor.api import router as monitor_router
from users.api import router as users_router
from monitor.tasks import check_url_status  # noqa: F401

Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


app.include_router(monitor_router, prefix="/api/monitor", tags=["monitor"])
app.include_router(users_router, prefix="/api/users", tags=["users"])


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Uptime Monitor API",
        version="1.0.0",
        description="Monitoring API with JWT authentication",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method.setdefault("security", [{"BearerAuth": []}])
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
