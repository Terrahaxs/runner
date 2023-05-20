from fastapi import FastAPI
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
def root(payload: Payload): # pragma: no cover
    # TODO: get signature info and pass to runner
    runner(payload)