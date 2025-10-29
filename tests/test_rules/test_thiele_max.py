import random

from unittest import TestCase

from tests.random_instances import get_random_profile
from trivoting.election.alternative import Alternative
from trivoting.election.trichotomous_ballot import TrichotomousBallot
from trivoting.election.trichotomous_profile import TrichotomousProfile
from trivoting.rules import MaxSatisfactionILPBuilder
from trivoting.rules.max_satisfaction import max_satisfaction_ilp, max_satisfaction
from trivoting.rules.thiele import (
    thiele_method,
    PAVILPHervouin2025,
    PAVILPTalmonPage2021,
    PAVILPKraiczy2025,
)
from trivoting.election.selection import Selection


class TestPAV(TestCase):

    def test_pav_on_random_instance(self):
        for _ in range(20):
            for builder in [
                PAVILPKraiczy2025,
                PAVILPTalmonPage2021,
                PAVILPHervouin2025,
            ]:
                profile = get_random_profile(20, 50)
                max_size = random.randint(1, len(profile.alternatives))
                res = thiele_method(
                    profile, max_size, ilp_builder_class=builder, resoluteness=True
                )
                self.assertLessEqual(len(res), max_size, f"Failure with PAV[{builder.__name__}] on: {profile}")

    def test_pav_on_trivial_instances(self):
        for builder in [PAVILPKraiczy2025, PAVILPTalmonPage2021, PAVILPHervouin2025]:
            # Empty profile
            profile = TrichotomousProfile()
            self.assertEqual(
                thiele_method(profile, 0, ilp_builder_class=builder), Selection()
            )

            # Only disapproved
            alternatives = [Alternative(i) for i in range(10)]
            negative_ballots = [
                TrichotomousBallot(disapproved=alternatives[:6]) for _ in range(10)
            ]
            profile = TrichotomousProfile(negative_ballots, alternatives=alternatives)
            res = thiele_method(profile, len(alternatives), ilp_builder_class=builder)
            self.assertEqual(len(res), 0)

            # Separated ballots
            positive_ballots = [
                TrichotomousBallot(approved=alternatives[6:]) for _ in range(100)
            ]
            profile.extend(positive_ballots)
            res = thiele_method(profile, len(alternatives), ilp_builder_class=builder)
            self.assertEqual(len(res), 4)
            for alt in alternatives[6:]:
                self.assertIn(alt, res)

    def test_max_sat(self):
        for _ in range(50):
            profile = get_random_profile(30, 100)
            max_size = random.randint(1, len(profile.alternatives))
            res1 = thiele_method(
                profile, max_size, ilp_builder_class=MaxSatisfactionILPBuilder, resoluteness=True
            )
            self.assertLessEqual(len(res1), max_size, f"Failure with Max satisfaction[Thiele] on: {profile}, k={max_size}")

            res2 = max_satisfaction_ilp(
                profile, max_size, resoluteness=True
            )
            self.assertLessEqual(len(res2), max_size, f"Failure with Max satisfaction[ILP] on: {profile}, k={max_size}")

            res3 = max_satisfaction(
                profile, max_size, resoluteness=True
            )
            self.assertLessEqual(len(res3), max_size, f"Failure with Max satisfaction[Direct] on: {profile}, k={max_size}")

            self.assertEqual(profile.selection_support(res1), profile.selection_support(res2), f"Failure with Max satisfaction[Thiele] and Max satisfaction[ILP] on: {profile}, k={max_size}: r1={res1}, r2={res2}")
            self.assertEqual(profile.selection_support(res1), profile.selection_support(res3), f"Failure with Max satisfaction[Thiele] and Max satisfaction[Direct] on: {profile}, k={max_size}: r1={res1}, r3={res3}")
