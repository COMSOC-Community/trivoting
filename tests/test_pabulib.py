import os
from unittest import TestCase

from trivoting.election.pabulib import parse_pabulib


class TestPabulib(TestCase):
    def test_pabulib_read(self):
        current_file_path = os.path.dirname(os.path.realpath(__file__))
        preflib_file_path = os.path.join(current_file_path, "data", "pabulib_approval.pb")

        profile = parse_pabulib(preflib_file_path)
        self.assertEqual(len(profile), 2066)
        for ballot in profile:
            self.assertEqual(ballot.disapproved, set())
            self.assertGreater(len(ballot.approved), 0)