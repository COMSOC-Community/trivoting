import random

from unittest import TestCase

from tests.random_instances import get_random_profile
from trivoting.election.alternative import Alternative
from trivoting.election.trichotomous_ballot import TrichotomousBallot
from trivoting.election.trichotomous_profile import TrichotomousProfile
from trivoting.rules.thiele import (
    thiele_method,
    PAVScoreKraiczy2025,
    PAVScoreHervouin2025,
    PAVScoreTalmonPaige2021,
)
from trivoting.election.selection import Selection


class TestPAV(TestCase):

    def test_pav_on_random_instance(self):
        for _ in range(20):
            for thiele_score in [
                PAVScoreKraiczy2025,
                PAVScoreTalmonPaige2021,
                PAVScoreHervouin2025,
            ]:
                profile = get_random_profile(20, 50)
                max_size = random.randint(1, len(profile.alternatives))
                res = thiele_method(
                    profile, max_size, thiele_score_class=thiele_score, resoluteness=True
                )
                self.assertLessEqual(len(res), max_size, f"Failure with PAV[{thiele_score.__name__}] on: {profile}")

    def test_pav_on_trivial_instances(self):
        for thiele_score in [
                PAVScoreKraiczy2025,
                PAVScoreTalmonPaige2021,
                PAVScoreHervouin2025,]:
            # Empty profile
            profile = TrichotomousProfile()
            self.assertEqual(
                thiele_method(profile, 0, thiele_score_class=thiele_score), Selection(), f"Failure with {thiele_score.__name__}"
            )

            # Only disapproved
            alternatives = [Alternative(str(i)) for i in range(10)]
            negative_ballots = [
                TrichotomousBallot(disapproved=alternatives[:6]) for _ in range(10)
            ]
            profile = TrichotomousProfile(negative_ballots, alternatives=alternatives)
            res = thiele_method(profile, len(alternatives), thiele_score_class=thiele_score)
            self.assertEqual(len(res), 0, f"Failure with {thiele_score.__name__}")

            # Separated ballots
            positive_ballots = [
                TrichotomousBallot(approved=alternatives[6:]) for _ in range(100)
            ]
            profile.extend(positive_ballots)
            res = thiele_method(profile, len(alternatives), thiele_score_class=thiele_score)
            self.assertEqual(len(res), 4, f"Failure with {thiele_score.__name__}")
            for alt in alternatives[6:]:
                self.assertIn(alt, res, f"Failure with {thiele_score.__name__}")

