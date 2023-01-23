## Terrahaxs Worker

The Terrahaxs Worker is responsible for executing tasks as part of your Terraform CI/CD Workflow. The Terrahaxs Worker is intended
to be flexible and deployed in any environment. You can use the Terrahaxs hosted worker or you can use it via GitHub Actions or
deploy it on self-hosted infrastructure and make it accessible via a public URL.

### Security

The Terrahaxs Worker is a remote execution machine and therefore requires protection to prevent malicious actors from attempting
to run unauthorized commands. To guard against malicious actors the Terrahaxs Worker receives a payload in the form of a signed [JWT](https://jwt.io/introduction/) and before executing any commands it validates the JWT using the Terrahaxs API. Any requests made which are not signed
will raise an exception.

### Deployment Options

#### GitHub Action

Terrahaxs deploys a Docker Image with the Terrahaxs Worker, you can see the [repo here](https://github.com/Terrahaxs/github-action-worker).

If you would like to build a customized image with your own Terraform Versions/binaries you can fork/clone the repo and make your changes.

#### Lambda Function URL

For an example of how to deploy the Terrahaxs Worker as a Lambda Function with a Function URL look at [this repo](https://github.com/Terrahaxs/lambda-url-worker)

#### Other

The Terrahaxs Worker uses [FastAPI](https://fastapi.tiangolo.com/). To deploy a worker in another format you'll need to install
the Terrahaxs Worker and start the API. Here is a rough outline:

```
# requirements.txt

git+https://github.com/terrahaxs/worker.git
```

```python
# main.py

import uvicorn
from terrahaxs_worker import app

uvicorn.run(app, host="0.0.0.0", port=9000)
```

You can also inject any error handling or other code you may want to.


### Contributing

We welcome open source contributions to the Terrahaxs Worker.