import os

class CommandRunner:
    def __init__(self, request):
        self.request = request
        self.env = {**os.environ, **request.env}

    def run(self):
        skip_non_essential = False

        r = []
        for command in self.request.commands:
            if not skip_non_essential or command.run_on_fail:
                step = command.run(env=self.env)
                r.append(step)

                if step.include_in_env is not None:
                    self.env[step.include_in_env] = step.output

                # NOTE: Terrahaxs uses -detailed-exitcode for terraform plan to detect if the there are any updates required
                # to the infrastructure. An exit-code of two indicates changes are required but Terraform did not fail.
                if (step.slug == 'terraform_plan' and step.exit_code not in [0, 2]) or (step.slug != 'terraform_plan' and step.exit_code != 0):
                    skip_non_essential = True

        return (not skip_non_essential), r