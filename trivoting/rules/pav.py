from __future__ import annotations

import abc
from collections.abc import Iterable, Callable

from trivoting.election.trichotomous_profile import AbstractTrichotomousProfile

from pulp import LpProblem, LpMaximize, LpBinary, LpVariable, lpSum, LpStatusOptimal, value, PULP_CBC_CMD, \
    LpAffineExpression

from trivoting.election.selection import Selection


class PAVMipVoter:
    """
    Helper class representing a voter in the Proportional Approval Voting (PAV) ILP model.

    Parameters
    ----------
    ballot : FrozenTrichotomousBallot
        The ballot of the voter.
    multiplicity : int
        The number of identical ballots represented by this voter.
    x_vars : dict[int, LpVariable]
        Decision variables representing the voter's contribution to the PAV score
        for each possible approval count.

    Attributes
    ----------
    ballot : FrozenTrichotomousBallot
        The ballot of the voter.
    multiplicity : int
        The number of identical ballots represented by this voter.
    app_sat_vars : dict[int, LpVariable]
        Decision variables counting the number of approved alternative that have been selected. The higher, the better.
    disapp_sat_vars : dict[int, LpVariable]
        Decision variables counting the number of disapproved alternative that have not been selected. The higher, the better.
    app_dissat_vars : dict[int, LpVariable]
        Decision variables counting the number of approved alternative that have not been selected. The higher, the worst.
    disapp_dissat_vars : dict[int, LpVariable]
        Decision variables counting the number of disapproved alternative that have been selected. The higher, the worst.
    """
    def __init__(self, ballot, multiplicity):
        self.ballot = ballot
        self.multiplicity = multiplicity
        self.app_sat_vars = None
        self.disapp_sat_vars = None
        self.app_dissat_vars = None
        self.disapp_dissat_vars = None
        self.sat_vars = None
        self.dissat_vars = None

class PAVILPBuilder(abc.ABC):
    def __init__(self, profile: AbstractTrichotomousProfile, max_size_selection: int):
        self.profile = profile
        self.max_size_selection = max_size_selection
        self.model = LpProblem("pav", LpMaximize)
        self.voters = []
        self.selection_vars = {alt: LpVariable(f"y_{alt.name}", cat=LpBinary) for alt in profile.alternatives}

    @abc.abstractmethod
    def init_voters_vars(self) -> None:
        """"""

    @abc.abstractmethod
    def objective(self) -> LpAffineExpression:
        """"""

class PAVILPKraiczy2025(PAVILPBuilder):
    """
    Defines the ILP objective for the PAV ILP solver as defined in Section 3.3 of
    ``Proportionality in Thumbs Up and Down Voting`` (Kraiczy, Papasotiropoulos, Pierczyński and Skowron, 2025).
    The objective is to maximise the PAV score where both approved and selected, and disapproved and not selected
    alternatives contribute positively.
    """
    def init_voters_vars(self) -> None:
        # Init the variables
        for i, ballot in enumerate(self.profile):
            pav_voter = PAVMipVoter(ballot, multiplicity=self.profile.multiplicity(ballot))
            pav_voter.sat_vars = dict()
            for k in range(1, len(self.profile.alternatives) + 1):
                pav_voter.sat_vars[k] = LpVariable(f"s_{i}_{k}", cat=LpBinary)
            self.voters.append(pav_voter)

        # Constraint them to ensure proper counting
        for voter in self.voters:
            self.model += lpSum(voter.sat_vars.values()) == lpSum(
                self.selection_vars[alt] for alt in voter.ballot.approved) + lpSum(
                1 - self.selection_vars[alt] for alt in voter.ballot.disapproved)

    def objective(self) -> LpAffineExpression:
        return lpSum(lpSum(v / i for i, v in voter.sat_vars.items()) for voter in self.voters)


class PAVILPTalmonPage2021(PAVILPBuilder):
    """
    Defines the ILP objective for the PAV ILP solver as defined in Section 3.3 of
    ``Proportionality in Committee Selection with Negative Feelings`` (Talmon and Page, 2021).
    The objective is to maximise the difference between (1) the PAV score in which approved and selected alternatives
    are taken into account, and (2) the PAV score in which disapproved but selected alternatives are taken into account.
    """

    def init_voters_vars(self) -> None:
        # Init the variables
        for i, ballot in enumerate(self.profile):
            pav_voter = PAVMipVoter(ballot, multiplicity=self.profile.multiplicity(ballot))
            pav_voter.app_sat_vars = dict()
            pav_voter.disapp_dissat_vars = dict()
            for k in range(1, len(self.profile.alternatives) + 1):
                pav_voter.app_sat_vars[k] = LpVariable(f"as_{i}_{k}", cat=LpBinary)
                pav_voter.disapp_dissat_vars[k] = LpVariable(f"dd_{i}_{k}", cat=LpBinary)
            self.voters.append(pav_voter)

        # Constraint them to ensure proper counting
        for voter in self.voters:
            self.model += lpSum(voter.app_sat_vars.values()) == lpSum(self.selection_vars[alt] for alt in voter.ballot.approved)
            self.model += lpSum(voter.disapp_dissat_vars.values()) == lpSum(self.selection_vars[alt] for alt in voter.ballot.disapproved)

    def objective(self) -> LpAffineExpression:
        return lpSum(lpSum(v / i for i, v in voter.app_sat_vars.items()) for voter in self.voters) - lpSum(lpSum(v / i for i, v in voter.disapp_dissat_vars.items()) for voter in self.voters)


class PAVILPHervouin2025(PAVILPBuilder):
    """
    Defines the ILP objective for the PAV ILP solver as defined by Matthieu Hervouin.
    The objective is to maximise the sum of (1) the PAV score in which approved and selected alternatives
    are taken into account, and (2) the PAV score over the maximum size of the selection minus the number of
    disapproved but selected alternatives.
    """

    def init_voters_vars(self) -> None:
        # Init the variables
        for i, ballot in enumerate(self.profile):
            pav_voter = PAVMipVoter(ballot, multiplicity=self.profile.multiplicity(ballot))
            pav_voter.app_sat_vars = dict()
            pav_voter.disapp_dissat_vars = dict()
            for k in range(1, len(self.profile.alternatives) + 1):
                pav_voter.app_sat_vars[k] = LpVariable(f"as_{i}_{k}", cat=LpBinary)
                pav_voter.disapp_dissat_vars[k] = LpVariable(f"dd_{i}_{k}", cat=LpBinary)
            self.voters.append(pav_voter)

        # Constraint them to ensure proper counting
        for voter in self.voters:
            self.model += lpSum(voter.app_sat_vars.values()) == lpSum(self.selection_vars[alt] for alt in voter.ballot.approved)
            self.model += lpSum(voter.disapp_dissat_vars.values()) == self.max_size_selection - lpSum(self.selection_vars[alt] for alt in voter.ballot.disapproved)

    def objective(self) -> LpAffineExpression:
        return lpSum(lpSum(v / i for i, v in voter.app_sat_vars.items()) for voter in self.voters) + lpSum(lpSum(v / i for i, v in voter.disapp_dissat_vars.items()) for voter in self.voters)

def proportional_approval_voting(
    profile: AbstractTrichotomousProfile,
    max_size_selection: int,
    ilp_builder_class: type[PAVILPBuilder] = None,
    initial_selection: Selection | None = None,
    resoluteness: bool = True,
    verbose: bool = False,
    max_seconds: int = 600
) -> Selection | list[Selection]:
    """
    Compute the selections of the Proportional Approval Voting (PAV) rule via Integer Linear Programming (ILP).
    The ILP is solved with the `pulp` package.

    Different objective functions can be used.

    Parameters
    ----------
    profile : AbstractTrichotomousProfile
        The trichotomous profile.
    max_size_selection : int
        Maximum number of alternatives to select.
    ilp_builder_class : type[PAVILPBuilder], optional
        Builder class for the ILP. Defautls to :py:class:`PAVILPKraiczy2025`.
    initial_selection : Selection, optional
        An initial partial selection fixing some alternatives as selected or rejected.
        If `implicit_reject` is True in the initial selection, no alternatives are fixed to be rejected.
        Defaults to None.
    resoluteness : bool, optional
        If True, returns a single optimal selection (resolute).
        If False, returns all tied optimal selections (irresolute).
        Defaults to True.
    verbose : bool, optional
        If True, enables ILP solver output.
        Defaults to False.
    max_seconds : int, optional
        Time limit in seconds for the ILP solver.
        Defaults to 600.

    Returns
    -------
    Selection | list[Selection]
        The selection if resolute (:code:`resoluteness == True`), or a list of selections
        if irresolute (:code:`resoluteness == False`).
    """

    if ilp_builder_class is None:
        ilp_builder_class = PAVILPKraiczy2025

    ilp_builder = ilp_builder_class(profile, max_size_selection)

    model = ilp_builder.model
    ilp_builder.init_voters_vars()
    selection_vars = ilp_builder.selection_vars

    # Select no more than allowed
    model += lpSum(selection_vars.values()) <= max_size_selection

    # Handle initial selection
    if initial_selection is not None:
        for alt in initial_selection.selected:
            model += selection_vars[alt] == 1
        if not initial_selection.implicit_reject:
            for alt in initial_selection.rejected:
                model += selection_vars[alt] == 0

    # Objective: max PAV score
    model += ilp_builder.objective()

    status = model.solve(PULP_CBC_CMD(msg=verbose, timeLimit=max_seconds))

    all_selections = []

    if status == LpStatusOptimal:
        selection = Selection(implicit_reject=True)
        for alt, v in selection_vars.items():
            if value(v) >= 0.9:
                selection.add_selected(alt)
        all_selections.append(selection)
    else:
        raise ValueError(f"Solver did not find an optimal solution, status is {status}.")

    if resoluteness:
        return all_selections[0]

    # If irresolute, we solve again, banning the previous selections
    model += ilp_builder.objective() == value(model.objective)

    previous_selection = selection
    while True:
        # See http://yetanothermathprogrammingconsultant.blogspot.com/2011/10/integer-cuts.html
        model += (
                             lpSum((1 - selection_vars[a]) for a in previous_selection.selected) +
                             lpSum(selection_vars[a] for a in selection_vars if a not in previous_selection)
                     ) >= 1

        model += (
                             lpSum(selection_vars[a] for a in previous_selection.selected) -
                             lpSum(selection_vars[a] for a in selection_vars if a not in previous_selection)
                     ) <= len(previous_selection) - 1

        status = model.solve(PULP_CBC_CMD(msg=verbose, timeLimit=max_seconds))

        if status != LpStatusOptimal:
            break

        previous_selection = Selection([a for a in selection_vars if value(selection_vars[a]) is not None and value(selection_vars[a]) >= 0.9], implicit_reject=True)
        if previous_selection not in all_selections:
            all_selections.append(previous_selection)

    return all_selections
