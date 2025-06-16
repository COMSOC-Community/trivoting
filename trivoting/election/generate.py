from collections.abc import Callable

from preflibtools.properties import num_voters

from trivoting.election.alternative import Alternative
from trivoting.election.trichotomours_ballot import TrichotomousBallot
from trivoting.election.trichotomours_profile import TrichotomousProfile


def generate_random_ballot(
        alternatives: list[Alternative],
        approve_disapproved_sampler: Callable,
        approved_sampler: Callable,
        disapproved_sampler: Callable
) -> TrichotomousBallot:
    ballot = TrichotomousBallot()
    approve_disapproved = approve_disapproved_sampler(num_voters=1, num_candidates=len(alternatives))[0]
    potentially_approved = []
    potentially_disapproved = []
    for i, a in enumerate(alternatives):
        if i in approve_disapproved:
            potentially_approved.append(a)
        else:
            potentially_disapproved.append(a)
    approved_indices = approved_sampler(num_voters=1, num_candidates=len(potentially_approved))[0]
    ballot.approved = [alternatives[i] for i in approved_indices]
    disaspproved_indices = disapproved_sampler(num_voters=1, num_candidates=len(potentially_disapproved))[0]
    disaspproved_indices = [i for i in disaspproved_indices if i not in approved_indices]
    ballot.disapproved = [alternatives[i] for i in disaspproved_indices]
    return ballot

def generate_random_profile(
        num_alternatives: int,
        num_voters: int,
        approve_disapproved_sampler: Callable,
        approved_sampler: Callable,
        disapproved_sampler: Callable
) -> TrichotomousProfile:
    alternatives = [Alternative(i) for i in range(num_alternatives)]
    profile = TrichotomousProfile(alternatives=alternatives)
    for _ in range(num_voters):
        ballot = generate_random_ballot(
            alternatives,
            approve_disapproved_sampler,
            approved_sampler,
            disapproved_sampler
        )
        profile.add_ballot(ballot)
    return profile
