import random
from unittest import TestCase

from tests.random_instances import get_random_profile
from trivoting.election import TrichotomousProfile, Selection, Alternative, TrichotomousBallot
from trivoting.rules import max_net_support, thiele_method
from trivoting.rules.max_net_support import max_net_support_ilp
from trivoting.rules.thiele import NetSupportThieleScore


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

    def test_max_net_support_formulations(self):
        for _ in range(50):
            for m in range(2, 7):
                profile = get_random_profile(m, 50)
                max_size = random.randint(1, len(profile.alternatives))
                res1 = thiele_method(
                    profile, max_size, thiele_score_class=NetSupportThieleScore, resoluteness=True
                )
                self.assertLessEqual(len(res1), max_size, f"Failure with Max net support[Thiele] on: {profile}, k={max_size}")

                res2 = max_net_support_ilp(
                    profile, max_size, resoluteness=True
                )
                self.assertLessEqual(len(res2), max_size, f"Failure with Max net support[ILP] on: {profile}, k={max_size}")

                res3 = max_net_support(
                    profile, max_size, resoluteness=True
                )
                self.assertLessEqual(len(res3), max_size, f"Failure with Max net support[Direct] on: {profile}, k={max_size}")

                self.assertEqual(profile.selection_support(res1), profile.selection_support(res2), f"Failure with Max net support[Thiele] and Max net support[ILP] on: {profile}, k={max_size}: r1={res1}, r2={res2}")
                self.assertEqual(profile.selection_support(res1), profile.selection_support(res3), f"Failure with Max net support[Thiele] and Max net support[Direct] on: {profile}, k={max_size}: r1={res1}, r3={res3}")
