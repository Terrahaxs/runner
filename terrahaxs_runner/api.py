from fastapi import FastAPI, Request, HTTPException
from terrahaxs_runner.settings import settings
from terrahaxs_runner.models import Payload
from terrahaxs_runner.runner import runner
from terrahaxs_runner.logger import logger

app = FastAPI()


@app.get('/health')
def health():  # pragma: no cover
    return {
        "app_url": settings.api_url,
        "healthy": True,
        "version": settings.version
    }


@app.post('/')
def root(request: Request, payload: Payload):  # pragma: no cover
    if request.headers.get('X-Terrahaxs-Signature') is None:
        logger.error("X-Terrahaxs-Signature header is missing.")
        raise HTTPException(
            status_code=401,
            detail="Terrahaxs signature could not be verified.")

    runner(payload, request.headers.get('X-Terrahaxs-Signature'))
