import os
from unittest import TestCase

from trivoting.election.preflib import parse_preflib


class TestPreflib(TestCase):
    def test_preflib_read(self):
        current_file_path = os.path.dirname(os.path.realpath(__file__))
        preflib_file_path = os.path.join(
            current_file_path, "data", "preflib_cat_instance.cat"
        )

        profile = parse_preflib(preflib_file_path)
        self.assertEqual(profile.num_ballots(), 100)
