from unittest import TestCase

from trivoting.election.alternative import Alternative
from trivoting.election.trichotomous_ballot import TrichotomousBallot
from trivoting.election.trichotomous_profile import TrichotomousProfile
from trivoting.rules.tax_rules import tax_method_of_equal_shares, tax_sequential_phragmen


def example_1_KPPS25():
    """Example 1 of Proportionality in Thumbs Up and Down Voting"""

    alts = [Alternative(i) for i in range(1, 31)]

    profile = TrichotomousProfile(alternatives=alts)
    for i in range(4):
        profile.add_ballot(
            TrichotomousBallot(approved=alts[20:], disapproved=alts[:10] + alts[10 + 2 * i: 10 + 2 * i + 4])
        )

    profile.add_ballot(
        TrichotomousBallot(approved=alts[20:], disapproved=alts[:12] + alts[18:20])
    )

    for _ in range(6):
        profile.add_ballot(TrichotomousBallot(approved=alts[:20]))
    profile.add_ballot(
        TrichotomousBallot(
            approved=alts[:10], disapproved=alts[20:]
        )
    )

    profile.max_size_selection = 10

    return profile

class TestExamplesKPPS25(TestCase):

    def test_mes_tax(self):
        profile = example_1_KPPS25()
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

    def test_phragmen_tax(self):
        profile = example_1_KPPS25()
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

    def test_epjr(self):
        pass

    def test_group_veto(self):
        pass