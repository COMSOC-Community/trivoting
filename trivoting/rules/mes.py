from __future__ import annotations

from collections.abc import Collection

from pabutools.election import Instance, Project, ApprovalMultiProfile, FrozenApprovalBallot

from trivoting.election.alternative import Alternative
from trivoting.election.trichotomours_profile import AbstractTrichotomousProfile
from trivoting.fractions import frac
from trivoting.tiebreaking import TieBreakingRule


def tax_mes(
    profile: AbstractTrichotomousProfile,
    max_size_selection: int,
    force_selected: Collection[Alternative] | None = None,
    force_not_selected: Collection[Alternative] | None = None,
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
            force_selected : Iterable[Alternative], optional
                A set of alternatives initially selected.
            force_not_selected : Iterable[Alternative], optional
                A set of alternatives initially not selected.
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

    app_scores, disapp_scores = profile.approval_disapproval_score_dict()

    running_alternatives = set()
    pb_instance = Instance()
    for alt, app_score in app_scores.items():
        support = app_score - disapp_scores[alt]
        if support > 0:
            pb_instance.add(Project(alt.name, cost=frac(app_score, support)))
            running_alternatives.add(alt)

    pb_profile = ApprovalMultiProfile(instance=pb_instance)
    for ballot in profile:
        pb_profile.append(
            FrozenApprovalBallot(alt for alt in ballot.approved if alt in running_alternatives)
        )


