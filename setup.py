from setuptools import find_packages
from setuptools import setup

setup(
    name="terrahaxs-runner",
    version="0.0.13",
    description="Terrahaxs runner to execute Terraform CI/CD commands.",
    packages=find_packages(exclude=["features"]),
    include_package_data=True,
    install_requires=[
        "requests",
        # AWS command line is used to upload plans
        "awscli",
        "PyJWT",
        # Needed to download the previously saved plans
        "botocore[crt]",
        "boto3",
        "semver",
        "fastapi",
        "uvicorn",
        "pycryptodome==3.14.1",
        "aws-lambda-powertools==2.1.0",
    ]
)
