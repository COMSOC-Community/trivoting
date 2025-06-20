from unittest import TestCase

from trivoting.election.alternative import Alternative
from trivoting.election.trichotomous_ballot import TrichotomousBallot


class TestTriBallot(TestCase):
    def test_tri_ballot(self):
        alts = [Alternative(i) for i in range(20)]

        ballot = TrichotomousBallot(approved=alts[:5], disapproved=alts[5:10])

        for a in alts[:10]:
            self.assertIn(a, ballot)
        for a in alts[10:]:
            self.assertNotIn(a, ballot)

        self.assertEqual(len(ballot), 10)
        ballot.add_approved(alts[0])
        self.assertEqual(len(ballot), 10)
        ballot.add_disapproved(alts[6])
        self.assertEqual(len(ballot), 10)
        ballot.add_approved(alts[10])
        self.assertIn(alts[10], ballot)
        self.assertIn(alts[10], ballot.approved)
        self.assertEqual(len(ballot), 11)
        ballot.add_disapproved(alts[11])
        self.assertIn(alts[11], ballot)
        self.assertIn(alts[11], ballot.disapproved)
        self.assertEqual(len(ballot), 12)
