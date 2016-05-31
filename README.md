# microcosm-elasticsearch

Elasticsearch configuration using [microcosm](https://github.com/globality-corp/microcosm) wiring.

[![Circle CI](https://circleci.com/gh/globality-corp/microcosm-elasticsearch/tree/develop.svg?style=svg)](https://circleci.com/gh/globality-corp/microcosm-elasticsearch/tree/develop)


## Usage

    from microcosm.api import create_object_graph

    graph = create_object_graph(name="foo")
    graph.use("elasticsearch_client")


## Convention

 - Support for signed requests for AWS Elasticsearch using AWS4Auth
 - Support for IAM Role-based credentials based on instance metadata when running on EC2
 - Proper unicode support for Python 2.x / 3.x codebases


## Configuration

When using with an AWS Elasticsearch instance, set proper AWS environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION), and use:

    config.elasticsearch_client.use_aws4auth = True

When configuring for running on an EC2 instance and use the instance's IAM role-provided AWS credentials:

    config.elasticsearch_client.use_aws4auth = True
    config.elasticsearch_client.use_aws_instance_metadata = True

For proper Unicode support on Python 2.x, use:

    config.elasticsearch_client.use_python2_serializer = True
