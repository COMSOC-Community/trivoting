Election module
===============

.. automodule:: trivoting.election

Alternatives
------------

.. automodule:: trivoting.election.alternative

.. autoclass:: trivoting.election.alternative.Alternative
    :members:
    :show-inheritance:

Trichotomous Ballots
--------------------

.. automodule:: trivoting.election.trichotomous_ballot

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

.. automodule:: trivoting.election.trichotomous_profile

.. autoclass:: trivoting.election.trichotomous_profile.AbstractTrichotomousProfile

.. autoclass:: trivoting.election.trichotomous_profile.TrichotomousProfile
    :members:
    :show-inheritance:

.. autoclass:: trivoting.election.trichotomous_profile.TrichotomousMultiProfile
    :members:
    :show-inheritance:

Link to abcvoting
-----------------

.. automodule:: trivoting.election.abcvoting

.. autofunction:: trivoting.election.abcvoting.abcvoting_to_trichotomous_profile

.. autofunction:: trivoting.election.abcvoting.parse_abcvoting_yaml

Link with Pabulib and pabutools
-------------------------------

.. automodule:: trivoting.election.pabulib

.. autofunction:: trivoting.election.pabulib.parse_pabulib

.. autofunction:: trivoting.election.pabulib.pb_approval_profile_to_trichotomous_profile

.. autofunction:: trivoting.election.pabulib.pb_approval_ballot_to_trichotomous_ballot

Link with PrefLib
-----------------

.. automodule:: trivoting.election.preflib

.. autofunction:: trivoting.election.preflib.parse_preflib

.. autofunction:: trivoting.election.preflib.cat_instance_to_trichotomous_profile

.. autofunction:: trivoting.election.preflib.cat_preferences_to_frozen_trichotomous_ballot

Generate Random Profile
-----------------------

.. automodule:: trivoting.election.generate

.. autofunction:: trivoting.election.generate.generate_random_ballot

.. autofunction:: trivoting.election.generate.generate_random_profile

Selection
---------

.. automodule:: trivoting.election.selection

.. autoclass:: trivoting.election.selection.Selection
    :members:
    :show-inheritance:
