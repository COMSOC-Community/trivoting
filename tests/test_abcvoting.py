import os
from unittest import TestCase

from trivoting.election.abcvoting import parse_abcvoting_yaml
from trivoting.election.alternative import Alternative


class TestABCVoting(TestCase):
    def test_abcvoting(self):
        current_file_path = os.path.dirname(os.path.realpath(__file__))
        yaml_dir_path = os.path.join(
            current_file_path, "test_rules", "abcvoting_test_instances"
        )
        for yaml_file in os.listdir(yaml_dir_path)[:50]:
            yaml_file_path = os.path.join(yaml_dir_path, yaml_file)
            profile = parse_abcvoting_yaml(yaml_file_path)
            for ballot in profile:
                self.assertEqual(len(ballot.disapproved), 0)
            for alt in profile.alternatives:
                self.assertEqual(type(alt), Alternative)

        yaml_file_path = os.path.join(yaml_dir_path, "instanceL0000.abc.yaml")
        profile = parse_abcvoting_yaml(yaml_file_path)
        self.assertEqual(profile.num_ballots(), 8)
