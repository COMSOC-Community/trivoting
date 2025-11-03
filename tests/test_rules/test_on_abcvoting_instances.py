import os
from collections.abc import Iterable
from functools import partial
from multiprocessing import Pool

import yaml

from unittest import TestCase

from trivoting.election import AbstractTrichotomousProfile
from trivoting.election.abcvoting import parse_abcvoting_yaml
from trivoting.rules import PAVScoreKraiczy2025, PAVScoreTalmonPaige2021, PAVScoreHervouin2025
from trivoting.rules.chamberlin_courant import chamberlin_courant
from trivoting.rules.max_net_support import max_net_support, max_net_support_ilp
from trivoting.rules.thiele import (
    thiele_method,
    sequential_thiele, ApprovalThieleScore, NetSupportThieleScore,
)
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
    return sorted(
        [int(a.name) for a in budget_allocation if a in supported_alternatives]
    )


def irresolute_res_representation(budget_allocations, profile):
    res = []
    for alloc in budget_allocations:
        alloc_repr = resolute_res_representation(alloc, profile)
        if alloc_repr not in res:
            res.append(alloc_repr)
    return sorted(res)


def exhaustivee_cc(
    profile: AbstractTrichotomousProfile, max_size_selection: int, resoluteness=True
):
    raw_res = chamberlin_courant(
        profile, max_size_selection, resoluteness=resoluteness
    )

    if resoluteness:
        res_list = [raw_res]
    else:
        res_list = raw_res
    new_res = []
    for res in res_list:
        if len(res.selected) < max_size_selection:
            for alt in profile.alternatives:
                if alt not in res.selected:
                    res.add_selected(alt)
                if len(res.selected) == max_size_selection:
                    new_res.append(res)
                    break
        else:
            new_res.append(res)
    if resoluteness:
        return new_res[0]
    return new_res


RULE_MAPPING = {
    "seqphragmen": sequential_phragmen,
    "pav": [
        partial(thiele_method, thiele_score_class=PAVScoreKraiczy2025),
        partial(thiele_method, thiele_score_class=PAVScoreTalmonPaige2021),
        partial(thiele_method, thiele_score_class=PAVScoreHervouin2025),
    ],
    "av": [
        partial(sequential_thiele, thiele_score_class=ApprovalThieleScore),
        partial(sequential_thiele, thiele_score_class=NetSupportThieleScore),
        partial(thiele_method, thiele_score_class=ApprovalThieleScore),
        partial(thiele_method, thiele_score_class=NetSupportThieleScore),
        max_net_support_ilp,
        max_net_support,
    ],
    "cc": exhaustivee_cc,
    # ABCvoting only has MES with completion...
    # "equal-shares": [
    #     partial(tax_method_of_equal_shares, tax_function=DisapprovalLinearTax.initialize(1)),
    #     partial(tax_method_of_equal_shares, tax_function=TaxKraiczy2025),
    # ]
}


def process_yaml_file(yaml_file_path: str):
    profile_raw = parse_abcvoting_yaml(yaml_file_path)
    print("ABC Voting test: ", yaml_file_path)

    for profile in [profile_raw, profile_raw.as_multiprofile()]:
        expected_result = read_abcvoting_expected_result(yaml_file_path, profile)

        for rule_id, rules in RULE_MAPPING.items():
            if not isinstance(rules, Iterable):
                rules = [rules]
            for rule in rules:
                # print("\t", rule)
                potential_results_repr = expected_result[rule_id]
                try:
                    selection = rule(
                        profile, profile.max_size_selection, resoluteness=True
                    )
                    selection_repr = resolute_res_representation(
                        selection.selected, profile
                    )
                    # print("\t", "R", selection_repr, potential_results_repr)
                    assert selection_repr in potential_results_repr, f"Failure on {os.path.basename(yaml_file_path)} (m={len(profile.alternatives)}, n={profile.num_ballots()}) with resolute {rule.__name__}: {selection_repr} not in {potential_results_repr}"
                except NotImplementedError:
                    pass

                try:
                    selections = rule(
                        profile, profile.max_size_selection, resoluteness=False
                    )
                    selections_repr = irresolute_res_representation(
                        [s.selected for s in selections], profile
                    )
                    # print("\t", "IR", selections_repr, potential_results_repr)
                    assert selections_repr == potential_results_repr, f"Failure on {os.path.basename(yaml_file_path)} (m={len(profile.alternatives)}, n={profile.num_ballots()}) with resolute {rule.__name__}: {selections_repr} != {potential_results_repr}"
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
