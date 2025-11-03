import random

from unittest import TestCase

from tests.random_instances import get_random_profile
from trivoting.election.alternative import Alternative
from trivoting.election.trichotomous_ballot import TrichotomousBallot
from trivoting.election.trichotomous_profile import TrichotomousProfile
from trivoting.rules.thiele import (
    sequential_thiele,
    PAVScoreKraiczy2025,
    PAVScoreTalmonPaige2021,
    PAVScoreHervouin2025,
)
from trivoting.election.selection import Selection


class TestSequentialPAV(TestCase):

    def test_seq_pav_on_random_instance(self):
        for _ in range(20):
            for score in [
                PAVScoreKraiczy2025,
                PAVScoreTalmonPaige2021,
                PAVScoreHervouin2025,
            ]:
                profile = get_random_profile(20, 50)
                max_size = random.randint(1, len(profile.alternatives))
                res = sequential_thiele(profile, max_size, score, resoluteness=True)
                self.assertLessEqual(len(res), max_size, f"Failure with Sequential PAV[{score.__name__}] on: {profile}, k={max_size}")

    def test_seq_pav_on_trivial_instances(self):
        for score in [
            PAVScoreKraiczy2025,
            PAVScoreTalmonPaige2021,
            PAVScoreHervouin2025,
        ]:
            print(
                f"Computing Sequential PAV with {score.__name__} on trivial instances"
            )
            # Empty profile
            profile = TrichotomousProfile()
            self.assertEqual(sequential_thiele(profile, 0, score), Selection())

            # Only disapproved
            alternatives = [Alternative(str(i)) for i in range(10)]
            negative_ballots = [
                TrichotomousBallot(disapproved=alternatives[:6]) for _ in range(10)
            ]
            profile = TrichotomousProfile(negative_ballots, alternatives=alternatives)
            res = sequential_thiele(profile, len(alternatives), score)
            self.assertEqual(len(res), 0)

            # Separated ballots
            positive_ballots = [
                TrichotomousBallot(approved=alternatives[6:]) for _ in range(100)
            ]
            profile.extend(positive_ballots)
            res = sequential_thiele(profile, len(alternatives), score)
            self.assertEqual(len(res), 4)
            for alt in alternatives[6:]:
                self.assertIn(alt, res)
