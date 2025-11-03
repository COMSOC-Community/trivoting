from __future__ import annotations

from pulp import (
    lpSum,
    LpBinary,
    LpVariable,
    LpInteger,
    LpAffineExpression,
)

from trivoting.election import AbstractTrichotomousProfile, Selection
from trivoting.rules.ilp_schemes import ILPBuilder, ilp_optimiser_rule
from trivoting.utils import generate_subsets


def chamberlin_courant_brute_force(
    profile: AbstractTrichotomousProfile,
    max_size_selection: int,
    initial_selection: Selection = None,
    resoluteness: bool = True
) -> Selection | list[Selection]:
    if initial_selection is None:
        initial_selection = Selection(implicit_reject=True)
    max_coverage = None
    arg_max_coverage = None
    for selection_selected in generate_subsets(profile.alternatives, max_size=max_size_selection - len(initial_selection)):
        selection = Selection(selected=list(selection_selected) + initial_selection.selected, implicit_reject=True)
        covered_voters = profile.num_covered_ballots(selection)
        if max_coverage is None or covered_voters > max_coverage:
            max_coverage = covered_voters
            arg_max_coverage = [selection]
        elif max_coverage == covered_voters:
            arg_max_coverage.append(selection)
    if arg_max_coverage is None:
        raise ValueError("In CC brute force no solution has been found, weird...")
    if resoluteness:
        return arg_max_coverage[0]
    return arg_max_coverage

class ChamberlinCourantILPBuilder(ILPBuilder):
    model_name = "ChamberlinCourant"

    def init_vars(self) -> None:
        super(ChamberlinCourantILPBuilder, self).init_vars()

        self.vars["sat_var"] = dict()
        self.vars["dissat_var"] = dict()
        self.vars["cc_var"] = dict()

        for i, ballot in enumerate(self.profile):
            sat_var = LpVariable(f"sat_{i}", lowBound=-self.max_size_selection, upBound=self.max_size_selection, cat=LpInteger)
            dissat_var = LpVariable(f"dissat_{i}", lowBound=-self.max_size_selection, upBound=self.max_size_selection, cat=LpInteger)
            cc_var = LpVariable(f"cc_{i}", cat=LpBinary)

            self.model += sat_var == lpSum(self.vars["selection"][alt] for alt in ballot.approved)
            self.model += dissat_var == lpSum(self.vars["selection"][alt] for alt in ballot.disapproved)

            # Linearisation of z = 1 if x > y and z = 0 otherwise
            self.model += (sat_var - dissat_var >= 1 - (1 - cc_var) * self.max_size_selection)
            self.model += (sat_var - dissat_var <= cc_var * self.max_size_selection)

            self.vars["sat_var"][i] = sat_var
            self.vars["dissat_var"][i] = dissat_var
            self.vars["cc_var"][i] = cc_var

    def objective(self) -> LpAffineExpression:
        return lpSum(self.vars["cc_var"].values())


def chamberlin_courant(
    profile: AbstractTrichotomousProfile,
    max_size_selection: int,
    initial_selection: Selection = None,
    resoluteness: bool = True,
    max_seconds: int = 600,
    verbose: bool = False,
) -> Selection | list[Selection]:
    """
    Compute the selections of the Chamberlin-Courant rule.

    The Chamberlin-Courant returns selections that maximise the number of covered voter. A voter is covered if
    strictly more approved alternatives are selected than disapproved ones.

    The outcome of the rule is computed via an Integer Linear Program (ILP).

    Parameters
    ----------
    profile : AbstractTrichotomousProfile
        The trichotomous profile.
    max_size_selection : int
        Maximum number of alternatives to select.
    initial_selection : Selection, optional
        An initial selection that fixes some alternatives as selected or rejected.
        If `implicit_reject` is True, no alternatives are fixed to be rejected.
    resoluteness : bool, optional
        If True, returns a single selection (resolute).
        If False, returns all tied optimal selections (irresolute).
        Defaults to True.
    max_seconds : int, optional
        Maximum number of seconds to run the ILP solver for.
        Defaults to 600 seconds (10 minutes).
    verbose : bool, optional
        If True the output of the ILP solver is not silenced.
        Defaults to False.

    Returns
    -------
    Selection | list[Selection]
        The selection if resolute (:code:`resoluteness == True`), or a list of selections
        if irresolute (:code:`resoluteness == False`).
    """
    ilp_builder = ChamberlinCourantILPBuilder(profile, max_size_selection, initial_selection, max_seconds=max_seconds, verbose=verbose)
    return ilp_optimiser_rule(ilp_builder, resoluteness=resoluteness)
