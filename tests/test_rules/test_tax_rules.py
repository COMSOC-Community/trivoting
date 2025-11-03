import random
from functools import partial

from unittest import TestCase

from tests.random_instances import get_random_profile
from trivoting.election.alternative import Alternative
from trivoting.election.trichotomous_ballot import TrichotomousBallot
from trivoting.election.trichotomous_profile import TrichotomousProfile
from trivoting.election.selection import Selection
from trivoting.fractions import frac
from trivoting.rules.tax_rules import tax_method_of_equal_shares, DisapprovalLinearTax

from trivoting.rules.tax_rules import tax_sequential_phragmen


def tax_rules(max_size_selection):
    rules = [tax_method_of_equal_shares, tax_sequential_phragmen]
    linear_taxes = [
        DisapprovalLinearTax.initialize(frac(1, x))
        for x in range(1, max_size_selection + 1)
    ]
    for tax in linear_taxes:
        rules.append(partial(tax_method_of_equal_shares, tax_function=tax))
        rules.append(partial(tax_sequential_phragmen, tax_function=tax))
    return rules


class TestMES(TestCase):

    def test_tax_rules_on_random_instance(self):
        for _ in range(50):
            profile = get_random_profile(20, 50)
            max_size = random.randint(1, len(profile.alternatives))
            for rule in tax_rules(max_size):
                res = rule(profile, max_size, resoluteness=True)
                self.assertLessEqual(len(res), max_size, f"Failure with Tax MES on: {profile}, k={max_size}")

    def test_tax_rules_on_trivial_instances(self):
        for rule in tax_rules(0):
            for resolute in (True, False):
                # Empty profile
                profile = TrichotomousProfile()
                self.assertEqual(
                    rule(profile, 0, resoluteness=resolute),
                    Selection() if resolute else [Selection()],
                )

        for rule in tax_rules(10):
            for resolute in (True, False):
                # Only disapproved
                alternatives = [Alternative(str(i)) for i in range(10)]
                negative_ballots = [
                    TrichotomousBallot(disapproved=alternatives[:6]) for _ in range(10)
                ]
                profile = TrichotomousProfile(
                    negative_ballots, alternatives=alternatives
                )
                res = rule(profile, len(alternatives), resoluteness=resolute)
                if resolute:
                    res = [res]
                for r in res:
                    self.assertEqual(len(r), 0)

                # Separated ballots
                positive_ballots = [
                    TrichotomousBallot(approved=alternatives[6:]) for _ in range(100)
                ]
                profile.extend(positive_ballots)
                res = rule(profile, len(alternatives), resoluteness=resolute)
                if resolute:
                    res = [res]
                for r in res:
                    self.assertEqual(len(r), 4)
                    for alt in alternatives[6:]:
                        self.assertIn(alt, r)
