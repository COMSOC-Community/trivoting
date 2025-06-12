from __future__ import annotations

from collections.abc import Iterable

from trivoting.election.alternative import Alternative
from trivoting.election.trichotomours_ballot import TrichotomousBallot


class TrichotomousProfile(list):
    """
    Represents a trichotomous profile, i.e., a collection of trichotomous ballots, one per voter.
    """

    def __init__(
        self,
        init: Iterable[TrichotomousBallot] = (),
        *,
        alternatives: Iterable[Alternative] = None,
    ) -> None:
        init = list(init)  # in case `init` is an iterable
        super().__init__(init)
        if alternatives is None:
            self.alternatives = set()
        else:
            self.alternatives = set(alternatives)

    def __add__(self, value):
        return TrichotomousProfile(
            list.__add__(self, value),
            alternatives=self.alternatives
        )

    def __mul__(self, value):
        return TrichotomousProfile(
            list.__mul__(self, value),
            alternatives=self.alternatives
        )
