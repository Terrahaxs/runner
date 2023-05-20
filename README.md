## Terrahaxs Runner

The Terrahaxs Runner is responsible for executing tasks as part of your Terraform CI/CD Workflow. The Terrahaxs Runner is intended
to be flexible and deployed in any environment. You can use the Terrahaxs hosted runner or you can use it via GitHub Actions or
deploy it on self-hosted infrastructure and make it accessible via a public URL.

### Security

The Terrahaxs Runner is essentially a remote execution machine and therefore requires protection to prevent malicious actors from attempting
to run unauthorized commands. Before the runner executes any commands it verifies the signature of the payload it received with the Terrahaxs
public key. The Terrahaxs public key is retrieved from the Terrahaxs API. For more information on digital signatures checkout [this amazing
blog post](https://auth0.com/blog/how-to-explain-public-key-cryptography-digital-signatures-to-anyone/) by Auth0.

### Deployment Options

#### GitHub Action

Terrahaxs deploys a Docker Image with the Terrahaxs Runner, you can see the [repo here](https://github.com/Terrahaxs/github-action-worker).

If you would like to build a customized image with your own Terraform Versions/binaries you can fork/clone the repo and make your changes.

#### Lambda Function URL

For an example of how to deploy the Terrahaxs Runner as a Lambda Function with a Function URL look at [this repo](https://github.com/Terrahaxs/lambda-url-worker)

#### Other

The Terrahaxs Runner uses [FastAPI](https://fastapi.tiangolo.com/). To deploy a runner in another format you'll need to install
the Terrahaxs Runner and start the API. Here is a rough outline:

```
# requirements.txt

git+https://github.com/terrahaxs/runner.git
```

```python
# main.py

import uvicorn
from terrahaxs_runner import app

uvicorn.run(app, host="0.0.0.0", port=9000)
```

You can also inject any error handling or other code you may want to.


### Contributing

We welcome open source contributions to the Terrahaxs Runner.