import unittest

from tests.random_instances import get_random_profile
from trivoting.tiebreaking import lexico_tie_breaking, app_score_tie_breaking, support_tie_breaking, \
    TieBreakingException, refuse_tie_breaking


class TestTieBreaking(unittest.TestCase):

    def test_tie_breaking(self):
        profile = get_random_profile(50, 50)
        alts = list(profile.alternatives)[:20]

        lexico_tie_breaking.order(profile, alts)
        lexico_tie_breaking.untie(profile, alts)

        support_tie_breaking.order(profile, alts)
        support_tie_breaking.untie(profile, alts)

        app_score_tie_breaking.order(profile, alts)
        app_score_tie_breaking.untie(profile, alts)

        with self.assertRaises(TieBreakingException):
            refuse_tie_breaking.order(profile, alts)
        with self.assertRaises(TieBreakingException):
            refuse_tie_breaking.untie(profile, alts)