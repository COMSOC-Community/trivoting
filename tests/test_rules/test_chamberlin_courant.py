import random
from unittest import TestCase

from tests.random_instances import get_random_profile
from trivoting.election import TrichotomousProfile, Selection, Alternative, TrichotomousBallot
from trivoting.rules.chamberlin_courant import chamberlin_courant, chamberlin_courant_brute_force


class TestChamberlinCourant(TestCase):

    def test_cc_on_random_instance(self):
        for _ in range(50):
            profile = get_random_profile(20, 50)
            max_size = random.randint(1, len(profile.alternatives))
            res = chamberlin_courant(profile, max_size, resoluteness=True)
            self.assertLessEqual(len(res), max_size, f"Failure with CC on: {profile}, k={max_size}")

    def test_cc_on_trivial_instances(self):
        # Empty profile
        profile = TrichotomousProfile()
        self.assertEqual(chamberlin_courant(profile, 0), Selection())

        # Only disapproved
        alternatives = [Alternative(i) for i in range(10)]
        negative_ballots = [
            TrichotomousBallot(disapproved=alternatives[:6]) for _ in range(10)
        ]
        profile = TrichotomousProfile(negative_ballots, alternatives=alternatives)
        res = chamberlin_courant(profile, len(alternatives))
        self.assertEqual(len(res), 0)

    def test_cc_on_specific_instances(self):
        a = Alternative("a")
        b = Alternative("b")
        c = Alternative("c")
        d = Alternative("d")
        e = Alternative("e")
        alternatives = [a, b, c, d, e]
        ballots = [
            TrichotomousBallot(approved=[a, b], disapproved=[c]),
            TrichotomousBallot(approved=[c]),
        ]
        profile = TrichotomousProfile(ballots, alternatives=alternatives)
        res = chamberlin_courant(profile, 3)
        self.assertEqual(len(res), 3)

        profile.add_ballot(TrichotomousBallot(approved=[a], disapproved=[c]))
        res = chamberlin_courant(profile, 2)
        self.assertIn(a, res)
        self.assertNotIn(c, res)

    def test_with_brute_force(self):
        for _ in range(50):
            for m in range(2, 7):
                profile = get_random_profile(m, 50)
                max_size = random.randint(1, len(profile.alternatives))
                res1 = chamberlin_courant(profile, max_size, resoluteness=True)
                res1_coverage = profile.num_covered_ballots(res1)
                res2 = chamberlin_courant_brute_force(profile, max_size, resoluteness=True)
                res2_coverage = profile.num_covered_ballots(res1)
                self.assertEqual(res1_coverage, res2_coverage, f"Failure CC comparing to brute-force: {profile}, k={max_size}, bf={res2} (c={res1_coverage}), ilp={res1} (c={res2_coverage})")