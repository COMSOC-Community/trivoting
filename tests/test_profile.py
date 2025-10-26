from unittest import TestCase

from tests.random_instances import get_random_profile
from trivoting.election.alternative import Alternative
from trivoting.election.trichotomous_ballot import TrichotomousBallot
from trivoting.election.trichotomous_profile import TrichotomousProfile


class TestProfile(TestCase):
    def test_profile(self):
        alternatives = [Alternative(i) for i in range(20)]
        ballots = [
            TrichotomousBallot(
                approved=alternatives[1:10], disapproved=alternatives[11:14]
            ),
            TrichotomousBallot(
                approved=alternatives[15:18], disapproved=alternatives[0:5]
            ),
            TrichotomousBallot(
                approved=alternatives[18:19], disapproved=alternatives[4:9]
            ),
            TrichotomousBallot(),
        ]

        profile = TrichotomousProfile(ballots, alternatives=alternatives)

        self.assertEqual(profile.alternatives, set(alternatives))
        self.assertEqual(profile.num_ballots(), 4)
        self.assertEqual(profile.support(alternatives[0]), -1)
        self.assertEqual(profile.support(alternatives[1]), 0)
        self.assertEqual(profile.support(alternatives[18]), 1)

        # Test general operations on profiles
        profile = profile.__add__(TrichotomousProfile([ballots[0], ballots[1]]))
        self.assertEqual(profile.num_ballots(), 6)
        profile *= 3
        self.assertEqual(profile.num_ballots(), 18)

    def test_scores(self):
        for _ in range(50):
            raw_profile = get_random_profile(5, 3)
            for profile in [raw_profile, raw_profile.as_multiprofile()]:
                for alt in profile.alternatives:
                    app_score = profile.approval_score(alt)
                    disapp_score = profile.disapproval_score(alt)
                    support = profile.support(alt)
                    self.assertGreaterEqual(app_score, 0)
                    self.assertGreaterEqual(disapp_score, 0)
                    self.assertEqual(support, app_score - disapp_score)
                    self.assertEqual(
                        profile.approval_disapproval_score(alt),
                        (app_score, disapp_score),
                    )
                self.assertEqual(
                    profile.approval_score_dict(),
                    {
                        alt: profile.approval_score(alt)
                        for alt in profile.alternatives
                        if profile.approval_score(alt) > 0
                    },
                )
                self.assertEqual(
                    profile.disapproval_score_dict(),
                    {
                        alt: profile.disapproval_score(alt)
                        for alt in profile.alternatives
                        if profile.disapproval_score(alt) > 0
                    },
                )
                self.assertEqual(
                    profile.support_dict(),
                    {
                        alt: profile.support(alt)
                        for alt in profile.alternatives
                        if sum(profile.approval_disapproval_score(alt)) > 0
                    },
                )
                reconstructed_app_disapp_dict = (
                    {
                        alt: profile.approval_score(alt)
                        for alt in profile.alternatives
                        if profile.approval_score(alt) > 0
                    },
                    {
                        alt: profile.disapproval_score(alt)
                        for alt in profile.alternatives
                        if profile.disapproval_score(alt) > 0
                    },
                )
                self.assertEqual(
                    profile.approval_disapproval_score_dict(),
                    reconstructed_app_disapp_dict,
                )
