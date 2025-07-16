import random
from unittest import TestCase

from trivoting.axiomatic.justified_representation import is_positive_ejr, is_group_veto
from trivoting.election.alternative import Alternative
from trivoting.election.trichotomous_ballot import TrichotomousBallot
from trivoting.election.trichotomous_profile import TrichotomousProfile
from trivoting.election.selection import Selection
from trivoting.rules.tax_rules import tax_method_of_equal_shares, tax_sequential_phragmen


def example_1_KPPS25():
    """Example 1 of Proportionality in Thumbs Up and Down Voting"""

    alts = [Alternative(i) for i in range(1, 31)]

    profile = TrichotomousProfile(alternatives=alts)

    # V1
    for i in range(4):
        profile.add_ballot(
            TrichotomousBallot(approved=alts[20:], disapproved=alts[:10] + alts[10 + 2 * i: 10 + 2 * i + 4])
        )
    profile.add_ballot(
        TrichotomousBallot(approved=alts[20:], disapproved=alts[:12] + alts[18:20])
    )

    # V2
    for _ in range(6):
        profile.add_ballot(TrichotomousBallot(approved=alts[:20]))

    # V3
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
            elif alt.name < 21:
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
            elif alt.name < 21:
                categorised_selection[1].append(alt)
            else:
                categorised_selection[2].append(alt)
        self.assertEqual(len(categorised_selection[0]), 0)
        self.assertEqual(len(categorised_selection[1]), 3)
        self.assertEqual(len(categorised_selection[2]), 3)

    def test_epjr(self):
        profile = example_1_KPPS25()
        max_size = profile.max_size_selection

        def generate_positive_selection():
            res = Selection(implicit_reject=True)
            for a in random.sample(range(1, 21), 3):
                res.selected.append(profile.get_alternative_by_name(a))
            for a in random.sample(range(21, 31), 3):
                res.selected.append(profile.get_alternative_by_name(a))

            alts = [a for a in profile.alternatives if not res.is_selected(a)]
            random.shuffle(alts)
            num_selected = 6
            for alt in alts:
                if random.random() < 4 / len(profile.alternatives):
                    res.selected.append(alt)
                    num_selected += 1
                if num_selected == max_size:
                    break

            res.selected.sort()
            res.rejected.sort()
            return res

        for _ in range(50):
            selection =  generate_positive_selection()
            self.assertTrue(is_positive_ejr(profile, max_size, selection))

        def generate_negative_selection():
            res = Selection(implicit_reject=True)

            for alt_name in random.sample(range(1, 21), random.randint(0, 2)):
                res.selected.append(profile.get_alternative_by_name(alt_name))
            for alt_name in random.sample(range(21, 31), random.randint(0, 2)):
                res.selected.append(profile.get_alternative_by_name(alt_name))

            res.selected.sort()
            res.rejected.sort()
            return res

        for _ in range(50):
            selection = generate_negative_selection()
            self.assertFalse(is_positive_ejr(profile, max_size, selection))

    def test_group_veto(self):
        profile = example_1_KPPS25()
        max_size = profile.max_size_selection

        def generate_negative_selection():
            res = Selection(implicit_reject=True)

            for alt_name in random.sample(range(1, 11), 3):
                res.selected.append(profile.get_alternative_by_name(alt_name))

            alts = [a for a in profile.alternatives if not res.is_selected(a)]
            random.shuffle(alts)
            num_selected = 3
            for alt in alts:
                if random.random() < 7 / len(profile.alternatives):
                    res.selected.append(alt)
                    num_selected += 1
                if num_selected == max_size:
                    break

            res.selected.sort()
            res.rejected.sort()
            return res

        for _ in range(30):
            selection = generate_negative_selection()
            self.assertFalse(is_group_veto(profile, max_size, selection))
