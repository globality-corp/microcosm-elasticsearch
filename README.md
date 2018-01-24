# microcosm-elasticsearch

Elasticsearch configuration using [microcosm](https://github.com/globality-corp/microcosm) wiring.

[![Circle CI](https://circleci.com/gh/globality-corp/microcosm-elasticsearch/tree/develop.svg?style=svg)](https://circleci.com/gh/globality-corp/microcosm-elasticsearch/tree/develop)


## Usage

 - Provides a `microcosm` compatible `Elasticsearch` client
    -  Supports signed requests for AWS Elasticsearch using AWS4Auth
    -  Supports IAM Role-based credentials based on instance metadata when running on EC2
    -  Provides proper unicode support for Python 2.x / 3.x codebases

 - Includes an implementation of a persistence `Store` using Elasticsarch

### Basic usage

See `fixtures.py` for a minimal example of how to define an index, some models, a store and search index. 

### Polymorphic models

Starting with version 6 ElasticSearch is deprecating the usage of mapping types - see [here](https://www.elastic.co/guide/en/elasticsearch/reference/master/removal-of-types.html).
One way to still have polymorphic indices is for the user to define a mapping field meant to hold the doctype. `microcosm-elasticsearch` supports this by default by adding a `doctype` field to every `Model`. The field value defaults to the lowercased model class name.

For example if I have a model:
```
from elasticsearch_dsl.field import Text
from microcosm_elasticsearch import Model

class Person(Model):
    first = Text()
    last = Text()
```

If I create a `Person`:
```
    person_store.create(Person(first="William", last="The Conqueror"))
```
then the record in ElasticSearch will look like
```
{
    "first": "William",
    "last": "The Conqueror",
    "doctype": "person"
}

```

To override those defaults, one can override the model's `__doctype_field__` and `__doctype_name__` to change the field name, and its value for that model, respectively. If we change the previous `Person` model in that way:

```
class Person(Model):
    __doctype_field__ = "the_doctype_field" 
    __doctype_name__ = "the_person"

    first = Text()
    last = Text()
```
Then creating a `Person` in the exact same way as before, its record in ElasticSearch will look like:
```
{
    "first": "William",
    "last": "The Conqueror",
    "the_doctype_field": "the_person"
}
```

Note that the model's `__doctype_field__` attribute needs to match the corresponding `SearchIndex`'s `doc_type_field` property.

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
