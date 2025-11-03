from __future__ import annotations

from pulp import lpSum, LpVariable, LpInteger, LpAffineExpression

from trivoting.election import AbstractTrichotomousProfile, Selection
from trivoting.rules.ilp_schemes import ILPBuilder, ilp_optimiser_rule


class MaxNetSupportILPBuilder(ILPBuilder):
    model_name = "MaxNetSupport"

    def init_vars(self) -> None:
        super(MaxNetSupportILPBuilder, self).init_vars()

        self.vars["sat_var"] = dict()

        for i, ballot in enumerate(self.profile):
            sat_var = LpVariable(f"sat_{i}", lowBound=-self.max_size_selection, upBound=self.max_size_selection, cat=LpInteger)
            self.model += sat_var == lpSum(self.vars["selection"][alt] for alt in ballot.approved) - lpSum(self.vars["selection"][alt] for alt in ballot.disapproved)
            self.vars["sat_var"][i] = sat_var

    def objective(self) -> LpAffineExpression:
        return lpSum(self.vars["sat_var"][i] * self.profile.multiplicity(b) for i, b in enumerate(self.profile))


def max_net_support_ilp(
    profile: AbstractTrichotomousProfile,
    max_size_selection: int,
    initial_selection: Selection = None,
    resoluteness: bool = True,
    max_seconds: int = 600,
    verbose: bool = False,
) -> Selection | list[Selection]:
    """
    Compute the selections maximising the total net support of the voters.

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
    ilp_builder = MaxNetSupportILPBuilder(profile, max_size_selection, initial_selection, max_seconds=max_seconds, verbose=verbose)
    return ilp_optimiser_rule(ilp_builder, resoluteness=resoluteness)



def max_net_support(
    profile: AbstractTrichotomousProfile,
    max_size_selection: int,
    initial_selection: Selection = None,
    resoluteness: bool = True
) -> Selection | list[Selection]:
    if not resoluteness:
        raise NotImplementedError("Max Net Support does not yet support resoluteness=False.")
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
