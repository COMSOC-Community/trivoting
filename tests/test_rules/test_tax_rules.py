import random

from unittest import TestCase

from tests.random_instances import get_random_profile
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
