from __future__ import annotations

from collections.abc import Iterable

from trivoting.election.alternative import Alternative


class TrichotomousBallot:
    """
    Represents a trichotomous ballot, i.e., a ballot in which the voter classifies the alternatives between approved,
    disapproved and not seen/no opinion.
    """

    def __init__(self, *, approved: Iterable[Alternative] = None, disapproved: Iterable[Alternative] = None):
        if approved is None:
            self.approved = set()
        else:
            self.approved = set(approved)

        if disapproved is None:
            self.disapproved = set()
        else:
            self.disapproved = set(disapproved)

    def add_approved(self, alt: Alternative):
        self.approved.add(alt)

    def add_disapproved(self, alt: Alternative):
        self.disapproved.add(alt)

    def __contains__(self, item):
        return item in self.approved or item in self.disapproved

    def __len__(self):
        return len(self.approved) + len(self.disapproved)

    def __str__(self):
        return f"[{self.approved} // {self.disapproved}]"

    def __repr__(self):
        return self.__str__()
