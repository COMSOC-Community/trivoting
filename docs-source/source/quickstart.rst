.. _quickstart:

Quick Start
===========

Now that you have installed trivoting (if not, see :ref:`installation`), you can start
using the package!

On this page, we will guide you through a simple example.

Describing a Trichotomous Profile
---------------------------------

Alternatives
^^^^^^^^^^^^

The fundamental elements are the alternatives, i.e., the
entities that will be voted upon. We define them using the class
:py:class:`~trivoting.election.alternative.Alternative`.

.. code-block:: python

    from trivoting.election import Alternative

    a1 = Alternative("a1")   # The constructor takes the name of the alternative
    a2 = Alternative("a2")
    a3 = Alternative("a3")

Trichotomous Ballots
^^^^^^^^^^^^^^^^^^^^

With the alternatives we can define a trichotomous ballot. These are defined via the class
:py:class:`~trivoting.election.trichotomous_ballot.TrichotomousBallot`.

.. code-block:: python

    from trivoting.election import TrichotomousBallot

    b1 = TrichotomousBallot(approved=[a1, a2], disapproved=[a3])
    b2 = TrichotomousBallot(approved=[a1])  # approved and/or disapproved can be omitted
    b3 = TrichotomousBallot(disapproved=[a3])

We can now define a trichotomous profile:

.. code-block:: python

    from trivoting.election import TrichotomousProfile

    profile = TrichotomousProfile([b1, b2], alternatives={a1, a2, a3})  # Specify all the available alternatives
    profile.append(b3)   # Use list methods to handle the profile

Computing a Selection of Alternatives
-------------------------------------

With the profile being defined, we can now start computing selections of alternatives. Rules for selecting alternatives
are defined in the module :py:mod:`~trivoting.rules`.

.. code-block:: python

    from trivoting.rules import proportional_approval_voting

    max_selection_size = 2  # This is an upper bound on the size of the selection
    selection = proportional_approval_voting(profile, max_selection_size)


