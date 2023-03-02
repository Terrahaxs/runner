import jwt
import requests
import semver
from terrahaxs_worker.settings import settings
from terrahaxs_worker.logger import logger
from terrahaxs_worker.models import Payload, Response, Request, Conclusion, Command
from terrahaxs_worker.command_runner import CommandRunner

def validate_payload_signature(payload):
    logger.info("Validating payload")
    if payload.token is not None:
        resp = requests.post(f"{settings.api_url}/worker/validate", headers={settings.token_header: payload.token})
    elif payload.payload is not None:
        resp = requests.post(f"{settings.api_url}/worker/validate", headers={settings.token_header: payload.payload['validation_jwt']})

    try:
        resp.raise_for_status()
    except Exception as e:
        logger.error(e)
        raise Exception("Could not validate JWT.")

    return resp.json()

def worker(payload: Payload):
    response = None
    logger.info(f'Worker Version: {settings.version}')
    try:
        min_version = validate_payload_signature(payload)['min_worker_version']

        if semver.VersionInfo.parse(settings.version).compare(min_version) < 0:
            response = Response(
                conclusion=Conclusion.failure,
                steps=[
                    Command(
                        title='Version Check',
                        slug='version_check',
                        command='',
                        check=True,
                        output=f"Please upgrade your worker version. The minimum supported version is {min_version}."
                    )
                ]
            )

            if payload.token is not None:
                return requests.post(f"{settings.api_url}/worker/callback", json=response.dict(),
                        headers={settings.token_header: payload.token})
            elif payload.payload is not None:
                return requests.post(f"{settings.api_url}/worker/callback", json=response.dict(),
                        headers={settings.token_header: payload.payload['validation_jwt']})

        logger.info("Running job")

        if payload.token is not None:
            command_dict = jwt.decode(payload.token, options={"verify_signature": False})
        elif payload.payload is not None:
            command_dict = payload.payload

        runner = CommandRunner(Request(**command_dict))

        success, steps = runner.run()
        response = Response(
            steps=steps,
            conclusion = Conclusion.success if success else Conclusion.failure
        )
        logger.info(response)

    except Exception as e:
        logger.error(e)
        response = Response(
            conclusion=Conclusion.failure,
            steps=[
                Command(
                    title='Worker Error',
                    slug='worker_error',
                    command='',
                    check=False,
                    output=str(e)
                )
            ]
        )
    finally:
        if payload.token is not None:
            req = requests.post(f"{settings.api_url}/worker/callback", json=response.dict(),
                        headers={settings.token_header: payload.token})
            req.raise_for_status()
        elif payload.payload is not None:
            req = requests.post(f"{settings.api_url}/worker/callback", json=response.dict(),
                        headers={settings.token_header: payload.payload['validation_jwt']})
            req.raise_for_status()
