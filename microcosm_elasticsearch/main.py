"""
CLI entry point hook.

"""
from argparse import ArgumentParser
from json import loads


def createall_main(graph):
    """
    Initialize indexes and mappings.

    """
    parser = ArgumentParser()
    parser.add_argument("--only", action="append")
    parser.add_argument("--skip", action="append")
    parser.add_argument("-D", "--drop", action="store_true")
    args = parser.parse_args()

    graph.elasticsearch_index_registry.createall(
        force=args.drop,
        only=args.only,
        skip=args.skip,
    )


def query_main(graph, default_index):
    """
    Run a query.

    """
    parser = ArgumentParser()
    parser.add_argument("-i", "--index", default=default_index)
    parser.add_argument("-q", "--query", default='{"match_all": {}}')
    parser.add_argument("-f", "--flat", action="store_true")
    args = parser.parse_args()

    try:
        query = loads(args.query)
    except Exception:
        parser.error("query must be valid json")

    response = graph.elasticsearch_client.search(
        index=args.index,
        body=dict(query=query),
    )

    if args.flat:
        return response["hits"]["hits"]
    else:
        return response
