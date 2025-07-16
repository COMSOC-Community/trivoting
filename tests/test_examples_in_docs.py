import unittest


class TestExamplesInDocs(unittest.TestCase):
    def test_alternatives(self):
        from trivoting.election import Alternative

        # Creating alternatives
        a1 = Alternative("Option A")
        a2 = Alternative("Option B")
        a3 = Alternative("Option C")

        # Alternatives are compared based on their names
        print(a1 == "Option A")  # True
        print(a1 == a2)  # False

        # They can be used in sets and as dictionary keys
        alternatives_set = {a1, a2}
        print(a3 in alternatives_set)  # False

        # Sorting alternatives is based on name
        sorted_alts = sorted([a2, a1, a3])
        print(sorted_alts)

    def test_ballots(self):
        from trivoting.election import Alternative, TrichotomousBallot

        # Create some alternatives
        a1 = Alternative("Option A")
        a2 = Alternative("Option B")
        a3 = Alternative("Option C")

        # Create a trichotomous ballot
        ballot = TrichotomousBallot(
            approved=[a1],
            disapproved=[a2]
        )

        print(ballot)  # {Option A} // {Option B}

        # Add more opinions
        ballot.add_approved(a3)
        print(ballot.approved)  # {Option A, Option C}
        print(ballot.disapproved)  # {Option B}

        # Check membership
        print(a1 in ballot)  # True as a1 is approved
        print(a2 in ballot)  # True as s2 is disapproved
        print(Alternative("Option D") in ballot)  # False

        # Freeze the ballot to make it immuable
        frozen = ballot.freeze()
        print(frozen)  # (Option A, Option C) // (Option B)

        # Frozen ballots are immutable and hashable
        ballot_set = {frozen}
        print(frozen in ballot_set)  # True

    def test_profiles(self):
        from trivoting.election.alternative import Alternative
        from trivoting.election.trichotomous_ballot import TrichotomousBallot
        from trivoting.election.trichotomous_profile import TrichotomousProfile

        # Define alternatives
        a = Alternative("a")
        b = Alternative("b")
        c = Alternative("c")

        # Create ballots
        ballot1 = TrichotomousBallot(approved=[a, b], disapproved=[c])
        ballot2 = TrichotomousBallot(approved=[b], disapproved=[a])

        # Initialize profile
        profile = TrichotomousProfile([ballot1, ballot2, ballot1, ballot2], alternatives=[a, b, c])

        # Access ballots (behaves like a list)
        b_at_pos_1 = profile[1]
        b_at_pos_1_to_3 = profile[1:3]
        profile.append(ballot1)
        profile.extend([ballot1, ballot2])

        # Convert to a multiprofile (groups ballots by multiplicity)
        multiprofile = profile.as_multiprofile()

        # Iterate over ballots
        for ballot in profile:
            print(ballot)

        from trivoting.election.trichotomous_ballot import FrozenTrichotomousBallot
        from trivoting.election.trichotomous_profile import TrichotomousMultiProfile

        # Freeze ballots to make them hashable and usable in multiprofiles
        frozen_ballot1 = ballot1.freeze()
        frozen_ballot2 = ballot2.freeze()

        # Initialize multiprofile with multiple copies of ballots
        multi_profile = TrichotomousMultiProfile([frozen_ballot1, frozen_ballot1, frozen_ballot2],
                                                 alternatives=[a, b, c])

        # Multiplicity of a specific ballot
        multiplicity = multi_profile.multiplicity(frozen_ballot1)

        for ballot in profile:
            print(ballot)

        for subprofile in profile.all_sub_profiles():
            print(subprofile)

        for sub_multi_profile in multi_profile.all_sub_profiles():
            print(sub_multi_profile)

        for selection in profile.all_feasible_selections(2):
            print(selection)

        for profile in [multi_profile, profile]:
            # Number of ballots
            n = profile.num_ballots()

            # Support score of alternative a (approvals minus disapprovals), or for all alternatives
            support_a = profile.support(a)
            support_dict = profile.support_dict()

            # Approval score (number of voters approving a), or for all alternatives
            approval_a = profile.approval_score(a)
            approval_score_dict = profile.approval_score_dict()

            # Disapproval score (number of voters disapproving a), or for all alternatives
            disapproval_a = profile.disapproval_score(a)
            disapproval_score_dict = profile.disapproval_score_dict()

            # Approval and  disapproval score at the same time or for all alternatives
            disapproval_a = profile.disapproval_score(a)
            disapproval_score_dict = profile.disapproval_score_dict()

            # Set of alternatives approved/disapproved in all ballots of the profile
            common_approved = profile.commonly_approved_alternatives()
            common_disapproved = profile.commonly_disapproved_alternatives()

    def test_preference_libraries(self):
        from trivoting.election import parse_pabulib, parse_preflib, parse_abcvoting_yaml

    def test_generate(self):

        from trivoting.election.generate import generate_random_profile
        # Use the set samplers from prefsampling
        from prefsampling.approval import urn, resampling, noise

        def my_urn_sampler(num_voters, num_candidates):
            return urn(num_voters, num_candidates, p=0.33, alpha=0.7)

        def my_resampling_sampler(num_voters, num_candidates):
            return resampling(num_voters, num_candidates, phi=0.5, rel_size_central_vote=0.5)

        def my_noise_sampler(num_voters, num_candidates):
            return noise(num_voters, num_candidates, phi=0.5, rel_size_central_vote=0.5)

        generate_random_profile(
            100,  # num_alternatives
            100,  # num_voters
            my_urn_sampler,
            # First sampler to divide between divides between potentially approved and potentially disapproved
            my_resampling_sampler,
            # Second sampler selects the definitively approved from the set of potentially approved
            my_noise_sampler,
            # Third sampler selects the definitively disapproved from the set of potentially disapproved
        )

    def test_selection(self):
        from trivoting.election import Alternative, Selection

        a1 = Alternative("a1")
        a2 = Alternative("a2")
        a3 = Alternative("a3")

        # Implicit rejection (default): everything not selected is rejected
        selection = Selection(selected=[a1])

        # Count how many alternatives are selected
        len(selection)

        # Count total number of selected + rejected alternatives
        selection.total_len()

        # Explicit rejection
        selection_explicit = Selection(selected=[a1], rejected=[a2, a3], implicit_reject=False)

        selection.is_selected(a1)      # True
        selection.is_rejected(a2)      # True, because a2 is not selected

        selection_explicit.is_selected(a1)   # True
        selection_explicit.is_rejected(a2)   # True
        selection_explicit.is_rejected(a3)

        a4 = Alternative("a4")

        selection.add_selected(a4)
        selection.extend_selected([Alternative("a5")])

        selection_explicit.add_rejected(Alternative("a6"))
        selection_explicit.extend_rejected([Alternative("a7"), Alternative("a8")])
