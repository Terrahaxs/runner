import pytest
from datetime import datetime, timedelta
from jose import jwt
from src.settings import settings
from src.worker import worker
from src.models import Payload, Command, Conclusion

@pytest.fixture(autouse=True)
def mock_worker_callback(requests_mock):
    adapter = requests_mock.post(f'{settings.api_url}/worker/callback')
    yield adapter

def test_exception_is_raised_if_jwt_is_not_valid(requests_mock):
    requests_mock.register_uri('POST', f"{settings.api_url}/worker/validate", json={'message': 'unathorized'}, status_code=401)

    with pytest.raises(Exception):
        worker(payload=Payload(token='foo'))

@pytest.fixture(autouse=True)
def mock_success_validation(requests_mock):
    requests_mock.post(f"{settings.api_url}/worker/validate", json={'min_worker_version': '0.0.0'})

def create_jwt(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=10)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, 'foo', algorithm='HS256')
    return encoded_jwt

def test_failure_returned_if_step_fails(mock_worker_callback):
    token = create_jwt({
            'env': {},
            'commands': [
                Command(
                    title='fail',
                    slug='fail',
                    command='exit 1',
                    check=True
                ).dict()
            ]
        })

    worker(Payload(token=token))
    
    assert mock_worker_callback.last_request.json()['conclusion'] == Conclusion.failure

def test_success_is_returned_if_all_steps_succeed(mock_worker_callback):
    token = create_jwt({
            'env': {},
            'commands': [
                Command(
                    title='success',
                    slug='success',
                    command='exit 0',
                    check=True
                ).dict()
            ]
        })

    worker(Payload(token=token))
    
    assert mock_worker_callback.last_request.json()['conclusion'] == Conclusion.success


def test_env_updated_if_included_in_env_set(mock_worker_callback):
    token = create_jwt({
            'env': {},
            'commands': [
                Command(
                    title='success',
                    slug='success',
                    command='echo foo',
                    include_in_env='FOO',
                    check=True
                ).dict(),
                Command(
                    title='success',
                    slug='success',
                    command='echo $FOO',
                    check=True
                ).dict()
            ]
        })

    worker(Payload(token=token))
    
    assert 'foo' in mock_worker_callback.last_request.json()['steps'][1]['output']

def test_all_essential_steps_are_executed(mock_worker_callback):
    token = create_jwt({
            'env': {},
            'commands': [
                Command(
                    title='fail',
                    slug='fail',
                    command='exit 1',
                    check=True
                ).dict(),
                Command(
                    title='foo',
                    slug='foo',
                    command='echo foo',
                    check=True,
                    run_on_fail=True
                ).dict()
            ]
        })

    worker(Payload(token=token))
    
    assert 'foo' in mock_worker_callback.last_request.json()['steps'][1]['output']


def test_exception_raised_if_supported_version_not_met(requests_mock, mock_worker_callback):
    """
    The Terrahaxs API should respond with min and max supported
    worker version - if this requirement is not met raise an exception and
    report to the Terrahaxs API that requirement is not met so that it can update
    the Check Run Status"""
    requests_mock.post(f"{settings.api_url}/worker/validate", json={'min_worker_version': '10.0.0'})
    token = create_jwt({
            'env': {},
            'commands': [
                Command(
                    title='success',
                    slug='success',
                    command='exit 0',
                    check=True
                ).dict()
            ]
        })

    worker(Payload(token=token))
    
    assert mock_worker_callback.last_request.json()['conclusion'] == Conclusion.failure