Election module
===============

.. automodule:: trivoting.election

Alternative
-----------

.. autoclass:: trivoting.election.alternative.Alternative
    :members:
    :show-inheritance:

Trichotomous Ballot
-------------------

.. autoclass:: trivoting.election.trichotomous_ballot.AbstractTrichotomousBallot
    :members:
    :show-inheritance:

.. autoclass:: trivoting.election.trichotomous_ballot.TrichotomousBallot
    :members:
    :show-inheritance:

.. autoclass:: trivoting.election.trichotomous_ballot.FrozenTrichotomousBallot
    :members:
    :show-inheritance:

Trichotomous Profile
--------------------

.. autoclass:: trivoting.election.trichotomous_profile.AbstractTrichotomousProfile
    :members:
    :show-inheritance:

.. autoclass:: trivoting.election.trichotomous_profile.TrichotomousProfile
    :members:
    :show-inheritance:

.. autoclass:: trivoting.election.trichotomous_profile.TrichotomousMultiProfile
    :members:
    :show-inheritance:

ABC Voting
----------

.. autofunction:: trivoting.election.abcvoting.abcvoting_to_trichotomous_profile

.. autofunction:: trivoting.election.abcvoting.parse_abcvoting_yaml

Pabulib
-------

.. autofunction:: trivoting.election.pabulib.parse_pabulib

.. autofunction:: trivoting.election.pabulib.pb_approval_profile_to_trichotomous_profile

.. autofunction:: trivoting.election.pabulib.pb_approval_ballot_to_trichotomous_ballot

PrefLib
-------

.. autofunction:: trivoting.election.preflib.parse_preflib

.. autofunction:: trivoting.election.preflib.cat_instance_to_trichotomous_profile

.. autofunction:: trivoting.election.preflib.cat_preferences_to_trichotomous_ballot

Generate Random Profile
-----------------------

.. autofunction:: trivoting.election.generate.generate_random_ballot

.. autofunction:: trivoting.election.generate.generate_random_profile
