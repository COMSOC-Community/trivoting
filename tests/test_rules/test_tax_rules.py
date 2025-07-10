import random

from unittest import TestCase

from tests.random_instances import get_random_profile
from tests.test_rules.instances import example_1_KPPS
from trivoting.election.alternative import Alternative
from trivoting.election.trichotomous_ballot import TrichotomousBallot
from trivoting.election.trichotomous_profile import TrichotomousProfile
from trivoting.rules.selection import Selection
from trivoting.rules.tax_rules import tax_method_of_equal_shares

from trivoting.rules.tax_rules import tax_sequential_phragmen


class TestMES(TestCase):

    def test_tax_rules_on_random_instance(self):
        for _ in range(50):
            profile = get_random_profile(50, 100)
            print(f"Computing Tax MES on randomly generated instance: {profile}")
            max_size = random.randint(1, len(profile.alternatives))
            for rule in [tax_method_of_equal_shares, tax_sequential_phragmen]:
                res = rule(profile, max_size, resoluteness=True)
                self.assertLessEqual(len(res), max_size)

    def test_tax_rules_on_trivial_instances(self):
        for rule in [tax_method_of_equal_shares, tax_sequential_phragmen]:
            # Empty profile
            profile = TrichotomousProfile()
            self.assertEqual(rule(profile, 0), Selection())

            # Only disapproved
            alternatives = [Alternative(i) for i in range(10)]
            negative_ballots = [TrichotomousBallot(disapproved=alternatives[:6]) for _ in range(10)]
            profile = TrichotomousProfile(negative_ballots, alternatives=alternatives)
            res = rule(profile, len(alternatives))
            self.assertEqual(len(res), 0)

            # Separated ballots
            positive_ballots = [TrichotomousBallot(approved=alternatives[6:]) for _ in range(100)]
            profile.extend(positive_ballots)
            res = rule(profile, len(alternatives))
            self.assertEqual(len(res), 4)
            for alt in alternatives[6:]:
                self.assertIn(alt, res)

    def test_mes_on_examples(self):
        profile = example_1_KPPS()
        max_size = profile.max_size_selection

        selection = tax_method_of_equal_shares(profile, max_size)
        categorised_selection = [[], [], []]
        for alt in selection.selected:
            if alt.name < 11:
                categorised_selection[0].append(alt)
            if 10 < alt.name < 21:
                categorised_selection[1].append(alt)
            else:
                categorised_selection[2].append(alt)
        self.assertEqual(len(categorised_selection[0]), 0)
        self.assertEqual(len(categorised_selection[1]), 3)
        self.assertEqual(len(categorised_selection[2]), 3)

    def test_phragmen_on_examples(self):
        profile = example_1_KPPS()
        max_size = profile.max_size_selection

        selection = tax_sequential_phragmen(profile, max_size)
        categorised_selection = [[], [], []]
        for alt in selection.selected:
            if alt.name < 11:
                categorised_selection[0].append(alt)
            if 10 < alt.name < 21:
                categorised_selection[1].append(alt)
            else:
                categorised_selection[2].append(alt)
        self.assertEqual(len(categorised_selection[0]), 0)
        self.assertEqual(len(categorised_selection[1]), 3)
        self.assertEqual(len(categorised_selection[2]), 3)
