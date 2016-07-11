#!/usr/bin/env python
from setuptools import find_packages, setup

project = "microcosm-elasticsearch"
version = "0.3.0"

setup(
    name=project,
    version=version,
    description="Elasticsearch client configuration",
    author="Globality Engineering",
    author_email="engineering@globality.com",
    url="https://github.com/globality-corp/microcosm-elasticsearch",
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    include_package_data=True,
    zip_safe=False,
    keywords="microcosm",
    install_requires=[
        "boto3>=1.3.1",
        "botocore>=1.4.23",
        "elasticsearch>=2.0.0",
        "microcosm>=0.9.0",
        "requests[security]>=2.9.1",
        "requests-aws4auth>=0.9",
    ],
    setup_requires=[
        "nose>=1.3.6",
    ],
    dependency_links=[
    ],
    entry_points={
        "microcosm.factories": [
            "elasticsearch_client = microcosm_elasticsearch.factories:configure_elasticsearch_client"
        ],
    },
    tests_require=[
        "coverage>=3.7.1",
        "mock>=1.0.1",
        "PyHamcrest>=1.8.5",
    ],
)
