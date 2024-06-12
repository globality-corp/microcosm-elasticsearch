#!/usr/bin/env python
from setuptools import find_packages, setup


project = "microcosm-elasticsearch"
version = "8.0.0"

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
    python_requires=">=3.11",
    keywords="microcosm",
    install_requires=[
        "boto3>=1.7.33",
        "elasticsearch>=7.0.0,<8",
        "elasticsearch-dsl>=7.0.0,<8",
        "microcosm>=4.0.0",
        "microcosm-flask>=6.0.0",
        "microcosm-metrics>=3.0.0",
        "requests[security]>=2.18.4",
        "urllib3>=1.25.10",
    ],
    extras_require={
        "test": [
            "coverage>=3.7.1",
            "PyHamcrest>=1.8.5",
            "pytest-cov>=5.0.0",
            "pytest>=6.2.5",
        ],
        "lint": [
            "flake8",
            "flake8-print",
            "flake8-isort",
        ],
        "typehinting": [
            "mypy",
        ],
    },
    setup_requires=[
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
