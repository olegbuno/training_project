import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.exceptions import AppError
from app.orders import router as orders_router

logger = logging.getLogger(__name__)

app = FastAPI()
app.include_router(orders_router)


@app.exception_handler(AppError)
async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
    logger.exception("app_error", extra={"path": request.url.path})
    return JSONResponse(status_code=exc.status_code, content={"error": exc.message})
