"""Wrapper for a Starcraft Count reference.

"""


class SCCount:
    def __init__(self, value: str):
        self.value = value

    def __repr__(self):
        return self.value


ALL = 'All'
