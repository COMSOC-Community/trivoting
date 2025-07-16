Election module
===============

.. automodule:: trivoting.election

Alternatives
------------

.. autoclass:: trivoting.election.alternative.Alternative
    :members:
    :show-inheritance:

Trichotomous Ballots
--------------------

.. autoclass:: trivoting.election.trichotomous_ballot.AbstractTrichotomousBallot
    :members:
    :show-inheritance:

.. autoclass:: trivoting.election.trichotomous_ballot.TrichotomousBallot
    :members:
    :show-inheritance:

.. autoclass:: trivoting.election.trichotomous_ballot.FrozenTrichotomousBallot
    :members:
    :show-inheritance:

Trichotomous Profiles
---------------------

.. autoclass:: trivoting.election.trichotomous_profile.AbstractTrichotomousProfile

.. autoclass:: trivoting.election.trichotomous_profile.TrichotomousProfile
    :members:
    :show-inheritance:

.. autoclass:: trivoting.election.trichotomous_profile.TrichotomousMultiProfile
    :members:
    :show-inheritance:

Link to abcvoting
-----------------

.. autofunction:: trivoting.election.abcvoting.abcvoting_to_trichotomous_profile

.. autofunction:: trivoting.election.abcvoting.parse_abcvoting_yaml

Link with Pabulib and pabutools
-------------------------------

.. autofunction:: trivoting.election.pabulib.parse_pabulib

.. autofunction:: trivoting.election.pabulib.pb_approval_profile_to_trichotomous_profile

.. autofunction:: trivoting.election.pabulib.pb_approval_ballot_to_trichotomous_ballot

Link with PrefLib
-----------------

.. autofunction:: trivoting.election.preflib.parse_preflib

.. autofunction:: trivoting.election.preflib.cat_instance_to_trichotomous_profile

.. autofunction:: trivoting.election.preflib.cat_preferences_to_trichotomous_ballot

Generate Random Profile
-----------------------

.. autofunction:: trivoting.election.generate.generate_random_ballot

.. autofunction:: trivoting.election.generate.generate_random_profile
