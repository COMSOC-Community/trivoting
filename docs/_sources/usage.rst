.. _usage:

Complete Guide
==============

Alternatives
------------

Please refer to the module :py:mod:`~trivoting.election.alternative` for more information.

An alternative represents a possible outcome of the election. It is defined by a single attribute: its name.
Equality, comparison, and hashing are all based on this name.

The central class is :py:class:`~trivoting.election.alternative.Alternative`.

.. code-block:: python

    from trivoting.election import Alternative

    # Creating alternatives
    a1 = Alternative("Option A")
    a2 = Alternative("Option B")
    a3 = Alternative("Option C")

    # Alternatives are compared based on their names
    print(a1 == "Option A")  # True
    print(a1 == a2)          # False

    # They can be used in sets and as dictionary keys
    alternatives_set = {a1, a2}
    print(a3 in alternatives_set)  # False

    # Sorting alternatives is based on name
    sorted_alts = sorted([a2, a1, a3])
    print(sorted_alts)  # ['Option A', 'Option B', 'Option C']

Trichotomous Ballots
--------------------

Please refer to the module :py:mod:`~trivoting.election.trichotomous_ballot` for more information.

Ballots contain the opinions of voters over a set of alternatives. In the trichotomous model,
each voter categorizes alternatives into three categories:

- **Approved**
- **Disapproved**
- **Neutral** (implicitly defined as those that are neither approved nor disapproved)

The base interface is :py:class:`~trivoting.election.trichotomous_ballot.AbstractTrichotomousBallot`, which is subclassed by
two concrete classes:

- :py:class:`~trivoting.election.trichotomous_ballot.TrichotomousBallot`: a mutable version.
- :py:class:`~trivoting.election.trichotomous_ballot.FrozenTrichotomousBallot`: an immutable, hashable version suitable for use in sets or as dictionary keys.

.. code-block:: python

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
    print(ballot.approved)     # {Option A, Option C}
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

Profiles
--------

Please refer to the module :py:mod:`~trivoting.election.trichotomous_profile` for more information.

The `trivoting` package provides classes to represent collections of trichotomous ballots, called profiles.
A profile models a group of voters' preferences classified into three categories: approved, disapproved, and not classified alternatives.

Two main profile classes are available:

- :py:class:`~trivoting.election.trichotomous_profile.TrichotomousProfile`: stores ballots individually, one per voter.
- :py:class:`~trivoting.election.trichotomous_profile.TrichotomousMultiProfile`: stores ballots with multiplicities, grouping identical ballots together.

TrichotomousProfile
^^^^^^^^^^^^^^^^^^^

The :py:class:`~trivoting.election.trichotomous_profile.TrichotomousProfile` class represents a list of ballots, where
each ballot is an instance of :py:class:`~trivoting.election.trichotomous_ballot.TrichotomousBallot`.
You can initialize a profile with an iterable of ballots, and optionally provide a set of alternatives and a maximum size for selections.

.. code-block:: python

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

    # Iterate over ballots
    for ballot in profile:
        print(ballot)

    # Convert to a multiprofile (groups ballots by multiplicity)
    multiprofile = profile.as_multiprofile()


Profile also have a `max_size_selection` attribute that indicates the maximum number of alternatives that can be selected
in a feasible outcome. The usage is reserved for parsing files. Users should not expect this attribute to be considerd
in most functions. Most functions needing this information require the value to be explicitly passed as an argument.

TrichotomousMultiProfile
^^^^^^^^^^^^^^^^^^^^^^^^

The :py:class:`~trivoting.election.trichotomous_profile.TrichotomousMultiProfile` class represents profiles where
ballots are stored with their multiplicities. It makes use of the :py:class:`~trivoting.election.trichotomous_ballot.FrozenTrichotomousBallot`
for the ballots.
This is more efficient when many voters have identical ballots.

.. code-block:: python

    from trivoting.election.trichotomous_ballot import FrozenTrichotomousBallot
    from trivoting.election.trichotomous_profile import TrichotomousMultiProfile

    # Freeze ballots to make them hashable and usable in multiprofiles
    frozen_ballot1 = ballot1.freeze()
    frozen_ballot2 = ballot2.freeze()

    # Initialize multiprofile with multiple copies of ballots
    multi_profile = TrichotomousMultiProfile([frozen_ballot1, frozen_ballot1, frozen_ballot2], alternatives=[a, b, c])

    # Multiplicity of a specific ballot
    multiplicity = multi_profile.multiplicity(frozen_ballot1)

    # Acces the ballots (behaves like a dict)
    profile[ballot1] = 3
    profile[ballot2] += 1

    # Iterate over ballots
    for ballot in multi_profile:
        print(ballot)

Details of a Profile
^^^^^^^^^^^^^^^^^^^^

Both classes provide the same methods to extract information about the profile.

.. code-block:: python

    for profile in [multi_profile, profile]:
        # Number of ballots
        n = profile.num_ballots()

        # Support score of alternative a (approvals minus disapprovals)
        support_a = profile.support(a)
        support_dict = profile.support_dict

        # Approval score (number of voters approving a)
        approval_a = profile.approval_score(a)

        # Disapproval score (number of voters disapproving a)
        disapproval_a = profile.disapproval_score(a)

        # All approval scores as a dictionary
        approval_dict = profile.approval_score_dict()

        # Iterate over all feasible selections (partial outcomes)
        for selection in profile.all_feasible_selections(max_size_selection=2):
            print(selection)
        common_approved = profile.commonly_approved_alternatives()
        common_disapproved = profile.commonly_disapproved_alternatives()


You can generate all subprofiles (all subsets of ballots), for both normal profiles and multiprofiles:

.. code-block:: python

    for subprofile in profile.all_sub_profiles():
        print(subprofile)

    for sub_multi_profile in multi_profile.all_sub_profiles():
        print(sub_multi_profile)

You can also generate all the feasible selections of the profile:

.. code-block:: python

    for selection in profile.all_feasible_selections(2):
        print(selection)


Interoperability with Other Libraries
-------------------------------------

This package provides functions to convert and parse election data from several popular external libraries/formats into
:py:class:`~trivoting.election.trichotomous_profile.TrichotomousProfile` objects used internally.

PrefLib Integration
^^^^^^^^^^^^^^^^^^^

Please refer to the module :py:mod:`~trivoting.election.preflib` for more information.

PrefLib is a popular dataset repository and parsing toolkit for voting preferences.
The module supports conversion of PrefLib categorical preferences (with up to 3 categories) into trichotomous ballots.

.. code-block:: python

    from trivoting.election import parse_preflib

    profile = parse_preflib("path/to/preflib_file.cat")

PaBuLib Integration
^^^^^^^^^^^^^^^^^^^

Please refer to the module :py:mod:`~trivoting.election.pabulib` for more information.

PaBuLib is a library for participatory budgeting profiles. Approval-based PaBuLib elections can be converted to our
format.

.. code-block:: python

    from trivoting.election import parse_pabulib

    profile = parse_pabulib("path/to/preflib_file.pb")
    print(profile.max_size_selection)  # The budget limit is saved as 'max_size_selection'

AbcVoting Integration
^^^^^^^^^^^^^^^^^^^^^

Please refer to the module :py:mod:`~trivoting.election.abcvoting` for more information.

The abcvoting library focuses on approval-based multiwinner elections. It can outputs preference files in the form
of a YAML file. These files can be parsed into the trivoting package.

.. code-block:: python

    from trivoting.election import parse_abcvoting_yaml

    profile = parse_abcvoting_yaml("path/to/abcvoting_profile.yaml")
    print(profile.max_size_selection)  # Parameter 'k' is saved in 'max_size_selection'

Random Generation of Profiles
-----------------------------

Please refer to the module :py:mod:`~trivoting.election.generate` for more information.

We provide convenient functions to generate random trichotomous ballots and profiles. You can control how alternatives
are assigned to approved, neutral, and disapproved categories by supplying your own sampling functions.
The sampling functions can typically be taken from the `prefsampling` package.

.. code-block:: python

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
        100, # num_alternatives
        100, # num_voters
        my_urn_sampler,  # First sampler to divide between divides between potentially approved and potentially disapproved
        my_resampling_sampler,  # Second sampler selects the definitively approved from the set of potentially approved
        my_noise_sampler,  # Third sampler selects the definitively disapproved from the set of potentially disapproved
    )


Selection
---------

Please refer to the module :py:mod:`~trivoting.election.selection` for more information.

Selections are used to represent the outcome of a rule: which alternatives are selected and which are rejected.
The central class is :py:class:`~trivoting.election.selection.Selection`.

A selection always includes the selected alternatives. Rejected alternatives can either be explicitly provided or be
implicitly inferred (i.e., anything not selected is considered rejected). This behavior is controlled by the ``implicit_reject`` flag.

.. code-block:: python

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

You can check whether an alternative is selected or rejected using the corresponding methods:

.. code-block:: python

    selection.is_selected(a1)      # True
    selection.is_rejected(a2)      # True, because a2 is not selected

    selection_explicit.is_selected(a1)   # True
    selection_explicit.is_rejected(a2)   # True
    selection_explicit.is_rejected(a3)   # True

You can add or extend the selected and rejected sets dynamically:

.. code-block:: python

    a4 = Alternative("a4")

    selection.add_selected(a4)
    selection.extend_selected([Alternative("a5")])

    selection_explicit.add_rejected(Alternative("a6"))
    selection_explicit.extend_rejected([Alternative("a7"), Alternative("a8")])


Rules
-----

Rules are used to determine selections based on a profile. They all take a `max_size_selection` argument that indicates
the maximum number of alternatives that can be selected. Since ballots can indicate disapproval, rules need not select
exactly the desired number of alternatives.

We try to always offer the possibility to ask for resolute or irresolute outcomes, via the `resoluteness` argument.
The tie breaking rule to use can typically be specified via the `tie_breaking`
argument (not all the rules support that). See the :py:mod:`~trivoting.tiebreaking` module for more information.
Initial selection can usually be passed to the rules via the `initial` argument. The rule then completes the initial
selection.

Proportional Approval Voting (PAV)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The :py:func:`~trivoting.rules.pav.proportional_approval_voting` function implements the Proportional Approval Voting (PAV)
rule using Integer Linear Programming (ILP).

You need to pass a trichotomous profile (implementing the :py:class:`~trivoting.election.trichotomous_profile.AbstractTrichotomousProfile` interface)
and specify the maximum number of alternatives to select.

.. code-block:: python

    from trivoting.rules import proportional_approval_voting

    selection = proportional_approval_voting(profile, max_size_selection=3)

    print(result)

By default, the function returns a single optimal selection (resolute). To retrieve all optimal selections (if multiple exist), set `resoluteness=False`.

.. code-block:: python

    results = proportional_approval_voting(profile, max_size_selection=3, resoluteness=False)

    for selection in results:
        print(selection)
    # Example output:


You can fix certain alternatives to be selected or rejected by providing an initial :py:class:`~trivoting.election.selection.Selection` object.

.. code-block:: python

    from trivoting.election import Selection

    initial = Selection(selected=[a1], implicit_reject=True)

    result = proportional_approval_voting(profile, max_size_selection=3, initial_selection=initial)

Additional options for the ILP solver can be passed:

- ``verbose=True`` enables output from the ILP solver.
- ``max_seconds`` can be used to limit the computation time (default: 600 seconds).

.. code-block:: python

    result = proportional_approval_voting(
        profile,
        max_size_selection=4,
        resoluteness=True,
        verbose=True,
        max_seconds=300
    )

Sequential Phragmén
^^^^^^^^^^^^^^^^^^^

The :py:func:`~trivoting.rules.phragmen.sequential_phragmen` function implements the sequential Phragmén rule
adapted to trichotomous preferences. This method distributes load among voters to achieve proportional representation.

You need to pass a trichotomous profile (implementing the :py:class:`~trivoting.election.trichotomous_profile.AbstractTrichotomousProfile` interface)
and specify the maximum number of alternatives to select.

.. code-block:: python

    from trivoting.rules import sequential_phragmen

    selection = sequential_phragmen(profile, max_size_selection=3)


By default, the function returns a single optimal selection (resolute). To retrieve all optimal selections (if multiple exist), set `resoluteness=False`.

.. code-block:: python

    results = sequential_phragmen(profile, max_size_selection=3, resoluteness=False)

    for selection in results:
        print(selection)
    # Example output:
    # {[a1, a2, a5]} // {implicit}
    # {[a1, a3, a5]} // {implicit}

You can fix certain alternatives to be selected or rejected by providing an initial :py:class:`~trivoting.election.selection.Selection` object.

.. code-block:: python

    from trivoting.election import Selection

    initial = Selection(selected=[a1], implicit_reject=True)

    result = sequential_phragmen(profile, max_size_selection=3, initial_selection=initial)

Additional options include:

- ``initial_loads``: a list of numeric values to set initial loads for the voters (default is 0 for all).
- ``tie_breaking``: a custom tie-breaking rule. Defaults to lexicographic tie-breaking.

.. code-block:: python

    from trivoting.tiebreaking import lexico_tie_breaking

    result = sequential_phragmen(
        profile,
        max_size_selection=4,
        initial_loads=[0, 0, 0],
        initial_selection=initial,
        tie_breaking=lexico_tie_breaking,
        resoluteness=True
    )


Tax PB Rule Scheme
^^^^^^^^^^^^^^^^^^

The :py:func:`~trivoting.rules.tax_rules.tax_pb_rule_scheme` function implements a generic scheme for applying
participatory budgeting (PB) rules to trichotomous profiles converted into PB instance via an opposition tax.

This method first translates the trichotomous profile into a PB instance by assigning higher costs to alternatives with
lower net support (approvals minus disapprovals). It then applies a PB rule from the `pabutools` package and converts
the resulting budget allocations back into selections of alternatives.

You need to pass a trichotomous profile (implementing the :py:class:`~trivoting.election.trichotomous_profile.AbstractTrichotomousProfile` interface),
specify the maximum number of alternatives to select and the PB rule to use (that may require kwargs).

.. code-block:: python

    from trivoting.rules import tax_pb_rule_scheme
    from pabutools.rules import method_of_equal_shares

    selection = tax_pb_rule_scheme(
        profile,
        max_size_selection=5,
        pb_rule=method_of_equal_shares,
        pb_rule_kwargs={"sat_class": pb_election.Cardinality_Sat}
    )

Additionally, resoluteness, initial selection and tie-breaking can be specified:

.. code-block:: python

    from trivoting.tiebreaking import lexico_tie_breaking

    selection = tax_pb_rule_scheme(
        profile,
        max_size_selection=5,
        pb_rule=method_of_equal_shares,
        pb_rule_kwargs={"sat_class": pb_election.Cardinality_Sat},
        resoluteness=False,
        tie_breaking=lexico_tie_breaking,
        initial_selection=selection
    )

Two tax-based rules are defined by default: :py:func:`~trivoting.rules.tax_rules.tax_method_of_equal_shares` and
:py:func:`~trivoting.rules.tax_rules.tax_sequential_phragmen`.

.. code-block:: python

    from trivoting.rules import tax_pb_rule_scheme

    selection_mes = tax_method_of_equal_shares(
        profile,
        max_size_selection=5,
        resoluteness=False,
        tie_breaking=lexico_tie_breaking,
        initial_selection=selection
    )

    selection_phrag = tax_sequential_phragmen(
        profile,
        max_size_selection=5,
        resoluteness=False,
        tie_breaking=lexico_tie_breaking,
        initial_selection=selection
    )

Tie-Breaking
------------

Please refer to the module :py:mod:`~trivoting.tiebreaking` for more information.

We provide several ways to break ties between several projects. All tie-breaking rules are
instantiations of the :py:class:`~trivoting.tiebreaking.TieBreakingRule` class.
This class defines two functions `untie` and `order` that respectively return a single project
from a set of several or order a list of projects.

We profile several tie-breaking rules:

- :py:func:`~trivoting.tiebreaking.lexico_tie_breaking`
- :py:func:`~trivoting.tiebreaking.support_tie_breaking`
- :py:func:`~trivoting.tiebreaking.refuse_tie_breaking`

.. code-block:: python

    from trivoting.tiebreaking import lexico_tie_breaking, support_tie_breaking, app_score_tie_breaking

        # Offers order() or untie() to either order alternatives
        # or single out an alternative

        # Lexicographic tie-breaking based on name
        order_alts = lexico_tie_breaking.order(profile, alt_set)
        alt = lexico_tie_breaking.untie(profile, alt_set)

        # Tie-breaking based on support of an alternative
        order_alts = support_tie_breaking.order(profile, alt_set)

        # Tie-breaking based on the approval score of an alternative
        alt = app_score_tie_breaking.untie(profile, alt_set)

Other tie-breaking rules can be implemented by instantiating the :py:class:`~trivoting.tiebreaking.TieBreakingRule` class.

Axiomatic
---------

Justified Representation
^^^^^^^^^^^^^^^^^^^^^^^^

Please refer to the module :py:mod:`~trivoting.axiomatic.justified_representation` for more information.

We provide utilities for verifying various justified representation (JR) axioms
in trichotomous voting settings: base EJR, base PJR, positive EJR and group veto.

.. code-block:: python

    from trivoting.axiomatic import is_base_ejr, is_base_pjr

    is_base_ejr(profile, k, selection)  # Uses closed-form characterization (efficient)
    is_base_pjr(profile, k, selection)  # Checks PJR using all cohesive groups

    from trivoting.axiomatic import is_positive_ejr, is_group_veto

    is_positive_ejr(profile, k, selection)  # Checks if all positively cohesive groups are satisfied
    is_group_veto(profile, k, selection)  # Ensures no sufficiently strong group is overruled


Fractions
---------

Please refer to the module :py:mod:`~trivoting.fractions` for more information.

We provide a customizable way to handle fractions. In general, all fractions should be defined
using the :py:func:`~trivoting.fractions.frac` function provided in the :py:mod:`~trivoting.fractions`
module. Not doing so may lead to undesirable behaviors (i.e., errors).

To make a fraction, simply follow this guide:

.. code-block:: python

    from trivoting.fractions import frac, str_as_frac

    # Define a fraction
    fraction = frac(1, 4)

    # Define a fraction from an integer
    fraction_from_int = frac(2)

    # Define a fraction from a float
    fraction_from_int = frac(2.6)

    # Define a fraction from a string
    fraction_from_str = str_as_frac("2.3")

By default, the `gmpy2 <https://gmpy2.readthedocs.io/en/latest/mpq.html>`_ module is used to
handle fractions. To change this, simply change the value of the `FRACTION` constant.

.. code-block:: python

    import trivoting.fractions

    # The default value
    pabutools.fractions.FRACTION = "gmpy2"

    # Change to Python float
    pabutools.fractions.FRACTION = "float"

Changing the `FRACTION` constant changes the algorithm used to handle fractions.

