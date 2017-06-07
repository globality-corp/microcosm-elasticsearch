"""
CLI entry point hook.

"""
from argparse import ArgumentParser


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
