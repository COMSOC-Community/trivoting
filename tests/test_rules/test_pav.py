import random

from unittest import TestCase

from prefsampling.approval import urn, resampling, noise

from trivoting.election.alternative import Alternative
from trivoting.election.generate import generate_random_profile
from trivoting.election.trichotomours_ballot import TrichotomousBallot
from trivoting.election.trichotomours_profile import TrichotomousProfile
from trivoting.rules.pav import proportional_approval_voting
from trivoting.rules.phragmen import sequential_phragmen


class TestPAV(TestCase):

    def test_pav_on_random_instance(self):
        for _ in range(20):
            profile = generate_random_profile(
                100,
                100,
                lambda num_voters, num_candidates: urn(num_voters, num_candidates, p=0.5, alpha=0.7),
                lambda num_voters, num_candidates: resampling(num_voters, num_candidates, phi=0.5,
                                                              rel_size_central_vote=0.7),
                lambda num_voters, num_candidates: noise(num_voters, num_candidates, phi=0.5,
                                                         rel_size_central_vote=0.7),
            )
            print(f"Computing PAV on randomly generated instance: {profile}")
            max_size = random.randint(1, len(profile.alternatives))
            res = proportional_approval_voting(profile, max_size, resoluteness=True)
            self.assertLessEqual(len(res), max_size)

    def test_pav_on_trivial_instances(self):
        # Empty profile
        profile = TrichotomousProfile()
        self.assertEqual(proportional_approval_voting(profile, 0), [])

        # Only disapproved
        alternatives = [Alternative(i) for i in range(10)]
        negative_ballots = [TrichotomousBallot(disapproved=alternatives[:6]) for _ in range(10)]
        profile = TrichotomousProfile(negative_ballots, alternatives=alternatives)
        res = proportional_approval_voting(profile, len(alternatives))
        self.assertEqual(len(res), 0)

        # Separated ballots
        positive_ballots = [TrichotomousBallot(approved=alternatives[6:]) for _ in range(100)]
        profile.extend(positive_ballots)
        res = proportional_approval_voting(profile, len(alternatives))
        self.assertEqual(len(res), 4)
        for alt in alternatives[6:]:
            self.assertIn(alt, res)
