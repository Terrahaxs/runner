import json
import requests
import os
from fastapi import FastAPI
import rollbar
from mangum import Mangum
from src.logger import logger
from src.settings import settings, ModeEnum
from src.command_runner import CommandRunnerFactory
from src.requests import RequestFactory
from src.models import Payload, Response
import jwt

rollbar.init(settings.rollbar_key, settings.env)
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
    logger.info("Validating payload")
    print(payload)
    # NOTE: We only need to validate the payload when the worker is receiving requests in API mode.
    # This is to prevent remote code execution from bad actors. When the worker is running in SQS mode
    # we know for sure that the payload is valid.
    req = requests.post(f"{settings.api_url}/worker/validate", headers={settings.token_header: payload.token})
    req.raise_for_status()
    do_work(payload)


def do_work(payload: Payload):
    logger.info("Running job")
    command_dict = jwt.decode(payload.token, options={"verify_signature": False})

    request = RequestFactory.get(command_dict)
    runner = CommandRunnerFactory.get(request)

    success, steps = runner.run()
    response = Response(
        steps=steps,
        conclusion = 'success' if success else 'failure'
    )
    logger.info(response)

    req = requests.post(f"{settings.api_url}/worker/callback", json=response.dict(),
                headers={settings.token_header: payload.token})
    req.raise_for_status()
    
@rollbar.lambda_function
def handler(event, context):  # pragma: no cover
    if settings.mode == ModeEnum.api:
        try:
            asgi_handler = Mangum(app)
            # Call the instance with the event arguments
            response = asgi_handler(event, context)

            return response
        except BaseException:
            rollbar.report_exc_info()
            rollbar.wait()
            raise
    elif settings.mode == ModeEnum.sqs:
        for record in event["Records"]:
            body = json.loads(record['body'])
            token = body['Message']
            do_work(Payload(token=token))
    elif settings.mode == ModeEnum.github_action:
        token = os.getenv('TOKEN')
        do_work(Payload(token=token))
    else:
        raise Exception("Invalid mode")