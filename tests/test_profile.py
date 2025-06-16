from unittest import TestCase

from trivoting.election.alternative import Alternative
from trivoting.election.trichotomours_ballot import TrichotomousBallot
from trivoting.election.trichotomours_profile import TrichotomousProfile


class TestProfile(TestCase):
    def test_profile(self):
        alternatives = [Alternative(i) for i in range(20)]
        ballots = [
            TrichotomousBallot(approved=alternatives[1:10], disapproved=alternatives[11:14]),
            TrichotomousBallot(approved=alternatives[15:18], disapproved=alternatives[0:5]),
            TrichotomousBallot(approved=alternatives[18:19], disapproved=alternatives[4:9]),
            TrichotomousBallot(),
        ]

        profile = TrichotomousProfile(ballots, alternatives=alternatives)

        self.assertEqual(profile.alternatives, set(alternatives))
        self.assertEqual(profile.num_ballots(), 4)
        self.assertEqual(profile.approval_score(alternatives[0]), -1)
        self.assertEqual(profile.approval_score(alternatives[1]), 0)
        self.assertEqual(profile.approval_score(alternatives[18]), 1)
        for a in alternatives:
            self.assertGreaterEqual(profile.approval_score(a, symmetric=False), 0)

        # Test general operations on profiles
        profile = profile.__add__(TrichotomousProfile([ballots[0], ballots[1]]))
        self.assertEqual(profile.num_ballots(), 6)
        profile *= 3
        self.assertEqual(profile.num_ballots(), 18)