import random
from unittest import TestCase

from tests.random_instances import get_random_profile
from trivoting.axiomatic.justified_representation import is_cohesive_for_l, all_cohesive_groups, is_base_ejr, \
    is_base_pjr, is_base_ejr_brute_force
from trivoting.election.alternative import Alternative
from trivoting.election.trichotomous_ballot import TrichotomousBallot
from trivoting.election.trichotomous_profile import TrichotomousProfile
from trivoting.rules.phragmen import sequential_phragmen
from trivoting.election.selection import Selection


class TestJustifiedRepresentation(TestCase):
    def test_cohesive_group_for_l(self):
        alternatives = [Alternative(k) for k in range(4)]
        profile = TrichotomousProfile(
            [
                TrichotomousBallot(approved=alternatives[0:]),
                TrichotomousBallot(approved=alternatives[1:]),
                TrichotomousBallot(approved=alternatives[1:]),
                TrichotomousBallot(approved=alternatives[1:]),
            ],
            alternatives=alternatives,
        )
        for sub_profile in profile.all_sub_profiles():
            is_cohesive_for_l(profile, 3, 1, sub_profile)

        list(all_cohesive_groups(profile, 3, min_l=0))

    def test_base_ejr(self):

        alternatives = [Alternative(k) for k in range(4)]
        profile = TrichotomousProfile(
            [
                TrichotomousBallot(approved=alternatives[0:]),
                TrichotomousBallot(approved=alternatives[1:]),
                TrichotomousBallot(approved=alternatives[1:]),
                TrichotomousBallot(approved=alternatives[1:]),
            ],
            alternatives=alternatives,
        )

        selection = sequential_phragmen(profile, 3)
        is_base_ejr_brute_force(profile, 3, selection)
        is_base_ejr(profile, 3, selection)

        max_size_selection = 3
        for _ in range(30):
            profile = get_random_profile(4, 10)
            selection = Selection(random.choices(profile.alternatives, k=3))
            self.assertEqual(is_base_ejr_brute_force(profile, max_size_selection, selection),
                             is_base_ejr(profile, max_size_selection, selection))

    def test_base_pjr(self):
        alternatives = [Alternative(k) for k in range(4)]
        profile = TrichotomousProfile(
            [
                TrichotomousBallot(approved=alternatives[0:]),
                TrichotomousBallot(approved=alternatives[1:]),
                TrichotomousBallot(approved=alternatives[1:]),
                TrichotomousBallot(approved=alternatives[1:]),
            ],
            alternatives=alternatives,
        )

        selection = sequential_phragmen(profile, 3)
        is_base_pjr(profile, 3, selection)

        max_size_selection = 3
        for _ in range(30):
            profile = get_random_profile(4, 15)
            selection = sequential_phragmen(profile, max_size_selection)
            self.assertTrue(is_base_pjr(profile, max_size_selection, selection))
