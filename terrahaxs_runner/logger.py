import os
from terrahaxs_runner.settings import settings


def get():
    # Note: For some reason logging in GitHub Actions doesn't work unless
    # you use the print statement
    if os.getenv('GITHUB_ACTIONS') is not None:  # pragma: no cover
        class Logger:
            def __init__(self):
                pass

            def info(self, message):
                print(message)

            def error(self, message):
                print(message)

            def debug(message):
                print(message)
        return Logger()
    else:
        from aws_lambda_powertools import Logger
        return Logger()
