Rules module
============

.. automodule:: trivoting.rules

Meta Rule
---------

.. automodule:: trivoting.rules.ilp_schemes

.. autoclass:: trivoting.rules.ilp_schemes.ILPNotOptimalError
    :members:
    :show-inheritance:

.. autoclass:: trivoting.rules.ilp_schemes.ILPBuilder
    :members:
    :show-inheritance:

.. autoclass:: trivoting.rules.ilp_schemes.PuLPSolvers
    :members:
    :show-inheritance:

.. autofunction:: trivoting.rules.ilp_schemes.ilp_optimiser_rule


Thiele Methods
--------------

.. automodule:: trivoting.rules.thiele

.. autoclass:: trivoting.rules.thiele.ThieleScore
    :members:
    :show-inheritance:

.. autoclass:: trivoting.rules.thiele.PAVScoreKraiczy2025

.. autoclass:: trivoting.rules.thiele.PAVScoreTalmonPaige2021

.. autoclass:: trivoting.rules.thiele.PAVScoreHervouin2025

.. autoclass:: trivoting.rules.thiele.ApprovalThieleScore

.. autoclass:: trivoting.rules.thiele.NetSupportThieleScore

.. autofunction:: trivoting.rules.thiele.thiele_method

.. autofunction:: trivoting.rules.thiele.sequential_thiele

Sequential Phragmén's Rule
--------------------------

.. automodule:: trivoting.rules.phragmen

.. autofunction:: trivoting.rules.phragmen.sequential_phragmen


Tax-Based Rules
---------------

.. automodule:: trivoting.rules.tax_rules

.. autoclass:: trivoting.rules.tax_rules.TaxFunction
    :members:
    :show-inheritance:

.. autoclass:: trivoting.rules.tax_rules.TaxKraiczy2025

.. autoclass:: trivoting.rules.tax_rules.DisapprovalLinearTax

.. autofunction:: trivoting.rules.tax_rules.tax_pb_instance

.. autofunction:: trivoting.rules.tax_rules.tax_pb_rule_scheme

.. autofunction:: trivoting.rules.tax_rules.tax_method_of_equal_shares

.. autofunction:: trivoting.rules.tax_rules.tax_sequential_phragmen
