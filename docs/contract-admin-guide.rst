===========================================
Administrator's Guide
===========================================

.. toctree::
   :maxdepth: 3
   :caption: Contents:

This document describes the **contractility** contract management system, for race contract management. Race 
directors generate race services requests to the administrator, who uses the system to create a record about 
the :term:`event` and generate a contract. The contract is email to the race director and the race services team. 
The race director accepts the contract through the system which generates another email and marks the
:term:`event` *committed*. 


.. _event-life-cycle:

Event Life Cycle
======================

This describes the life cycle for event management.

   * Race director sends Race Services Request email
     
     * see :ref:`contact-new-race`
   
   * Race director responds to the :ref:`post-event-email` or :ref:`post-event-email-reminder` 

     * if the race director says that the race will not be held

       * from :ref:`admin-calendar-view` click on the :term:`event` or from :ref:`event-overview-view`, 
         select the :term:`event`, click **Edit**, then click **Delete**

     * if the race director says they're not sure, or they don't have all the required information yet

       * from :ref:`admin-calendar-view` click on the :term:`event` or from :ref:`event-overview-view`, 
         select the :term:`event`, click **Edit**, change **State** to *tentative*, 
         then click **Update**

   * Details are learned from the race director about the :term:`event`

     * see :ref:`race-details-confirmed`
     * from :ref:`admin-calendar-view` click on the :term:`event` or from :ref:`event-overview-view`, 
       select the :term:`event`, click **Edit**
     * make sure **State** is set to *tentative*
     * update the details which are known, then click **Update**

   * All details are known for the :term:`event`, and the race director is ready to move forward 

     * see :ref:`race-details-confirmed`
     * click **Update and Send Contract** to generate a contract
     * :ref:`contract-email` is automatically generated to the race director 

   * About 5 days before the :term:`event`

     * :ref:`pre-event-coordination-email` is automatically generated, to the race director and event :term:`lead`

   * About 2 days before the :term:`event`
     
     * a reminder email automatically generated, just to the :term:`event` :term:`lead`

   * About 5 days after the :term:`event`

     * for :term:`events <event>` which have *finishline* or *coursemarking* :term:`services <service>`, 
       :ref:`post-event-email` is automatically generated
     * regardless of service, the :term:`event` is :term:`renewed <renew>`
     * see :ref:`post-event-processing` for additional details

   * If the :term:`event` is still in *renewed-pending* state 120 days before the expected date of the race

     * :ref:`post-event-email-reminder` is automatically generated to the race director

   * If the :term:`event` is still in *renewed-pending* state 30 days before the expected date of the race

     * admin should delete the event manually
     * from :ref:`admin-calendar-view` click on the :term:`event` or from 
       :ref:`event-overview-view`, select the :term:`event`, click **Edit** to get to the :ref:`edit-event-view`, 
       then click **Delete**


.. _event-state-flow:

Event State Flow
=================

.. graphviz::

   digraph{
      "renewed-pending" -> "tentative" [label="RD responds to renewal email"]
      "(New Race)" -> "tentative" [label="RD requests date"]
      "tentative" -> "tentative" [label="RD and admin confirm info"]
      "tentative" -> "contract-sent" [label="Update and Send Contract"]
      "contract-sent" -> "committed" [label="RD agrees to contract"]
      "contract-sent" -> "canceled" [label="RD cancels race"]
      "committed" -> "canceled" [label="RD cancels race"]
      "committed" -> "renewed-pending" [label="5 days after event"]
      "renewed-pending" -> "(delete)" [label="RD says no go"]
      "tentative" -> "(delete)" [label="RD says no go"]
      
      "renewed-pending" [color=cyan, style=filled]
      "tentative" [color=green, style=filled]
      "contract-sent" [color=cyan, style=filled]
      "committed" [color=cyan, style=filled]
      "canceled" [color=green, style=filled]
      "(delete)" [color=green, style=filled]

      "manual" [color=green, style=filled]
      "automatic" [color=cyan, style=filled]
   }


.. _use-cases:

Use Cases (What To Do...)
=========================


.. _log-in:

When You Want to Log In
-------------------------
From the contractility home page, click on `log in` in the upper right corner. You will be shown a google sign in 
challenge similar to below. Sign in with your steeplechasers.org account.

.. image:: images/choose-account.*
   :align: center

If this is your first time using the application, you be shown the following, which will give the application permission to create files in G Suite on your behalf. Click Allow

.. image:: images/sign-in-challenge.*
   :align: center


.. _contact-new-race:

When We Learn About a New Race
------------------------------

We learn about a new :term:`race` either through email generated by the :ref:`race-services-request-view`, other 
email, etc. Often there is incomplete information. Regardless, you should create the :term:`event` with whatever
information you have.

You can create an :term:`event` in one of two ways.

1. From :ref:`admin-calendar-view` click on the :term:`event` date
2. From :ref:`event-overview-view` click **New**

Once the form is displayed

   * fill in as much information as you have available to you
   * click **Create**

**If the Race has Finish Line Services** - Race directors may be contacting you with incomplete
information, and if so you will have to chase them down  to find all the relevant bits. This may
have to be done over time as often when they first contact us they may not have  all of the
information themselves.

**If the Race has Only Premium Promotion** - Premium promotion is executed through the
communications group rather than race services. We'll still be using  this tool to track that. It is
expected that the communication group will look at the **contractility** data periodically to
determine what races are to be promoted. See :ref:`contract-for-premium-promotion` for more details.


.. _contact-legacy-race:

When We're Contacted for a Race We've Done Before
------------------------------------------------------

If we've done a :term:`race` before, there will already be a database entry for the :term:`race`, and likely the
:term:`event` was :term:`renewed <renew>` after the previous year's race. 

You need to verify the current details with the race director and update the :term:`event` which was created.

You can find the event to edit in one of two ways.

   1. from :ref:`event-overview-view`, use the Search box at the top of the table, and enter the race name

      * you should see all the :term:`events <event>` associated with this :term:`race`
      * click on the :term:`event` for the coming year, then click **Edit**

   2. from :ref:`admin-calendar-view`, navigate to the date of the :term:`race's <race>` :term:`event`

      * click on the :term:`event`

Now you can edit the :term:`event` with the current details and when ready send the contract.

   * fill in as much information as you have available to you
   * change **State** to *tentative* 

     * **this is very important, if you don't do this the race
       director will receive extra confusing emails and we'll lose track of what we're doing**

   * click **Update**

     * or if you're ready to generate a contract, click **Update and Send Contract**


.. _race-director-questions:

When the Race Director has Questions
--------------------------------------

Some questions you get will have to go through Mark, as you won't be able to handle them -- generally these are 
questions about how to manage a race rather than contract related stuff. Probably best way to handle this is to 
forward to Mark, copying the RD, with appropriate text that Mark is best suited to respond. Hopefully if Mark 
gets information from them which needs to be in the database and you're not copied, he'll get it to you.


.. _race-details-confirmed:

When Race Details are Confirmed by Race Director
------------------------------------------------

As the details are confirmed by the race director, use the :ref:`edit-event-view` to update the :term:`event`. When
all the details are known and the race director is ready, generate the contract. 

You can edit an :term:`event` in one of two ways.

1. from :ref:`admin-calendar-view` navigate to the :term:`event` date and then click on the :term:`event` 
2. from :ref:`event-overview-view` click **Edit**

Before you can generate a contract for finish line services, you need at least the following:

   :Race: the name of the :term:`race`
   :Date: the date of the :term:`event`
   :Course: the :term:`course` the :term:`race` will be run on
   :Start Time: time of day that the main :term:`event` starts
   :Distance: distance for the :term:`race`
   :Client: the name of the :term:`client`
   :Services: one or more services which the client is contracting for
   :Max Participants: this is used to determine the pricing for finishline :term:`services <service>`
   :Lead: the leader who will run the finish line operation on the day of the :term:`event`. This needs to be 
      finalized well before the event so that emails are sent properly to all concerned

Before you can generate a contract for premium promotion service (only), you need at least the following:

   :Race: the name of the :term:`race`
   :Date: the date of the :term:`event`
   :Course: the :term:`course` the :term:`race` will be run on
   :Client: the name of the :term:`client`
   :Services: one or more services which the client is contracting for

The remaining fields are useful as well, and should be filled in if applicable and known.


.. _agreement-accepted-race-treasurer:

When Race Director Accepts Agreement (Treasurer)
-------------------------------------------------

When a race director accepts the agreement, the treasurer will receive an email. The :term:`event` will 
automatically be transitioned into the *committed* :term:`state`. 

An invoice should be generated to the :term:`client` as indicated by the financial policies. Once an invoice is 
generated, the treasurer should click the **Invoice Sent** button on the :ref:`edit-event-view`. 


.. _agreement-accepted-race-services:

When Race Director Accepts Agreement (Race Services Admin)
-----------------------------------------------------------

When a race director accepts the agreement, the race services admin will receive an email. The :term:`event` will 
automatically be transitioned into the *committed* :term:`state`. 

The :term:`lead` for the race needs to be identified well before the event so that resources are allocated 
correctly and emails are sent to the appropriate people. Generally we should have a committment for a :term:`lead`
before sending the contract to the race director, however the system does not enforce this.


.. _contract-for-premium-promotion:

When We Contract for Premium Promotion (Communications)
----------------------------------------------------------

The communications team handles all premium promotion, regardless of whether the race has also contracted for
other services.

To determine the events for the next premium promotion email, use the :ref:`event-overview-view` filters:

   :States: select *committed*
   :Date Range: From the day the email goes out, To [3 months] after that
   :Service(s): select *premiumpromotion*

The table will be filtered to only the :term:`events <event>` which should be in the next email.

The **CSV** button can be used to download these :term:`events <event>`, if desired.


.. _changes-to-committed-agreement:

When Changes Need to be Made to a Committed Agreement
---------------------------------------------------------------

Occasionally, after the race director has agreed to the contract, there needs to be a change. E.g., if the race
director decides on premium promotion after the initial agreement, a change needs to be made.

When the contract is in *committed* :term:`state`, the **Update and Send Contract** button is desensitized.

If it's necessary to change the contract after the initial agreement, simply edit the :term:`event`, make the 
needed changes (e.g., add *premiumpromotion*), and change the :term:`state` to *tentative*. By changing the 
:term:`state`, the **Update and Send Contract** button will be sensitized, and can be clicked to send another
contract.

Note once this is done, the system voids previous contract and it is not accessible.


.. _exception-required:

When an Exception to Standard Availability Rules is Needed
----------------------------------------------------------------

Normally, events are allowed on weekends and not allowed on weekdays. There are some holidays during the week when
we want to allow events, and some weekend days we don't want to allow events. For these, we need to configure
:term:`exceptions <exception>`.

To create exceptions, use the :ref:`event-exceptions-view`.