from pulp import LpMaximize, LpProblem, lpSum, PULP_CBC_CMD, LpStatusOptimal, value, LpBinary, LpVariable, LpInteger

from trivoting.election import AbstractTrichotomousProfile, Selection


def chamberlin_courant_ilp(profile: AbstractTrichotomousProfile, max_size_selection: int, initial_selection: Selection = None, resoluteness: bool=True, max_seconds: int = 600, verbose: bool = False) -> Selection | list[Selection]:
    model = LpProblem("ChamberlinCourant", LpMaximize)

    selection_vars = {alt: LpVariable(f"y_{alt.name}", cat=LpBinary) for alt in profile.alternatives}

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
            "sat_var": LpVariable(f"sat_{i}", lowBound=0, upBound=max_size_selection, cat=LpInteger),
            "dissat_var": LpVariable(f"disat_{i}", lowBound=0, upBound=max_size_selection, cat=LpInteger),
            "cc_var": LpVariable(f"cc_{i}", cat=LpBinary)
        }
        voter_details.append(voter)

    # Constraint voter_details to ensure proper counting
    for voter in voter_details:
        model += voter["sat_var"] == lpSum(selection_vars[alt] for alt in voter["ballot"].approved)
        model += voter["dissat_var"] == lpSum(selection_vars[alt] for alt in voter["ballot"].disapproved)

        # Linearisation of z = 1 if x > y and z = 0 otherwise
        model += voter["sat_var"] - voter["dissat_var"] >= 1 - (1 - voter["cc_var"]) * max_size_selection
        model += voter["sat_var"] - voter["dissat_var"] <= voter["cc_var"] * max_size_selection

    # Objective: max PAV score
    model += lpSum(voter["cc_var"] for voter in voter_details)

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
    model += lpSum(voter["cc_var"] for voter in voter_details) == value(model.objective)

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

        previous_selection = Selection(
            [a for a in selection_vars if value(selection_vars[a]) is not None and value(selection_vars[a]) >= 0.9],
            implicit_reject=True)
        if previous_selection not in all_selections:
            all_selections.append(previous_selection)

    return all_selections