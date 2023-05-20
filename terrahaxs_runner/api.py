from fastapi import FastAPI, Request
from terrahaxs_runner.settings import settings
from terrahaxs_runner.models import Payload
from terrahaxs_runner.runner import runner

app = FastAPI()

@app.get('/health')
def health(): # pragma: no cover
    return {
        "app_url": settings.api_url,
        "healthy": True,
        "version": settings.version
    }

@app.post('/')
def root(request: Request, payload: Payload): # pragma: no cover
    assert request.headers.get('X-Worker-Signature') is not None, "Missing signature header."

    runner(payload, request.headers.get('X-Terrahaxs-Runner-Signature'))