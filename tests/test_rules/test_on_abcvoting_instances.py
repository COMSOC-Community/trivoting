import os

import yaml

from unittest import TestCase

from trivoting.election.abcvoting import parse_abcvoting_yaml
from trivoting.rules.pav import proportional_approval_voting
from trivoting.rules.phragmen import sequential_phragmen


def read_abcvoting_expected_result(file_path, profile):
    with open(file_path) as f:
        data = yaml.safe_load(f)

    expected_results = dict()

    # Alternative that have support
    supported_alternatives = set()
    for alt in profile.alternatives:
        if profile.support(alt) > 0:
            supported_alternatives.add(int(alt.name))

    for entry in data["compute"]:
        if entry["rule_id"] in RULE_MAPPING and entry["resolute"] is False:
            potential_results = entry["result"]

            potential_results_representation = []
            for res in potential_results:
                res_representation = [a for a in res if a in supported_alternatives]
                res_representation.sort()
                if res_representation not in potential_results_representation:
                    potential_results_representation.append(res_representation)
            potential_results_representation.sort()

            expected_results[entry["rule_id"]] = potential_results_representation
    return expected_results

def resolute_res_representation(budget_allocation, profile):
    # Alternative that have support
    supported_alternatives = set()
    for alt in profile.alternatives:
        if profile.support(alt) > 0:
            supported_alternatives.add(alt)
    return sorted([int(a.name) for a in budget_allocation if a in supported_alternatives])

def irresolute_res_representation(budget_allocations, profile):
    res = []
    for alloc in budget_allocations:
        alloc_repr = resolute_res_representation(alloc, profile)
        if alloc_repr not in res:
            res.append(alloc_repr)
    return sorted(res)

RULE_MAPPING = {
    "seqphragmen": sequential_phragmen,
    "pav": proportional_approval_voting,
}

class TestOnABCVoting(TestCase):
    def test_rules_on_abcvoting(self):
        current_file_path = os.path.dirname(os.path.realpath(__file__))
        yaml_dir_path = os.path.join(current_file_path, "abcvoting_test_instances")
        all_yaml_files = os.listdir(yaml_dir_path)
        for yaml_file_index, yaml_file in enumerate(all_yaml_files):
            yaml_file_path = os.path.join(yaml_dir_path, yaml_file)

            profile = parse_abcvoting_yaml(yaml_file_path)

            print(f"{yaml_file_index + 1}/{len(all_yaml_files)} Testing on {yaml_file}: {len(profile.alternatives)} alternatives and {profile.num_ballots()} voters")

            expected_result = read_abcvoting_expected_result(yaml_file_path, profile)

            for rule_id, rule in RULE_MAPPING.items():
                print(f"\t{rule_id}")
                potential_results_repr = expected_result[rule_id]
                try:
                    selection = rule(profile, profile.max_size_selection, resoluteness=True)
                    selection_repr = resolute_res_representation(selection, profile)
                    self.assertIn(selection_repr, potential_results_repr)
                except NotImplementedError:
                    pass

                try:
                    selections = rule(profile, profile.max_size_selection, resoluteness=False)
                    selections_repr = irresolute_res_representation(selections, profile)
                    self.assertEqual(selections_repr, potential_results_repr)
                except NotImplementedError:
                    pass
