from __future__ import annotations

from collections.abc import Collection
from copy import deepcopy

from trivoting.election.alternative import Alternative
from trivoting.election.trichotomours_ballot import AbstractTrichotomousBallot
from trivoting.election.trichotomours_profile import AbstractTrichotomousProfile
from trivoting.fractions import Numeric, frac
from trivoting.tiebreaking import TieBreakingRule, lexico_tie_breaking


class PhragmenVoter:
    """
    Class used to summarise a voter during a run of the Phragmén's sequential rule.

    Parameters
    ----------
        ballot: AbstractTrichotomousBallot
            The ballot of the voter.
        load: Numeric
            The initial load of the voter.
        multiplicity: int
            The multiplicity of the ballot.

    Attributes
    ----------
        ballot: AbstractTrichotomousBallot
            The ballot of the voter.
        load: Numeric
            The initial load of the voter.
        multiplicity: int
            The multiplicity of the ballot.
    """

    def __init__(
        self, ballot: AbstractTrichotomousBallot, load: Numeric, multiplicity: int
    ):
        self.ballot = ballot
        self.load = load
        self.multiplicity = multiplicity

    def total_load(self):
        return self.multiplicity * self.load


def sequential_phragmen(
    profile: AbstractTrichotomousProfile,
    max_size_selection: int,
    initial_loads: list[Numeric] | None = None,
    initial_selection: Collection[Alternative] | None = None,
    tie_breaking: TieBreakingRule | None = None,
    resoluteness: bool = True,
) -> list[Alternative] | list[list[Alternative]]:
    """


    Parameters
    ----------
        profile : AbstractTrichotomousProfile
            The profile.
        max_size_selection : int
            The maximum number of alternatives that can be selected.
        initial_loads: list[Numeric], optional
            A list of initial load, one per ballot in `profile`. By defaults, the initial load is `0`.
        initial_selection : Iterable[Alternative], optional
            An initial budget allocation, typically empty.
        tie_breaking : TieBreakingRule, optional
            The tie-breaking rule used.
            Defaults to the lexicographic tie-breaking.
        resoluteness : bool, optional
            Set to `False` to obtain an irresolute outcome, where all tied budget allocations are returned.
            Defaults to True.

    Returns
    -------
        list[Alternative] | list[list[Alternative]]
            The selected alternatives if resolute (:code:`resoluteness == True`), or the set of selected alternatives
            if irresolute (:code:`resoluteness == False`).
    """

    def _sequential_phragmen_rec(alternatives, voters, selection):
        if len(alternatives) == 0:
            selection.sort()
            if selection not in all_selections:
                all_selections.append(selection)
        else:
            min_new_maxload = None
            arg_min_new_maxload = None
            for alt in alternatives:
                if approval_scores[alt] == 0:
                    new_maxload = float("inf")
                else:
                    new_maxload = frac(
                        sum(voters[i].total_load() for i in supporters[alt])
                        + alt.cost,
                        approval_scores[alt],
                    )
                if min_new_maxload is None or new_maxload < min_new_maxload:
                    min_new_maxload = new_maxload
                    arg_min_new_maxload = [alt]
                elif min_new_maxload == new_maxload:
                    arg_min_new_maxload.append(alt)

            tied_alternatives = tie_breaking.order(profile, arg_min_new_maxload)
            if resoluteness:
                selected_alternative = tied_alternatives[0]
                for voter in voters:
                    if selected_alternative in voter.ballot.approved:
                        voter.load = min_new_maxload
                selection.append(selected_alternative)
                alternatives.remove(selected_alternative)
                _sequential_phragmen_rec(alternatives, voters, selection)
            else:
                for selected_alternative in tied_alternatives:
                    new_voters = deepcopy(voters)
                    for voter in new_voters:
                        if selected_alternative in voter.ballot.approved:
                            voter.load = min_new_maxload
                    new_selection = deepcopy(selection) + [selected_alternative]
                    new_alternatives = deepcopy(alternatives)
                    new_alternatives.remove(selected_alternative)
                    _sequential_phragmen_rec(new_alternatives, new_voters, new_selection)

    if tie_breaking is None:
        tie_breaking = lexico_tie_breaking
    if initial_selection is None:
        initial_selection = list()
    else:
        initial_selection = list(initial_selection)

    max_size_selection -= len(initial_selection)

    initial_alternatives = set(a for a in profile.alternatives if a not in initial_selection)

    if initial_loads is None:
        initial_voters = [PhragmenVoter(b, 0, profile.multiplicity(b)) for b in profile]
    else:
        initial_voters = [
            PhragmenVoter(b, initial_loads[i], profile.multiplicity(b))
            for i, b in enumerate(profile)
        ]

    # Stores indices of the voters details list
    supporters = {
        alt: [i for i, v in enumerate(initial_voters) if alt in v.ballot.approved]
        for alt in initial_alternatives
    }
    opposants = {
        alt: [i for i, v in enumerate(initial_voters) if alt in v.ballot.disapproved]
        for alt in initial_alternatives
    }

    approval_scores = {alt: profile.approval_score(alt) for alt in initial_alternatives}

    all_selections : list[list[Alternative]] = []

    _sequential_phragmen_rec(initial_alternatives, initial_voters, initial_selection)

    if resoluteness:
        return all_selections[0]
    return all_selections

