from behave import *
from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5
from Crypto.PublicKey import RSA
from _pytest.monkeypatch import MonkeyPatch
import json
import base64
import requests_mock
from terrahaxs_runner.runner import runner, InvalidSignatureError, OrgNotAllowedError, RepoNotAllowedError, ProjectNotAllowedError, UpgradeRunnerError
from terrahaxs_runner.models import Payload, Command, Conclusion
from terrahaxs_runner.settings import settings

m = requests_mock.Mocker()

@given('the worker is not up to date')
def step_impl(context):
    m.get(f"{settings.api_url}/health", json={
        'min_runner_version': '0.0.9',
        'public_key': 'LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0KTUlHZk1BMEdDU3FHU0liM0RRRUJBUVVBQTRHTkFEQ0JpUUtCZ1FDOGM5dlpTd0lnaE5zWGFJTXM0aFo1anBUcgpGMkFadStHdWtzRy9ZUWViNWxSS25Ca0pFYXFVQWlDdno4cEdnNHQxWXF3SUdEN21CQk5VUGgwMHZFSXNneHZ3CnFFbnVhVkMrK1Y2Vm5nZ1E3ZVNiYmliMDJQWnJ3Q2FmVzd3eU05TllVMTRoUEZkbm95N2FBSlFBRGNFYXVvZHkKMzJwenlJY1QvUDFQUC91T2N3SURBUUFCCi0tLS0tRU5EIFBVQkxJQyBLRVktLS0tLQo='
    })

@given('a mocked terrahaxs api')
def step_impl(context):
    m.get(f"{settings.api_url}/health", json={
        'min_runner_version': '0.0.7',
        'public_key': 'LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0KTUlHZk1BMEdDU3FHU0liM0RRRUJBUVVBQTRHTkFEQ0JpUUtCZ1FDOGM5dlpTd0lnaE5zWGFJTXM0aFo1anBUcgpGMkFadStHdWtzRy9ZUWViNWxSS25Ca0pFYXFVQWlDdno4cEdnNHQxWXF3SUdEN21CQk5VUGgwMHZFSXNneHZ3CnFFbnVhVkMrK1Y2Vm5nZ1E3ZVNiYmliMDJQWnJ3Q2FmVzd3eU05TllVMTRoUEZkbm95N2FBSlFBRGNFYXVvZHkKMzJwenlJY1QvUDFQUC91T2N3SURBUUFCCi0tLS0tRU5EIFBVQkxJQyBLRVktLS0tLQo='
    })

    context.worker_callback = m.post(f"{settings.api_url}/runner/callback", json={})

@given('an invalid signature')
def step_impl(context):
    context.signature = '5b6cc2b35edac7cd83d21247c11637714a5a72942f816f4b6f2462ca35b9631d968b8de86370c15aa49b8599d3a341e2c1732b80a28e0ccfa8b08eb2c1586e6f8b29f67745b4756baf4d61fdb90c84f4b8b277f252c73af47585cb257cbb3a3c10f08a4540d3d637f55e4104624b480d9972c20dcaa94e077f06dc0e2f78025e'

@given('allowed orgs is {orgs}')
def step_impl(context, orgs):
    MonkeyPatch().setattr(settings, 'allowed_orgs', orgs)

@given('allowed repos is {repos}')
def step_impl(context, repos):
    settings.allowed_repos = repos    

@given('allowed projects is {projects}')
def step_impl(context, projects):
    settings.allowed_projects = projects

@given('a {payload} payload')
def step_impl(context, payload):
    if payload == 'worker.request':
        context.payload = {
                'validation_jwt': 'foo',
                'env': {},
                'org': 'Terrahaxs',
                'repo': 'test',
                'project_name': 'test/default',
                'response_jwt': 'foo',
                'commands': [
                    Command(
                        title='success',
                        slug='success',
                        command='exit 0',
                        include_in_env=True,
                        check=True
                    ).dict()
                ]
            }
    elif payload == 'worker.failed_step':
        context.payload = {
                'validation_jwt': 'foo',
                'env': {},
                'org': 'Terrahaxs',
                'repo': 'test',
                'project_name': 'test/default',
                'response_jwt': 'foo',
                'commands': [
                    Command(
                        title='failed',
                        slug='failed',
                        command='exit 1',
                        fail_message='Append to failure',
                        check=True
                    ).dict(),
                    Command(
                        title='echo',
                        slug='echo',
                        command='echo foo',
                        check=True,
                        run_on_fail=True
                    ).dict()
                ]
            }  
    
    private_key = base64.b64decode('LS0tLS1CRUdJTiBSU0EgUFJJVkFURSBLRVktLS0tLQpNSUlDWFFJQkFBS0JnUUM4Yzl2WlN3SWdoTnNYYUlNczRoWjVqcFRyRjJBWnUrR3Vrc0cvWVFlYjVsUktuQmtKCkVhcVVBaUN2ejhwR2c0dDFZcXdJR0Q3bUJCTlVQaDAwdkVJc2d4dndxRW51YVZDKytWNlZuZ2dRN2VTYmJpYjAKMlBacndDYWZXN3d5TTlOWVUxNGhQRmRub3k3YUFKUUFEY0VhdW9keTMycHp5SWNUL1AxUFAvdU9jd0lEQVFBQgpBb0dBYXBZdzgxNk1UbTQyS0xBdytSTEsyV2UrYkpVbEFva1VaUk9XUjdNT2hhdXBZeVdVdDE5cGxocjU5OVpUCnRyd3lCV3VRbDJkM004dDhUenB1ZEdSQ0hFWnJ0N1d5MHc3Tm1OV3dGbDQydlJaRnV5NlJoNWVDOHRDSnRDWG8KbzM4UVpGdzd4TTN2REZOTExrK21sRFQ5Y093dW9kN3lGNjMzL3pFVUhHZURRcUVDUVFENXdYcU1UVmpydTUyMApOdlJTYVRSM21SRjcvQWtPdXdaMmRSb2lVWEhNaWNCaldmU1hmVGVDZ1VsMGRhdlFPSWJMMG50VW9tVzNzMi94CkltdytTOE9qQWtFQXdTb0UxWm1HNWw1MzNGdUE5UjN6YnNnN0lvTzQvSEhmQmhxTVk0KzRBNlI4WWpFMStnQ2kKVzN1TFVnSTRqL3dVME14ZGtzNlZoeFpqNHAxZitVdzI4UUpCQVBROXkzUk5aN29RWGVjUkh0bEEzUGhnam9LcgpOTWhkQ2JMcVRjWmwwMTN0RUdHWVpPT0lwckpQY09BYyt3ckRYTDhTZFYyTSt1QXM4RG5tS2VpNSt2VUNRUUNaCmw1NjJkVmhGcjFJaFhvVUE0cXJoS01lVW55YWxYS29Zd1YxbUFTNHhmMFlFRWRzNGllNlBUWUl2V0dLL1lwTHUKbjhHNzdSWUtqeXduVWpteEVnQVJBa0JNS1QxQkpjeFZuWlpQZ3MxT2c3VE1mSzdkTTBiajVlQTJLZGRhSjdtZgpGVURzRkZTOFhyczFYSk1WeUx6elN0TElTL0k0eDMraW41Z0JVWHhZVklxbgotLS0tLUVORCBSU0EgUFJJVkFURSBLRVktLS0tLQo=').decode('utf-8')
    private_key = RSA.importKey(private_key)
    message = json.dumps(context.payload).encode('utf-8')
    digest = SHA256.new()
    digest.update(message)
    signer = PKCS1_v1_5.new(private_key)
    sig = signer.sign(digest)
    context.signature = sig.hex()

@when('I run the runner')
def step_impl(context):
    with m:
        try:
            context.result = runner(context.payload, context.signature)
        except Exception as e:
            print(e)
            context.result = e

@then('the result is {result}')
def step_impl(context, result):
    print(context.result)
    assert context.result.conclusion == result, context.result.conclusion

@then('there are {number} steps returned')
def step_impl(context, number):
    assert len(context.result.steps) == int(number), context.result.steps

@then('a InvalidSignatureError is raised')
def step_impl(context):
    assert isinstance(context.result, InvalidSignatureError), type(context.result)

@then('a OrgNotAllowedError is raised')
def step_impl(context):
    assert isinstance(context.result, OrgNotAllowedError), type(context.result)

@then('a RepoNotAllowedError is raised')
def step_impl(context):
    assert isinstance(context.result, RepoNotAllowedError), type(context.result)


@then('a ProjectNotAllowedError is raised')
def step_impl(context):
    assert isinstance(context.result, ProjectNotAllowedError), type(context.result)

@then('a UpgradeRunnerError is raised')
def step_impl(context):
    assert isinstance(context.result, UpgradeRunnerError), type(context.result)