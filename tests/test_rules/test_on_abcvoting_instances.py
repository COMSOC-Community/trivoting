import os
from multiprocessing import Pool

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

def process_yaml_file(yaml_file_path: str):
    profile = parse_abcvoting_yaml(yaml_file_path)

    print(f"Testing on {os.path.basename(yaml_file_path)}: {len(profile.alternatives)} alternatives and {profile.num_ballots()} voters")

    expected_result = read_abcvoting_expected_result(yaml_file_path, profile)

    for rule_id, rule in RULE_MAPPING.items():
        potential_results_repr = expected_result[rule_id]
        try:
            selection = rule(profile, profile.max_size_selection, resoluteness=True)
            selection_repr = resolute_res_representation(selection.selected, profile)
            assert selection_repr in potential_results_repr
        except NotImplementedError:
            pass

        try:
            selections = rule(profile, profile.max_size_selection, resoluteness=False)
            selections_repr = irresolute_res_representation([s.selected for s in selections], profile)
            assert selections_repr == potential_results_repr
        except NotImplementedError:
            pass

    return True

class TestOnABCVoting(TestCase):
    def test_rules_on_abcvoting(self):
        current_file_path = os.path.dirname(os.path.realpath(__file__))
        yaml_dir_path = os.path.join(current_file_path, "abcvoting_test_instances")
        all_yaml_files = os.listdir(yaml_dir_path)
        yaml_paths = [os.path.join(yaml_dir_path, f) for f in all_yaml_files]

        with Pool() as pool:
            for res in pool.imap_unordered(process_yaml_file, yaml_paths):
                self.assertTrue(res)
