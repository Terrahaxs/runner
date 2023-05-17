import jwt
import requests
import semver
from terrahaxs_worker.settings import settings
from terrahaxs_worker.models import Payload, Response, Request, Conclusion, Command
from terrahaxs_worker.command_runner import CommandRunner

def validate_payload_signature(payload):
    print("Validating payload")
    resp = requests.post(f"{settings.api_url}/worker/validate", headers={settings.token_header: payload.payload['validation_jwt']})

    try:
        resp.raise_for_status()
    except Exception as e:
        print(e)
        raise Exception("Could not validate JWT.")

    return resp.json()

def worker(payload: Payload):
    response = None
    print(f'Worker Version: {settings.version}')
    try:
        min_version = validate_payload_signature(payload)['min_worker_version']

        if semver.VersionInfo.parse(settings.version).compare(min_version) < 0:
            response = Response(
                request=payload.payload,
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
                    headers={settings.token_header: payload.payload['validation_jwt']})

        print("Running job")

        command_dict = payload.payload

        runner = CommandRunner(Request(**command_dict))

        success, steps = runner.run()
        response = Response(
            request=payload.payload,
            steps=steps,
            conclusion = Conclusion.success if success else Conclusion.failure
        )
        print(response)

    except Exception as e:
        print(e)
        response = Response(
            request=payload.payload,
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
                    headers={settings.token_header: payload.payload['validation_jwt']})
        req.raise_for_status()
