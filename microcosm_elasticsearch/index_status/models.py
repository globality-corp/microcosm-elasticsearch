"""
Synthetic object containing information about an index.

"""


class IndexStatus:
    def __init__(
        self,
        name,
        aliases,
        mapping,
        stats,
    ):
        self.name = name
        self.aliases = aliases
        self.mapping = mapping
        self.stats = stats
