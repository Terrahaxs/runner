from setuptools import find_packages
from setuptools import setup

setup(
    name="terrahaxs-worker",
    version="0.1",
    description="Terrahaxs Worker to execute Terraform CI/CD commands.",
    packages=find_packages(exclude=["tests"]),
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
    ]
)
