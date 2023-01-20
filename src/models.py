import time
import subprocess
from pydantic import BaseModel, validator
from typing import Optional
from enum import Enum
from src.logger import logger

class Payload(BaseModel):
    token: str

class Conclusion(str, Enum):
    action_required = 'action_required'
    cancelled = 'cancelled'
    failure = 'failure'
    neutral = 'neutral'
    success = 'success'
    skipped = 'skipped'
    stale = 'stale'
    timed_out = 'timed_out'

class Command(BaseModel):
    title: str
    slug: str
    command: str
    check: bool
    fail_message: Optional[str]
    run_on_fail: Optional[bool] = False
    include_output: Optional[bool] = True
    # This value is used to determine if the output of the command should
    # update the env for future commands. This maintains backward compatibility with
    # atlantis and the `env` command steps.
    # https://www.runatlantis.io/docs/custom-workflows.html
    include_in_env: Optional[str] = None
    # TODO: figure out how best to implement
    # What we want to do is enable a way to format the output of the command
    output_filter: Optional[str] = None
    completed: bool = False
    duration: Optional[float] = None
    exit_code: Optional[int]
    output: Optional[str] = ""

    @validator("output", always=True)
    def _validate_output(cls, v):
        if v is None:
            return ""
        return v

    def run(self, env):
        start = time.perf_counter()
        logger.debug(self.command)
        o = subprocess.run(
            self.command,
            shell=True,
            env=env,
            cwd='/tmp',
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )

        stop = time.perf_counter()

        if o.returncode != 0 and self.fail_message:
            self.output += self.fail_message

        if self.include_output:
            self.output += o.stdout.decode('utf-8')

        logger.debug(o.stdout.decode('utf-8'))
        self.duration = stop - start
        self.exit_code = o.returncode
        self.completed = True
        return self

class Response(BaseModel):
    conclusion: Conclusion
    steps: list[Command]

class RequestV1(BaseModel):
    env: dict
    commands: list[Command]