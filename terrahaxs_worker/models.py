import time
import subprocess
from pydantic import BaseModel, validator
from typing import Optional
from enum import Enum

class Payload(BaseModel):
    payload: dict

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
    fail_message: Optional[str] = ""
    run_on_fail: Optional[bool] = False
    include_output: Optional[bool] = True
    # This value is used to determine if the output of the command should
    # update the env for future commands. This maintains backward compatibility with
    # atlantis and the `env` command steps.
    # https://www.runatlantis.io/docs/custom-workflows.html
    include_in_env: Optional[str] = None
    completed: bool = False
    duration: Optional[float] = None
    exit_code: Optional[int]
    output: Optional[str] = ""

    @validator("output", always=True)
    def _validate_output(cls, v): # pragma: no cover
        if v is None:
            return ""
        return v

    @validator("fail_message", always=True)
    def _validate_fail_message(cls, v): # pragma: no cover
        if v is None:
            return ""
        return v

    def run(self, env):
        start = time.perf_counter()
        dir = env['DIR'] if ('DIR' in env and self.slug not in ['clone', 'git_config']) else '/'
        print(f"Running command: {self.command} in {dir}")
        o = subprocess.run(
            self.command,
            shell=True,
            env=env,
            cwd=dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )

        stop = time.perf_counter()

        exit_code = o.returncode
        if (self.slug == 'terraform_plan' and exit_code not in [0, 2]) or (self.slug != 'terraform_plan' and exit_code != 0) and self.fail_message:
            self.output += self.fail_message

        if self.include_output:
            self.output += o.stdout.decode('utf-8')

        print(o.stdout.decode('utf-8'))
        self.duration = stop - start
        self.exit_code = o.returncode
        self.completed = True
        return self

class Response(BaseModel):
    conclusion: Conclusion
    steps: list[Command]
    request: dict

class Request(BaseModel):
    env: dict
    commands: list[Command]