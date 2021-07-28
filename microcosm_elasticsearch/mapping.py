from elasticsearch_dsl import Mapping

from microcosm_elasticsearch.models import Model


def create_mapping(*model_classes: Model) -> Mapping:
    mapping = Mapping()

    for model_class in model_classes:
        mapping.update(model_class._doc_type.mapping)

    return mapping
