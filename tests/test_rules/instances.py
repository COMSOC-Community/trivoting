from trivoting.election.alternative import Alternative
from trivoting.election.trichotomous_ballot import TrichotomousBallot
from trivoting.election.trichotomous_profile import TrichotomousProfile


def example_1_KPPS():
    """Example 1 of Proportionality in Thumbs Up and Down Voting"""

    alts = [Alternative(i) for i in range(1, 31)]

    profile = TrichotomousProfile(alternatives=alts)
    for i in range(4):
        profile.add_ballot(
            TrichotomousBallot(approved=alts[20:], disapproved=alts[:10] + alts[10 + 2 * i: 10 + 2 * i + 4])
        )

    profile.add_ballot(
        TrichotomousBallot(approved=alts[20:], disapproved=alts[:12] + alts[18:20])
    )

    for _ in range(6):
        profile.add_ballot(TrichotomousBallot(approved=alts[:20]))
    profile.add_ballot(
        TrichotomousBallot(
            approved=alts[:10], disapproved=alts[20:]
        )
    )

    profile.max_size_selection = 10

    return profile