from __future__ import annotations

from abc import ABC, abstractmethod
from collections import Counter
from collections.abc import Iterable

from trivoting.election.alternative import Alternative
from trivoting.election.trichotomours_ballot import TrichotomousBallot
from trivoting.fractions import Numeric

class AbstractTrichotomousProfile(ABC, Iterable[TrichotomousBallot]):
    """
    Abstract class representing a profile, that is, a collection of ballots. This class is only meant to be inherited.
    """

    @abstractmethod
    def multiplicity(self, ballot: TrichotomousBallot) -> int:
        """
        Method returning the multiplicity of a ballot. Used to ensure that profiles and multiprofiles can be used
        interchangeably.

        Parameters
        ----------
            ballot :TrichotomousBallot
                The ballot whose multiplicity is inquired.

        Returns
        -------
            int
                The multiplicity of the ballots.
        """


class TrichotomousProfile(list, AbstractTrichotomousProfile):
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

    def approval_score(self, alternative: Alternative, symmetric: bool = True) -> Numeric:
        """ Returns the approval score of an alternative. By default, the approval score is symmetric, i.e., approving
        of an alternative increases its score by one and disapproving of an alternative decreases its score by 1.

        Parameters
        ----------
            alternative : Alternative
                The alternative to consider.
            symmetric : bool
               If `True` the score is symmetric, otherwise it is non-symmetric.

        """
        score = 0
        for ballot in self:
            if alternative in ballot.approved:
                score += 1
            elif alternative in ballot.disapproved and symmetric:
                score -= 1
        return score

    def multiplicity(self, ballot: TrichotomousBallot) -> int:
        """
        Returns 1 regardless of the input (even if the ballot does not appear in the profile, to save up computation).

        Parameters
        ----------
            ballot : TrichotomousBallot
                The ballot whose multiplicity is inquired.

        Returns
        -------
            int
                1
        """
        return 1

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


class TrichotomousMultiProfile(Counter, AbstractTrichotomousProfile):
    """
    Represents a trichotomous multi-profile, i.e., a collection of trichotomous ballots in which identical ballots
    are stored one together with their multiplicity.
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

    def approval_score(self, alternative: Alternative, symmetric: bool = True) -> Numeric:
        """ Returns the approval score of an alternative. By default, the approval score is symmetric, i.e., approving
        of an alternative increases its score by one and disapproving of an alternative decreases its score by 1.

        Parameters
        ----------
            alternative : Alternative
                The alternative to consider.
            symmetric : bool
               If `True` the score is symmetric, otherwise it is non-symmetric.

        """
        score = 0
        for ballot in self:
            if alternative in ballot.approved:
                score += 1
            elif alternative in ballot.disapproved and symmetric:
                score -= 1
        return score

    def multiplicity(self, ballot: TrichotomousBallot) -> int:
        """
        Returns the multiplicity of a ballot in the profile.

        Parameters
        ----------
            ballot : TrichotomousBallot
                The ballot whose multiplicity is inquired.

        Returns
        -------
            int
                The multiplicity of the ballot.
        """
        return self[ballot]

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