"""New original, single-process teaching API; not durable production execution.
The literal bearer values below are public fictional lab selectors, not credentials.
"""
from dataclasses import dataclass
from threading import Lock
from typing import Annotated, Literal
from uuid import uuid4
from fastapi import (BackgroundTasks, Depends, FastAPI, File, Header,
    HTTPException, Request, UploadFile, WebSocket, WebSocketDisconnect)
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, ConfigDict, Field

class TaskCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str = Field(strict=True, min_length=1, max_length=80)
    retries: int = Field(default=0, strict=True, ge=0, le=3)

class TaskView(BaseModel):
    id: str
    title: str
    status: str

class StatusUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: Literal["running", "succeeded", "failed", "cancelled"]

@dataclass
class RequestResource:
    id: str

DEMO_TENANTS = {"lesson-alpha": "alpha", "lesson-beta": "beta"}
TRANSITIONS = {
    "queued": {"running", "cancelled"},
    "running": {"succeeded", "failed", "cancelled"},
    "succeeded": set(), "failed": set(), "cancelled": set(),
}
bearer = HTTPBearer(auto_error=False)

def actor(credentials: Annotated[HTTPAuthorizationCredentials | None,
                               Depends(bearer)]) -> str:
    tenant = DEMO_TENANTS.get(credentials.credentials) if credentials else None
    if tenant is None:
        raise HTTPException(401, "unauthorized",
                            headers={"WWW-Authenticate": "Bearer"})
    return tenant

def request_resource(request: Request):
    resource = RequestResource(str(uuid4()))
    request.app.state.resource_events.append(("open", resource.id))
    try:
        yield resource
    finally:
        request.app.state.resource_events.append(("close", resource.id))

def create_app():
    app = FastAPI(title="Original teaching task API", version="1")
    app.add_middleware(CORSMiddleware, allow_origins=["https://lesson.example"],
                       allow_credentials=False, allow_methods=["GET", "POST", "PATCH"],
                       allow_headers=["Authorization", "Content-Type", "Idempotency-Key"])
    app.state.tasks = {}
    app.state.keys = {}
    app.state.lock = Lock()
    app.state.audit = []
    app.state.resource_events = []

    @app.exception_handler(RequestValidationError)
    async def invalid_input(request, exc):
        # Intentionally omit input values from the response.
        return JSONResponse(status_code=422, content={
            "code": "invalid_input",
            "fields": [list(error["loc"]) for error in exc.errors()],
        })

    @app.post("/v1/tasks", response_model=TaskView, status_code=201)
    def create_task(body: TaskCreate, background: BackgroundTasks,
                    tenant: Annotated[str, Depends(actor)],
                    key: Annotated[str | None, Header(alias="Idempotency-Key",
                                                   min_length=1, max_length=80)] = None):
        payload = body.model_dump()
        with app.state.lock:
            scoped = (tenant, key)
            if key and scoped in app.state.keys:
                prior_payload, task_id = app.state.keys[scoped]
                if prior_payload != payload:
                    raise HTTPException(409, "idempotency_key_conflict")
                return dict(app.state.tasks[task_id])
            task_id = str(uuid4())
            row = dict(id=task_id, title=body.title, tenant=tenant,
                       retries=body.retries, status="queued", private_note="lab only")
            app.state.tasks[task_id] = row
            if key:
                app.state.keys[scoped] = (payload, task_id)
        # This process-local append is intentionally not a durable queue.
        background.add_task(app.state.audit.append, {"event": "created", "id": task_id})
        return row

    @app.get("/v1/tasks/{task_id}", response_model=TaskView)
    def get_task(task_id: str, tenant: Annotated[str, Depends(actor)]):
        with app.state.lock:
            row = app.state.tasks.get(task_id)
            if row is None or row["tenant"] != tenant:
                raise HTTPException(404, "task_not_found")
            return dict(row)

    @app.patch("/v1/tasks/{task_id}", response_model=TaskView)
    def change_status(task_id: str, body: StatusUpdate,
                      tenant: Annotated[str, Depends(actor)]):
        with app.state.lock:
            row = app.state.tasks.get(task_id)
            if row is None or row["tenant"] != tenant:
                raise HTTPException(404, "task_not_found")
            if body.status == row["status"]:
                return dict(row)  # Repeating the same transition is a no-op.
            if body.status not in TRANSITIONS[row["status"]]:
                raise HTTPException(409, "invalid_transition")
            row["status"] = body.status
            return dict(row)

    @app.get("/lab/dependency-cache")
    def dependency_cache(
        first: Annotated[RequestResource, Depends(request_resource, scope="function")],
        second: Annotated[RequestResource, Depends(request_resource, scope="function")],
    ):
        return {"same": first is second}

    @app.get("/lab/dependency-uncached")
    def dependency_uncached(
        first: Annotated[RequestResource, Depends(request_resource, scope="function")],
        second: Annotated[RequestResource, Depends(request_resource, use_cache=False,
                                                 scope="function")],
    ):
        return {"same": first is second}

    @app.get("/lab/dependency-error")
    def dependency_error(
        resource: Annotated[RequestResource, Depends(request_resource, scope="function")],
    ):
        raise HTTPException(409, "lab_failure")

    @app.post("/v1/uploads")
    async def inspect_upload(
        tenant: Annotated[str, Depends(actor)],
        file: Annotated[UploadFile, File()],
    ):
        total = 0
        try:
            while chunk := await file.read(1024):
                total += len(chunk)
                if total > 4096:
                    raise HTTPException(413, "upload_too_large")
            return {"bytes": total}
        finally:
            await file.close()

    @app.websocket("/ws")
    async def echo(websocket: WebSocket):
        # Example only. A real handshake also needs explicit origin policy.
        if websocket.headers.get("authorization") != "Bearer lesson-alpha":
            await websocket.close(code=4401)
            return
        await websocket.accept()
        try:
            while True:
                message = await websocket.receive_text()
                if len(message) > 128:
                    await websocket.close(code=1009)
                    return
                await websocket.send_json({"echo": message})
        except WebSocketDisconnect:
            return
    return app

app = create_app()
