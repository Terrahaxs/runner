import requests
import semver
import base64
import json
import re
from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5
from Crypto.PublicKey import RSA
from terrahaxs_runner.settings import settings
from terrahaxs_runner.models import Payload, Response, Request, Conclusion, Command
from terrahaxs_runner.command_runner import CommandRunner
from terrahaxs_runner.logger import get as get_logger

logger = get_logger()


def runner(payload: Payload, signature: str):
    payload = payload.payload
    logger.append_keys(
        org=payload['org'],
        repo=payload['repo'],
        project_name=payload['project_name'])
    terrahaxs_info = get_terrahaxs_info()
    min_version = terrahaxs_info['min_runner_version']
    public_key = terrahaxs_info['public_key']

    verify_payload_signature(payload, signature, public_key)
    verify_runner_version(min_version, payload)
    verify_org(payload)
    verify_repo(payload)
    verify_project(payload)
    response = run(payload)

    req = requests.post(
        f"{settings.api_url}/runner/callback",
        json=response.dict(),
        headers={
            settings.token_header: payload['validation_jwt']})
    req.raise_for_status()
    return response


def get_terrahaxs_info():
    resp = requests.get(f"{settings.api_url}/health")
    resp.raise_for_status()
    return resp.json()


def verify_payload_signature(payload, signature: str, public_key):
    public_key = RSA.importKey(base64.b64decode(public_key).decode('utf-8'))
    message = json.dumps(payload).encode('utf-8')
    digest = SHA256.new()
    digest.update(message)
    sig = bytes.fromhex(signature)
    verifier = PKCS1_v1_5.new(public_key)
    verified = verifier.verify(digest, sig)

    if not verified:
        raise InvalidSignatureError('Payload signature is not verified')


def verify_runner_version(min_version, payload):
    logger.info(
        f'Runner Version: {settings.version}\nMin Version: {min_version}')

    if semver.VersionInfo.parse(settings.version).compare(min_version) < 0:
        raise UpgradeRunnerError(payload, min_version)


def verify_org(payload):
    _verify(payload['org'], settings.allowed_orgs, OrgNotAllowedError(payload))


def verify_repo(payload):
    _verify(
        payload['repo'],
        settings.allowed_repos,
        RepoNotAllowedError(payload))


def verify_project(payload):
    _verify(
        payload['project_name'],
        settings.allowed_projects,
        ProjectNotAllowedError(payload))


def _verify(name, allowed, exception):
    if allowed == '*':
        return

    a = allowed.split(',')

    found = False
    for o in a:
        if re.compile(o).match(name):
            found = True
    if found is False:
        raise exception


def run(payload):
    try:
        logger.info(f"Running Project: {payload['project_name']}")

        command_dict = payload

        runner = CommandRunner(Request(**command_dict), logger)

        success, steps = runner.run()
        response = Response(
            request=payload,
            steps=steps,
            conclusion=Conclusion.success if success else Conclusion.failure
        )
        logger.info(f"Project: {payload['project_name']} complete")
        return response

    except Exception as e:
        logger.error(e)
        response = Response(
            request=payload,
            conclusion=Conclusion.failure,
            steps=[
                Command(
                    title='runner Error',
                    slug='runner_error',
                    command='',
                    check=False,
                    output=str(e)
                )
            ]
        )


class InvalidSignatureError(Exception):
    pass


class OrgNotAllowedError(Exception):
    def __init__(self, payload):
        message = f"This runner is not permitted to run jobs for the {payload['org']} organization"
        response = Response(
            request=payload,
            conclusion=Conclusion.failure,
            steps=[
                Command(
                    title='Org Not Allowed',
                    slug='org_not_allowed',
                    command='',
                    check=True,
                    output=message
                )
            ]
        )

        req = requests.post(
            f"{settings.api_url}/runner/callback",
            json=response.dict(),
            headers={
                settings.token_header: payload['response_jwt']})
        req.raise_for_status()

        super().__init__(message)


class RepoNotAllowedError(Exception):
    def __init__(self, payload):
        message = f"This runner is not permitted to run jobs for the {payload['repo']} repo"
        response = Response(
            request=payload,
            conclusion=Conclusion.failure,
            steps=[
                Command(
                    title='Repo Not Allowed',
                    slug='repo_not_allowed',
                    command='',
                    check=True,
                    output=message)
            ]
        )

        req = requests.post(
            f"{settings.api_url}/runner/callback",
            json=response.dict(),
            headers={
                settings.token_header: payload['response_jwt']})
        req.raise_for_status()
        super().__init__(message)


class ProjectNotAllowedError(Exception):
    def __init__(self, payload):
        message = f"This runner is not permitted to run project {payload['project_name']}"

        response = Response(
            request=payload,
            conclusion=Conclusion.failure,
            steps=[
                Command(
                    title='Project Not Allowed',
                    slug='project_not_allowed',
                    command='',
                    check=True,
                    output=message)
            ]
        )

        req = requests.post(
            f"{settings.api_url}/runner/callback",
            json=response.dict(),
            headers={
                settings.token_header: payload['response_jwt']})
        req.raise_for_status()
        super().__init__(message)


class UpgradeRunnerError(Exception):
    def __init__(self, payload, min_version):
        message = f"Please upgrade your runner version. The minimum supported version is {min_version}."

        response = Response(
            request=payload,
            conclusion=Conclusion.failure,
            steps=[
                Command(
                    title='Project Not Allowed',
                    slug='project_not_allowed',
                    command='',
                    check=True,
                    output=message)
            ]
        )

        req = requests.post(
            f"{settings.api_url}/runner/callback",
            json=response.dict(),
            headers={
                settings.token_header: payload['response_jwt']})
        req.raise_for_status()
        super().__init__(message)
