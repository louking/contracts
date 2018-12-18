.. contractility documentation master file, created by
   sphinx-quickstart on Sun Dec 16 20:53:03 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to contractility's documentation!
=========================================

.. toctree::
   :maxdepth: 3
   :caption: Contents:

   contract-admin-guide
   contract-admin-reference
   contract-user-reference
   contract-definitions

The previous method of tracking race support business involves
maintenance of a Google Sheet (tab per year, row per weekend date). The
columns track all of the information required to generate the contract,
along with additional information for tracking when the invoice and
contract are sent, and when the payment and signed contract are
received. When the treasurer fills in all the fields required to go to
contract, a volunteer downloads the sheet and generates a Word file via
mail merge (saved as pdf). The treasurer emails the contract to the
client race director. The race director must sign the contract and
either scan/email or return via US Mail.

**contractility** automates much of the contract management flow. The
requirements for the tool are captured in `Race Support Contract
Management Requirements <https://docs.google.com/document/d/1WH2uHDB06FFOISQa5W9lNAxFINLMT44cMLdPIk848WE/edit?usp=sharing>`__.

Tool’s Primary Goals: Reduce the volunteer labor associated with
managing our race support business.

a) generate and track contracts with our race support clients. Reduce the processing related to signing contracts for both FSRC volunteer and race director. (Priority 1)

b) Make it easier to manage the data associated with our race support business with less manual manipulation of spreadsheets. (Priority 2)

c) Provide an availability calendar to aid race directors in selecting race dates. (Priority 2)

d) Automate status emails to race directors (Priority 2)

Tool’s secondary goal: support other agreements between FSRC and clients, e.g., for race sponsorship.

This document shows the race services contract flow.

The administrator should read :doc:`contract-admin-guide` and follow the specific use case they are interested 
in. Admininstrator and user process flows can be found within :doc:`contract-admin-reference` and 
:doc:`contract-user-reference` respectively. 

In addition to the admin and user process flows mentioned above, there
are some automated processes:

-  Before the race an automated email is generated. See :ref:`pre-event-coordination-email` for details.

-  After the race there are some actions which take place. See :ref:`post-event-processing` for details.

**Notes**

-  in this document the terms “contract” and “agreement” are used interchangeably.

Indices and tables
==================

* :ref:`genindex`
* :ref:`search`

.. move below `genindex` if needed
   * :ref:`modindex`
