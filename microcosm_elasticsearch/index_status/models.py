"""
Synthetic object containing information about an index.

"""


class IndexStatus:
    def __init__(
        self,
        name,
        data,
        stats,
    ):
        self.name = name
        self.data = data
        self.stats = stats
