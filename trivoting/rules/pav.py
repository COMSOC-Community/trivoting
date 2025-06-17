from __future__ import annotations

from collections.abc import Collection

from trivoting.election.alternative import Alternative
from trivoting.election.trichotomours_profile import AbstractTrichotomousProfile

from pulp import LpProblem, LpMaximize, LpBinary, LpVariable, lpSum, LpStatusOptimal, value, PULP_CBC_CMD


class PAVMipVoter:

    def __init__(self, ballot, multiplicity):
        self.ballot = ballot
        self.multiplicity = multiplicity
        self.x_vars = dict()


def proportional_approval_voting(
    profile: AbstractTrichotomousProfile,
    max_size_selection: int,
    force_selected: Collection[Alternative] | None = None,
    force_not_selected: Collection[Alternative] | None = None,
    resoluteness: bool = True,
    verbose: bool = False,
    max_seconds: int = 600
) -> list[Alternative] | list[list[Alternative]]:
    """
    Proportional Approval Voting via ILP solver.
    """

    mip_model = LpProblem("pav", LpMaximize)

    pav_voters = []
    for i, ballot in enumerate(profile):
        pav_voter = PAVMipVoter(ballot, multiplicity=profile.multiplicity(ballot))
        for k in range(1, len(profile.alternatives) + 1):
            pav_voter.x_vars[k] = LpVariable(f"x_{i}_{k}", cat=LpBinary)
        pav_voters.append(pav_voter)

    y_vars = {alt: LpVariable(f"y_{alt.name}", cat=LpBinary) for alt in profile.alternatives}

    # Select no more than allowed
    mip_model += lpSum(y_vars.values()) <= max_size_selection

    # Counts for the voters correspond to approved and selected + disapproved and not selected
    for voter in pav_voters:
        mip_model += lpSum(voter.x_vars.values()) == lpSum(y_vars[alt] for alt in voter.ballot.approved) + lpSum(1 - y_vars[alt] for alt in voter.ballot.disapproved)

    if force_selected is not None:
        for alt in force_selected:
            mip_model += y_vars[alt] == 1
    if force_not_selected is not None:
        for alt in force_not_selected:
            mip_model += y_vars[alt] == 0

    # Objective: max PAV score
    mip_model += lpSum(lpSum(v / i for i, v in voter.x_vars.items()) for voter in pav_voters)

    status = mip_model.solve(PULP_CBC_CMD(msg=verbose, timeLimit=max_seconds))

    all_selections = []

    if status == LpStatusOptimal:
        selection = []
        for alt, v in y_vars.items():
            if value(v) >= 0.9:
                selection.append(alt)
        all_selections.append(selection)
    else:
        raise ValueError("Solver did not find an optimal solution.")

    if resoluteness:
        return all_selections[0]

    # If irresolute, we solve again, banning the previous selections
    mip_model += lpSum(lpSum(v / i for i, v in voter.x_vars.items()) for voter in pav_voters) == value(mip_model.objective)

    previous_selection = selection
    while True:
        # See http://yetanothermathprogrammingconsultant.blogspot.com/2011/10/integer-cuts.html
        mip_model += (
                             lpSum((1 - y_vars[a]) for a in previous_selection) +
                             lpSum(y_vars[a] for a in y_vars if a not in previous_selection)
                     ) >= 1

        mip_model += (
                             lpSum(y_vars[a] for a in previous_selection) -
                             lpSum(y_vars[a] for a in y_vars if a not in previous_selection)
                     ) <= len(previous_selection) - 1

        status = mip_model.solve(PULP_CBC_CMD(msg=verbose, timeLimit=max_seconds))

        if status != LpStatusOptimal:
            break

        previous_selection = [a for a in y_vars if value(y_vars[a]) is not None and value(y_vars[a]) >= 0.9]
        if previous_selection not in all_selections:
            all_selections.append(previous_selection)

    return all_selections
