from __future__ import annotations

from collections.abc import Collection, Callable

import pabutools.election as pb_election
import pabutools.rules as pb_rules

from trivoting.election.alternative import Alternative
from trivoting.election.trichotomours_profile import AbstractTrichotomousProfile
from trivoting.fractions import frac
from trivoting.tiebreaking import TieBreakingRule


def tax_pb_instance(
        profile: AbstractTrichotomousProfile,
        max_size_selection: int,
        force_selected: Collection[Alternative],
        force_not_selected: Collection[Alternative],
):
    """
    Returns a Participatory Budgeting instance and profile based on the given trichotomous profile.
    """
    app_scores, disapp_scores = profile.approval_disapproval_score_dict()

    alt_to_project = dict()
    project_to_alt = dict()
    running_alternatives = set()
    pb_instance = pb_election.Instance(budget_limit=max_size_selection)
    for alt, app_score in app_scores.items():
        support = app_score - disapp_scores[alt]
        if support > 0 and alt not in force_selected and alt not in force_not_selected:
            project = pb_election.Project(alt.name, cost=frac(app_score, support))
            pb_instance.add(project)
            running_alternatives.add(alt)
            alt_to_project[alt] = project
            project_to_alt[project] = alt

    pb_profile = pb_election.ApprovalMultiProfile(instance=pb_instance)
    for ballot in profile:
        pb_profile.append(
            pb_election.FrozenApprovalBallot(alt_to_project[alt] for alt in ballot.approved if alt in running_alternatives)
        )
    return pb_instance, pb_profile, project_to_alt

def tax_pb_rule_scheme(
    profile: AbstractTrichotomousProfile,
    max_size_selection: int,
    pb_rule: Callable,
    force_selected: Collection[Alternative] | None = None,
    force_not_selected: Collection[Alternative] | None = None,
    tie_breaking: TieBreakingRule | None = None,
    resoluteness: bool = True,
):
    if force_selected is None:
        force_selected = list()
    else:
        force_selected = list(force_selected)
    if force_not_selected is None:
        force_not_selected = list()
    else:
        force_not_selected = list(force_not_selected)

    if profile.num_ballots() == 0:
        return force_selected if resoluteness else [force_selected]

    pb_instance, pb_profile, project_to_alt = tax_pb_instance(profile, max_size_selection, force_selected, force_not_selected)

    budget_allocation = pb_rule(
        pb_instance,
        pb_profile,
        tie_breaking=tie_breaking,
        resoluteness=resoluteness
    )

    if resoluteness:
        return [project_to_alt[p] for p in budget_allocation]
    else:
        return [[project_to_alt[p] for p in a] for a in budget_allocation]

def tax_method_of_equal_shares(
    profile: AbstractTrichotomousProfile,
    max_size_selection: int,
    force_selected: Collection[Alternative] | None = None,
    force_not_selected: Collection[Alternative] | None = None,
    tie_breaking: TieBreakingRule | None = None,
    resoluteness: bool = True,
) -> list[Alternative] | list[list[Alternative]]:
    """
    Tax method of equal shares.


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

    def pb_mes(instance, profile, tie_breaking=None, resoluteness=True):
        return pb_rules.method_of_equal_shares(
            instance,
            profile,
            sat_class=pb_election.Cardinality_Sat,
            tie_breaking=tie_breaking,
            resoluteness=resoluteness,
        )

    return tax_pb_rule_scheme(
        profile,
        max_size_selection,
        pb_mes,
        force_selected=force_selected,
        force_not_selected=force_not_selected,
        tie_breaking=tie_breaking,
        resoluteness=resoluteness,
    )

def tax_sequential_phragmen(
    profile: AbstractTrichotomousProfile,
    max_size_selection: int,
    force_selected: Collection[Alternative] | None = None,
    force_not_selected: Collection[Alternative] | None = None,
    tie_breaking: TieBreakingRule | None = None,
    resoluteness: bool = True,
) -> list[Alternative] | list[list[Alternative]]:
    """
    Tax sequential Phragmén.


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

    return tax_pb_rule_scheme(
        profile,
        max_size_selection,
        pb_rules.sequential_phragmen,
        force_selected=force_selected,
        force_not_selected=force_not_selected,
        tie_breaking=tie_breaking,
        resoluteness=resoluteness,
    )

