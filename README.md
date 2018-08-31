# microcosm-elasticsearch

Elasticsearch configuration using [microcosm](https://github.com/globality-corp/microcosm) wiring.


## Usage

 - Provides a `microcosm` compatible `Elasticsearch` client
    -  Support vanilla Elasticsearch 6.x
    -  Support standard credentials and signed requests for AWS Elasticsearch

 - Includes an implementation of a persistence `Store` using Elasticsarch

### Basic usage

See `fixtures.py` for a minimal example of how to define an index, some models, a store and search index.


### Polymorphic models

Starting with version 6 ElasticSearch [removed support for multiple mapping types per index](https://www.elastic.co/guide/en/elasticsearch/reference/master/removal-of-types.html).

For applications that need polymorphic types within the same index, `microcosm-elasticsearch` enables customization
of the `doctype` field and instantiation of an apropriate `Model` based on this field (which defaults to the lowercased
model class name.

For example, with this model defintion:

```
from elasticsearch_dsl.field import Text
from microcosm_elasticsearch import Model

class Person(Model):
    first = Text()
    last = Text()


person_store.create(Person(first="William", last="The Conqueror"))
```

The resulting record in ElasticSearch will look like:
```
{
    "first": "William",
    "last": "The Conqueror",
    "doctype": "person"
}
```

And querying `store.search()` will return an instance of `Person` (vs `Hit`) for this record.


## Testing

Unit tests depend on a running instance of Elasticsearch:

 1. Bring up the ES with `docker-compose`:

         docker-compose up -d

 2. Run tests:

         nosetests


## Configuration

When using vanilla Elasticsearch, set:

    config.elasticsearch_client.host = localhost
    config.elasticsearch_client.username = elastic
    config.elasticsearch_client.password = changeme


When using with an AWS Elasticsearch instance, set the usual `AWS_*` variables and use:

    config.elasticsearch_client.host = some-host-name
    config.elasticsearch_client.use_aws4auth = 'true'
