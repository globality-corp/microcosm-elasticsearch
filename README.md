# microcosm-elasticsearch

Elasticsearch configuration using [microcosm](https://github.com/globality-corp/microcosm) wiring.

[![Circle CI](https://circleci.com/gh/globality-corp/microcosm-elasticsearch/tree/develop.svg?style=svg)](https://circleci.com/gh/globality-corp/microcosm-elasticsearch/tree/develop)


## Usage

 - Provides a `microcosm` compatible `Elasticsearch` client
    -  Supports signed requests for AWS Elasticsearch using AWS4Auth
    -  Supports IAM Role-based credentials based on instance metadata when running on EC2
    -  Provides proper unicode support for Python 2.x / 3.x codebases

 - Includes an implementation of a persistence `Store` using Elasticsarch


## Testing

Unit tests depend on a running instance of Elasticsearch:

 1. Bring up the ES with `docker-compose`:

         docker-compose up -d

 2. Run tests:

         nosetests


## Configuration

When using with an AWS Elasticsearch instance, use:

    config.elasticsearch_client.use_aws4auth = 'true'
    config.elasticsearch_client.aws_access_key_id = 'aws-access-key-id'  # Will try to read from AWS_ACCESS_KEY_ID env var. by default
    config.elasticsearch_client.aws_secret_access_key = 'aws-secret-access-key'  # Will try to read from AWS_SECRET_ACCESS_KEY env var. by default
    config.elasticsearch_client.aws_region = 'aws-region'  # Will try to read from AWS_REGION env var. by default

When configuring for running on an EC2 instance and use the instance's IAM role-provided AWS credentials:

    config.elasticsearch_client.use_aws4auth = 'true'
    config.elasticsearch_client.use_aws_instance_metadata = 'true'

For proper Unicode support on Python 2.x, use:

    config.elasticsearch_client.use_python2_serializer = 'true'
