from fastapi import FastAPI
from src.settings import settings
from src.models import Payload
from src.worker import worker

app = FastAPI()

@app.get('/health')
def health(): # pragma: no cover
    return {
        "app_url": settings.api_url,
        "healthy": True,
        "version": settings.version
    }

@app.post('/')
def root(payload: Payload):
    worker(payload)