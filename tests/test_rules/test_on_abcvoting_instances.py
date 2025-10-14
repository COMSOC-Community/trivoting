import os
from collections.abc import Iterable
from functools import partial
from multiprocessing import Pool

import yaml

from unittest import TestCase

from trivoting.election.abcvoting import parse_abcvoting_yaml
from trivoting.rules import tax_method_of_equal_shares, TaxKraiczy2025, DisapprovalLinearTax
from trivoting.rules.thiele import thiele_method, PAVILPKraiczy2025, PAVILPTalmonPage2021, PAVILPHervouin2025, \
    sequential_thiele, ApprovalOnlyScore, SatisfactionScore
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
    "pav": [
        partial(thiele_method, ilp_builder_class=PAVILPKraiczy2025),
        partial(thiele_method, ilp_builder_class=PAVILPTalmonPage2021),
        partial(thiele_method, ilp_builder_class=PAVILPHervouin2025),
    ],
    "av": [
        partial(sequential_thiele, thiele_score_class=ApprovalOnlyScore),
        partial(sequential_thiele, thiele_score_class=SatisfactionScore),
    ],
    # ABCvoting only has MES with completion...
    # "equal-shares": [
    #     partial(tax_method_of_equal_shares, tax_function=DisapprovalLinearTax.initialize(1)),
    #     partial(tax_method_of_equal_shares, tax_function=TaxKraiczy2025),
    # ]
}

def process_yaml_file(yaml_file_path: str):
    profile = parse_abcvoting_yaml(yaml_file_path)

    print(f"Testing on {os.path.basename(yaml_file_path)}: {len(profile.alternatives)} alternatives and {profile.num_ballots()} voters")

    expected_result = read_abcvoting_expected_result(yaml_file_path, profile)

    for rule_id, rules in RULE_MAPPING.items():
        if not isinstance(rules, Iterable):
            rules = [rules]
        for rule in rules:
            potential_results_repr = expected_result[rule_id]
            try:
                selection = rule(profile, profile.max_size_selection, resoluteness=True)
                selection_repr = resolute_res_representation(selection.selected, profile)
                print("R", selection_repr, potential_results_repr)
                assert selection_repr in potential_results_repr
            except NotImplementedError:
                pass

            try:
                selections = rule(profile, profile.max_size_selection, resoluteness=False)
                selections_repr = irresolute_res_representation([s.selected for s in selections], profile)
                print("IR", selections_repr, potential_results_repr)
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

        with Pool(processes=1) as pool:
            for res in pool.imap_unordered(process_yaml_file, yaml_paths):
                self.assertTrue(res)
