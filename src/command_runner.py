import os
from src.models import RequestV1

class CommandRunnerV1:
    def __init__(self, request):
        self.request = request
        self.request.env['PATH'] = os.environ['PATH']

    def run(self):
        skip_non_essential = False

        r = []
        for command in self.request.commands:
            if not skip_non_essential or command.run_on_fail:
                step = command.run(env=self.request.env)
                r.append(step)

                if (step.slug == 'terraform_plan' and step.exit_code not in [0, 2]) or (step.slug != 'terraform_plan' and step.exit_code != 0):
                    skip_non_essential = True

        return (not skip_non_essential), r

class CommandRunnerFactory:
    @staticmethod
    def get(request):
        if isinstance(request, RequestV1):
            return CommandRunnerV1(request)
        else: # pragma: no cover
            raise Exception("Invalid request version")
