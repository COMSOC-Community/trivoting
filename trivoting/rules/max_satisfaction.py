from __future__ import annotations

from pulp import (
    LpMaximize,
    LpProblem,
    lpSum,
    LpStatusOptimal,
    value,
    LpBinary,
    LpVariable,
    LpInteger,
    HiGHS,
)

from trivoting.election import AbstractTrichotomousProfile, Selection


def max_satisfaction_ilp(
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

    Returns
    -------
    Selection | list[Selection]
        The selection if resolute (:code:`resoluteness == True`), or a list of selections
        if irresolute (:code:`resoluteness == False`).
    """
    model = LpProblem("MaximumSatisfaction", LpMaximize)

    selection_vars = {
        alt: LpVariable(f"y_{alt.name}", cat=LpBinary) for alt in profile.alternatives
    }

    # Select no more than allowed
    model += lpSum(selection_vars.values()) <= max_size_selection

    # Handle initial selection
    if initial_selection is not None:
        for alt in initial_selection.selected:
            model += selection_vars[alt] == 1
        if not initial_selection.implicit_reject:
            for alt in initial_selection.rejected:
                model += selection_vars[alt] == 0

    # Voters satisfaction variables
    voter_details = []
    for i, ballot in enumerate(profile):
        voter = {
            "ballot": ballot,
            "multiplicity": profile.multiplicity(ballot),
            "sat_var": LpVariable(
                f"sat_{i}", lowBound=-max_size_selection, upBound=max_size_selection, cat=LpInteger
            ),
        }
        voter_details.append(voter)

    # Constraint voter_details to ensure proper counting
    for voter in voter_details:
        model += voter["sat_var"] == lpSum(
            selection_vars[alt] for alt in voter["ballot"].approved
        ) - lpSum(
            selection_vars[alt] for alt in voter["ballot"].disapproved
        )

    # Objective: max PAV score
    model += lpSum(voter["sat_var"] for voter in voter_details)

    status = model.solve(HiGHS(msg=verbose, timeLimit=max_seconds))

    all_selections = []

    if status == LpStatusOptimal:
        selection = Selection(implicit_reject=True)
        for alt, v in selection_vars.items():
            if value(v) >= 0.9:
                selection.add_selected(alt)
        all_selections.append(selection)
    else:
        raise ValueError(
            f"Solver did not find an optimal solution, status is {status}."
        )

    if resoluteness:
        return all_selections[0]

    # If irresolute, we solve again, banning the previous selections
    model += lpSum(voter["sat_var"] for voter in voter_details) == value(model.objective)

    previous_selection = selection
    while True:
        # See http://yetanothermathprogrammingconsultant.blogspot.com/2011/10/integer-cuts.html
        model += (
            lpSum((1 - selection_vars[a]) for a in previous_selection.selected)
            + lpSum(
                selection_vars[a] for a in selection_vars if a not in previous_selection
            )
        ) >= 1

        model += (
            lpSum(selection_vars[a] for a in previous_selection.selected)
            - lpSum(
                selection_vars[a] for a in selection_vars if a not in previous_selection
            )
        ) <= len(previous_selection) - 1

        status = model.solve(HiGHS(msg=verbose, timeLimit=max_seconds))

        if status != LpStatusOptimal:
            break

        previous_selection = Selection(
            [
                a
                for a in selection_vars
                if value(selection_vars[a]) is not None
                and value(selection_vars[a]) >= 0.9
            ],
            implicit_reject=True,
        )
        if previous_selection not in all_selections:
            all_selections.append(previous_selection)

    return all_selections


def max_satisfaction(
    profile: AbstractTrichotomousProfile,
    max_size_selection: int,
    initial_selection: Selection = None,
    resoluteness: bool = True,
    max_seconds: int = 600,
    verbose: bool = False,
) -> Selection | list[Selection]:
    if not resoluteness:
        raise NotImplementedError("Max Satisfaction does not yet support resoluteness=False.")
    alt_scores = profile.support_dict()
    if initial_selection is None:
        selection = Selection(implicit_reject=True)
    else:
        selection = initial_selection
    for alt, score in sorted(alt_scores.items(), key=lambda x: -x[1]):
        if len(selection) >= max_size_selection:
            break
        if score > 0:
            selection.add_selected(alt)
    return selection
