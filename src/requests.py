from src.models import RequestV1

class RequestFactory:
    @staticmethod
    def get(payload: dict):
        if payload['version'] == 1:
            return RequestV1(**payload)