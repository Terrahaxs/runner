from fastapi import FastAPI
from terrahaxs_worker.settings import settings
from terrahaxs_worker.models import Payload
from terrahaxs_worker.worker import worker

app = FastAPI()

@app.get('/health')
def health(): # pragma: no cover
    return {
        "app_url": settings.api_url,
        "healthy": True,
        "version": settings.version
    }

@app.post('/')
def root(payload: Payload): # pragma: no cover
    worker(payload)