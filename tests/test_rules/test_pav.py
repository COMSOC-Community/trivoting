import random

from unittest import TestCase

from tests.random_instances import get_random_profile
from trivoting.election.alternative import Alternative
from trivoting.election.trichotomous_ballot import TrichotomousBallot
from trivoting.election.trichotomous_profile import TrichotomousProfile
from trivoting.rules.pav import proportional_approval_voting, PAVILPHervouin2025, PAVILPTalmonPage2021, PAVILPKraiczy2025
from trivoting.election.selection import Selection


class TestPAV(TestCase):

    def test_pav_on_random_instance(self):
        for _ in range(20):
            for builder in [PAVILPKraiczy2025, PAVILPTalmonPage2021, PAVILPHervouin2025]:
                profile = get_random_profile(50, 100)
                print(f"Computing PAV with {builder.__name__} on randomly generated instance: {profile}")
                max_size = random.randint(1, len(profile.alternatives))
                res = proportional_approval_voting(profile, max_size, ilp_builder_class=builder, resoluteness=True)
                self.assertLessEqual(len(res), max_size)

    def test_pav_on_trivial_instances(self):
        for builder in [PAVILPKraiczy2025, PAVILPTalmonPage2021, PAVILPHervouin2025]:
            # Empty profile
            profile = TrichotomousProfile()
            self.assertEqual(proportional_approval_voting(profile, 0, ilp_builder_class=builder), Selection())

            # Only disapproved
            alternatives = [Alternative(i) for i in range(10)]
            negative_ballots = [TrichotomousBallot(disapproved=alternatives[:6]) for _ in range(10)]
            profile = TrichotomousProfile(negative_ballots, alternatives=alternatives)
            res = proportional_approval_voting(profile, len(alternatives), ilp_builder_class=builder)
            self.assertEqual(len(res), 0)

            # Separated ballots
            positive_ballots = [TrichotomousBallot(approved=alternatives[6:]) for _ in range(100)]
            profile.extend(positive_ballots)
            res = proportional_approval_voting(profile, len(alternatives), ilp_builder_class=builder)
            self.assertEqual(len(res), 4)
            for alt in alternatives[6:]:
                self.assertIn(alt, res)
