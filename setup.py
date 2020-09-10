#!/usr/bin/env python
from setuptools import find_packages, setup


project = "microcosm-elasticsearch"
version = "7.0.0"

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
    python_requires=">=3.6",
    keywords="microcosm",
    install_requires=[
        "boto3>=1.7.33",
        "elasticsearch>=7.0.0",
        "elasticsearch-dsl>=7.0.0",
        "microcosm>=2.12.0",
        "microcosm-flask>=2.8.0",
        "microcosm-metrics>=2.1.0",
        "requests[security]>=2.18.4",
        "urllib3<1.25",
    ],
    setup_requires=[
        "nose>=1.3.6",
    ],
    dependency_links=[
    ],
    entry_points={
        "microcosm.factories": [
            "elasticsearch_client = microcosm_elasticsearch.factories:configure_elasticsearch_client",
            "elasticsearch_index_registry = microcosm_elasticsearch.registry:IndexRegistry",
            "index_status_convention = microcosm_elasticsearch.index_status.convention:configure_status_convention",
        ],
    },
    tests_require=[
        "coverage>=4.4.1",
        "PyHamcrest>=1.9.0",
    ],
)
