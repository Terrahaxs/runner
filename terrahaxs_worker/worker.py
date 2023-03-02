import jwt
import requests
import semver
from terrahaxs_worker.settings import settings
from terrahaxs_worker.logger import logger
from terrahaxs_worker.models import Payload, Response, Request, Conclusion, Command
from terrahaxs_worker.command_runner import CommandRunner

def validate_payload_signature(payload):
    logger.info("Validating payload")
    resp = requests.post(f"{settings.api_url}/worker/validate", headers={settings.token_header: payload.token})

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

            return requests.post(f"{settings.api_url}/worker/callback", json=response.dict(),
                    headers={settings.token_header: payload.token})

        logger.info("Running job")
        command_dict = jwt.decode(payload.token, options={"verify_signature": False})

        runner = CommandRunner(Request(**command_dict))

        success, steps = runner.run()
        response = Response(
            steps=steps,
            conclusion = Conclusion.success if success else Conclusion.failure
        )
        logger.info(response)

    except Exception as e:
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
        req = requests.post(f"{settings.api_url}/worker/callback", json=response.dict(),
                    headers={settings.token_header: payload.token})
        req.raise_for_status()
