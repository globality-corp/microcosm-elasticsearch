"""
CLI entry point hook.

"""
from argparse import ArgumentParser
from json import dump, loads
from sys import stdout


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
    parser = ArgumentParser()
    parser.add_argument("--index", default=default_index)
    parser.add_argument("--query", default='{"match_all": {}}')
    args = parser.parse_args()

    try:
        query = loads(args.query)
    except:
        parser.error("query must be valid json")

    response = graph.elasticsearch_client.search(
        index=args.index,
        body=dict(query=query),
    )
    dump(response, stdout)
