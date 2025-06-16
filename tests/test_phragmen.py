import os
import random

import yaml

from unittest import TestCase

from prefsampling.approval import urn, resampling, noise

from trivoting.election.abcvoting import parse_abcvoting_yaml
from trivoting.election.alternative import Alternative
from trivoting.election.generate import generate_random_profile
from trivoting.election.trichotomours_ballot import TrichotomousBallot
from trivoting.election.trichotomours_profile import TrichotomousProfile
from trivoting.rules.phragmen import sequential_phragmen


class TestPhragmen(TestCase):

    def test_phragmen_on_abc_instances(self):
        current_file_path = os.path.dirname(os.path.realpath(__file__))
        yaml_dir_path = os.path.join(current_file_path, "abcvoting_test_instances")
        for yaml_file in os.listdir(yaml_dir_path):
            yaml_file_path = os.path.join(yaml_dir_path, yaml_file)

            print(f"Computing Sequential Phragmen for {yaml_file}.")

            # Parse the profile
            profile = parse_abcvoting_yaml(yaml_file_path)
            if profile.max_size_selection is not None:
                # Read the expected result
                with open(yaml_file_path) as f:
                    data = yaml.safe_load(f)
                potential_results = None
                for entry in data["compute"]:
                    if entry["rule_id"] == "seqphragmen" and entry["resolute"] is False:
                        potential_results = entry["result"]
                        break
                potential_results_representation = None
                if potential_results:
                    non_void_alternatives = []
                    for alt in profile.alternatives:
                        if profile.approval_score(alt) > 0:  # This is safe because there are only approvals
                            non_void_alternatives.append(int(alt.name))
                    potential_results_representation = []
                    for res in potential_results:
                        res_representation = [a for a in res if a in non_void_alternatives]
                        res_representation.sort()
                        if res_representation not in potential_results_representation:
                            potential_results_representation.append(res_representation)
                    potential_results_representation.sort()

                for profile in [profile, profile.as_multiprofile()]:
                    # Compute the resolute rule
                    trivoting_res = sequential_phragmen(profile, profile.max_size_selection, resoluteness=True)
                    self.assertEqual(type(trivoting_res), list)
                    for alt in trivoting_res:
                        self.assertEqual(type(alt), Alternative)

                    if potential_results:
                        trivoting_res_representation = sorted([int(a.name) for a in trivoting_res])
                        self.assertIn(trivoting_res_representation, potential_results_representation)

                    # Compute the irresolute rule
                    trivoting_res = sequential_phragmen(profile, profile.max_size_selection, resoluteness=False)
                    self.assertEqual(type(trivoting_res), list)
                    for selection in trivoting_res:
                        self.assertEqual(type(selection), list)
                        for alt in selection:
                            self.assertEqual(type(alt), Alternative)

                    if potential_results:
                        trivoting_res_representation = sorted([[int(a.name) for a in res] for res in trivoting_res])
                        self.assertEqual(trivoting_res_representation, potential_results_representation)

        with self.assertRaises(TypeError):
            sequential_phragmen(None, None)

    def test_phragmen_on_random_instance(self):
        for _ in range(50):
            profile = generate_random_profile(
                100,
                100,
                lambda num_voters, num_candidates: urn(num_voters, num_candidates, p=0.5, alpha=0.7),
                lambda num_voters, num_candidates: resampling(num_voters, num_candidates, phi=0.5,
                                                              rel_size_central_vote=0.7),
                lambda num_voters, num_candidates: noise(num_voters, num_candidates, phi=0.5,
                                                         rel_size_central_vote=0.7),
            )
            print(f"Computing Phragmén on randomly generated instance: {profile}")
            max_size = random.randint(1, len(profile.alternatives))
            res = sequential_phragmen(profile, max_size, resoluteness=True)
            self.assertLessEqual(len(res), max_size)

    def test_phragmen_on_trivial_instances(self):
        # Empty profile
        profile = TrichotomousProfile()
        self.assertEqual(sequential_phragmen(profile, 0), [])

        # Only disapproved
        alternatives = [Alternative(i) for i in range(10)]
        negative_ballots = [TrichotomousBallot(disapproved=alternatives[:6]) for _ in range(10)]
        profile = TrichotomousProfile(negative_ballots, alternatives=alternatives)
        res = sequential_phragmen(profile, len(alternatives))
        self.assertEqual(len(res), 0)

        # Separated ballots
        positive_ballots = [TrichotomousBallot(approved=alternatives[6:]) for _ in range(100)]
        profile.extend(positive_ballots)
        res = sequential_phragmen(profile, len(alternatives))
        self.assertEqual(len(res), 4)
        for alt in alternatives[6:]:
            self.assertIn(alt, res)
