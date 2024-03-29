import os
from terrahaxs_runner.models import Command


class CommandRunner:
    def __init__(self, request, logger):
        self.request = request
        self.env = {**os.environ, **request.env}
        self.logger = logger

    def run(self):
        skip_non_essential = False

        r = []
        for command in self.request.commands:
            if not skip_non_essential or command.run_on_fail:
                try:
                    step = command.run(env=self.env, logger=self.logger)
                    r.append(step)
                except Exception as e:
                    step = Command(
                        title=command.title,
                        slug=command.slug,
                        command=command.command,
                        check=command.check,
                        output=str(e),
                        exit_code=1
                    )
                    r.append(step)

                if step.include_in_env is not None:
                    self.env[step.include_in_env] = step.output

                # NOTE: Terrahaxs uses -detailed-exitcode for terraform plan to detect if the there are any updates required
                # to the infrastructure. An exit-code of two indicates changes
                # are required but Terraform did not fail.
                if (step.slug == 'terraform_plan' and step.exit_code not in [0, 2]) or (
                        step.slug != 'terraform_plan' and step.exit_code != 0):
                    skip_non_essential = True

        return (not skip_non_essential), r
