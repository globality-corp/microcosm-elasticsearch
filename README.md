# microcosm-elasticsearch

Elasticsearch configuration using [microcosm](https://github.com/globality-corp/microcosm) wiring.

[![Circle CI](https://circleci.com/gh/globality-corp/microcosm-elasticsearch/tree/develop.svg?style=svg)](https://circleci.com/gh/globality-corp/microcosm-elasticsearch/tree/develop)


## Usage

    from microcosm.api import create_object_graph

    graph = create_object_graph(name="foo")
    graph.use("elasticsearch_client")

    # create an index
    graph.elasticsearch_client.indices.create(
        index="my-index",
        body=dict(
            settings=dict(
                "number_of_shards": 1,
                "number_of_replicas": 0,
            )
        )
    )

    # bulk index documents
    from elasticsearch.helpers import streaming_bulk
    docs_generator = some_generator_expression_yielding_dicts
    for ok, result in streaming_bulk(
        graph.elasticsearch_client,
        docs_generator,
        index="my-index",
        doc_type="my-doc-type",
        chunk_size=100,
        refresh=True,
        ):
        if not ok:
            raise RuntimeError("Bulk indexing failed for batch!")


## Convention

 - Support for signed requests for AWS Elasticsearch using AWS4Auth
 - Support for IAM Role-based credentials based on instance metadata when running on EC2
 - Proper unicode support for Python 2.x / 3.x codebases


## Configuration

When using with an AWS Elasticsearch instance, use:

    config.elasticsearch_client.use_aws4auth = True
    config.elasticsearch_client.aws_access_key_id = 'aws-access-key-id'  # Will try to read from AWS_ACCESS_KEY_ID env var. by default
    config.elasticsearch_client.aws_secret_access_key = 'aws-secret-access-key'  # Will try to read from AWS_SECRET_ACCESS_KEY env var. by default
    config.elasticsearch_client.aws_region = 'aws-region'  # Will try to read from AWS_REGION env var. by default

When configuring for running on an EC2 instance and use the instance's IAM role-provided AWS credentials:

    config.elasticsearch_client.use_aws4auth = True
    config.elasticsearch_client.use_aws_instance_metadata = True

For proper Unicode support on Python 2.x, use:

    config.elasticsearch_client.use_python2_serializer = True
