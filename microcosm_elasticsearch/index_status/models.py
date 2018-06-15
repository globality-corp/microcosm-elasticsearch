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
        settings,
    ):
        self.name = name
        self.aliases = aliases
        self.mapping = mapping
        self.stats = stats
        self.settings = settings
