## Terrahaxs Worker

The Terrahaxs Worker is responsible for executing tasks as part of your Terraform CI/CD Workflow. The Terrahaxs Worker is intended
to be flexible and deployed in any environment. You can use the Terrahaxs hosted worker or you can use it via GitHub Actions or
deploy it on self-hosted infrastructure and make it accessible via a public URL.

### Security

The Terrahaxs Worker is a remote execution machine and therefore requires protection to prevent malicious actors from attempting
to run unauthorized commands. To guard against malicious actors the Terrahaxs Worker receives a payload in the form of a signed [JWT](https://jwt.io/introduction/) and before executing any commands it validates the JWT using the Terrahaxs API. Any requests made which are not signed
will raise an exception.

### Contributing

We welcome open source contributions to the Terrahaxs Worker.