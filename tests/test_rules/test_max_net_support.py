import random
from unittest import TestCase

from tests.random_instances import get_random_profile
from trivoting.election import TrichotomousProfile, Selection, Alternative, TrichotomousBallot
from trivoting.rules import max_net_support
from trivoting.rules.chamberlin_courant import chamberlin_courant, chamberlin_courant_brute_force
from trivoting.rules.max_net_support import max_net_support_ilp


class TestMaxNetSupport(TestCase):

    def test_max_net_support_on_random_instance(self):
        for _ in range(50):
            profile = get_random_profile(20, 50)
            max_size = random.randint(1, len(profile.alternatives))
            res = max_net_support(profile, max_size, resoluteness=True)
            self.assertLessEqual(len(res), max_size, f"Failure with max_net_support on: {profile}, k={max_size}")

    def test_max_net_support_on_trivial_instances(self):
        # Empty profile
        profile = TrichotomousProfile()
        self.assertEqual(max_net_support(profile, 0), Selection())

        # Only disapproved
        alternatives = [Alternative(str(i)) for i in range(10)]
        negative_ballots = [
            TrichotomousBallot(disapproved=alternatives[:6]) for _ in range(10)
        ]
        profile = TrichotomousProfile(negative_ballots, alternatives=alternatives)
        res = max_net_support(profile, len(alternatives))
        self.assertEqual(len(res), 0)

    def test_max_net_support_with_ilp(self):
        for _ in range(50):
            for m in range(2, 7):
                profile = get_random_profile(m, 50)
                max_size = random.randint(1, len(profile.alternatives))
                res1 = max_net_support(profile, max_size, resoluteness=True)
                support1 = profile.num_covered_ballots(res1)
                res2 = max_net_support_ilp(profile, max_size, resoluteness=True)
                support2 = profile.num_covered_ballots(res1)
                self.assertEqual(support1, support2, f"Failure max_net_support comparing to brute-force: {profile}, k={max_size}, ilp={res1} (s={support1}), ordering={res2} (s={support2})")