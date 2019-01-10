===========================================
Administrator's Reference
===========================================

.. toctree::
   :maxdepth: 3
   :caption: Contents:

This page has views and emails used by the administrator. Note some of the views may not be visible
to you, depending on your privilege setting.


.. _admin-calendar-view:

Admin Calendar view
===================

The main administrative interface is a calendar of the :term:`events <event>` in the
database. The admininistrator can create a new :term:`event`, or select an :term:`event` for 
Edit, or Delete operations.

To create a new :term:`event`, click on a date. To edit an :term:`event`, click on the event.

.. image:: images/admin-calendar.*

The colors for the days and events help the administrator understand the state of the :term:`event`, 
whether finish line :term:`services <service>` are required, or if this :term:`event` just has 
premium promotion :term:`service`.

.. image:: images/admin-calendar-legend.*
   :align: center


.. _event-overview-view:

Event Overview view
===================

While the :ref:`admin-calendar-view` may be the easiest way to view all the :term:`events <event>`,
this view  provides a table  of all the events in the database which can be used as well. The admin
can create a new :term:`event`, or  select an :term:`event` for Edit, Notes, or Delete 
operations.

Notice the :term:`State` column. The :term:`State` may be updated automatically by the tool or the
admin can update it through the administrative interface. See :term:`state` for a description of the
states and whether they are set by the tool or by the administrator.

Clicking the buttons at the top will take you to specific views or perform some
action.

   :New: takes you to :ref:`create-event-view`

   :Edit: (requires single selection) takes you to :ref:`edit-event-view`

   :CSV: download a csv file of the currently filtered events. **Note** only the displayed events will be downloaded, 
      so if there are multiple pages of events, some may be missing.

   :Notes: (requires single selection) takes you to :ref:`edit-notes-view`

   :Delete: (requires single selection) shows popup “are you sure”, and if you click OK delete the :term:`event`

      **Note:** if you don't want the event deleted because (e.g., the race owes or paid money we want to 
      track), change the :term:`state` to *canceled*

   :Calendar: switch to the :ref:`admin-calendar-view`

The top row of controls provides a way to filter the table display down to only show the events
which are in a particular :term:`State`, within a Date Range, or which has contracted for specific
:term:`Services <service>`.

.. image:: images/event-overview.*


.. _create-event-view:

Create Event view
=================

The Create Event view is one way a race entry is created in the tool. Generally this is used when a
request is received for a new race. See  :ref:`post-event-processing` for details on how existing
races are automatically “renewed” for the following year.

Notice the :term:`State` field. The :term:`State` may be updated automatically by the tool or the
admin can update it through the administrative interface. See :term:`state` for a description of the
states and whether they are set by the tool or by the administrator.

When selecting **Race**, **Course**, or **Client**, a search box is displayed. You can start typing
to find these items if they were previously stored. If a new :term:`race`, :term:`course`, or 
:term:`client` is needed, click on the *<new>* entry and the :ref:`create-race-view`, :ref:`create-course-view`,
or :ref:`create-client-view`, respectively, will be displayed so the item can be created.

.. image:: images/create-event-view.*


.. _create-race-view:

Create Race view
==================

.. image:: images/create-race-view.*


.. _create-course-view:

Create Course view
===================

.. image:: images/create-course-view.*


.. _create-client-view:

Create Client view
======================

.. image:: images/create-client-view.*


.. _edit-event-view:

Edit Event view
=================

The Edit Event view can be used to update the specifics about the race,
and to generate a contract.

Click **Update** to update any changed fields in the :term:`event`.

Click **Update and Send Contract** button to generate the contract and send the :ref:`contract-email` 
to the race director (Contact email), treasurer, and raceservices. The event state 
is automatically set to *contract-sent*.

The **Resend Contract** button is only active if contact has been sent. If in *contract-sent* :term:`state`
:ref:`contract-email` will be resent. If in *committed* :term:`state`, :ref:`agreement-accepted-email`
will be resent.

If the :term:`event` needs to be deleted, click **Delete**. You will be asked for confirmation before the 
:term:`event` is deleted. Note another option is to change the :term:`event` :term:`state` to *canceled*.

.. image:: images/edit-event-view.*


.. _contract-email:

Contract email
==============

The contract email is sent to give the race director access to the
agreement. The race director may view the agreement, download the
agreement and accept the agreement directly from this email.

When the **Update and Send Contract** button is clicked from the :ref:`edit-event-view`, 
this email will be generated automatically.

The email will be something like the following. Note this is configured in the system
and can be changed by a superadmin.

   To: <Contact email>

   From: raceservices@steeplechasers.org

   Cc: raceservices@steeplechasers.org, treasurer@steeplechasers.org

   Subject: FSRC Race Support Agreement: <Event> - <Date>

   Hi <Contact First Name>,

   To confirm your date and lock it in on the FSRC schedule, you need to
   accept the Race Support Agreement.

   Click to `view <#agreement>`__ or `download <#agreement>`__ your Race
   Support Agreement for <Event> on <Date>. If you need any changes
   please reply to this email. If everything looks OK, please click the
   ACCEPT AGREEMENT button and follow the directions.

   Your invoice should arrive soon after you accept the agreement, but
   the payment isn’t due until a few days before the race.

   In order to get your listing on our `website
   calendar <https://steeplechasers.org/events/>`__, we provide the
   ability for the race director to manage the listing. That way, you
   can customize it as you see fit. The link to get started is:
   https://steeplechasers.org/events/community/add.

   [if premiumpromotion]

   We'll add the race to our email promotion around <Date minus 3
   months>. Please send along this year's artwork and registration link
   when you have it.

   [end if premiumpromotion]

   thanks,

When race director clicks ACCEPT AGREEMENT, the link takes them to the
:ref:`accept-agreement-view`.


.. _agreement-accepted-email:

Agreement Accepted email
========================

The Agreement Accepted email is sent when the race director accepts the
agreement. This contains the same information as was displayed in the
browser view after accepting.

The email will be something like the following. Note this is configured in the system
and can be changed by a superadmin.

   To: <Contact email>

   From: raceservices@steeplechasers.org

   Cc: raceservices@steeplechasers.org, treasurer@steeplechasers.org

   Subject: ACCEPTED - FSRC Race Support Agreement - <Event> <Date>

   Hi <Contact First Name>,

   Thank you for contracting with FSRC for race support services for
   <Event> on <Date>.

   [if customernotes]

   The following notes were captured when you signed your agreement.

   [customernotes]

   [end customernotes]

   [if finishline or coursemarking]

   You will be hearing from us about five days prior to your event for
   final coordination on our finish line services.

   [end finishline or coursemarking]

   [if premiumpromotion]

   Please watch for your premium promotion to start about three months
   prior to your event. To receive these, please subscribe to our
   mailings at http://eepurl.com/bMW_Wf, and be sure to check the
   Frederick Area Featured Races option.

   After your race, please send email addresses of your participants to
   communications@steeplechasers.org. These folks will be included in
   our mailings about Frederick area local races. As a reminder, you
   have agreed to include a statement in your waiver as follows, “I
   understand that I may receive emails about this race and other races
   promoted by the Frederick Steeplechasers Running Club.”

   [end premiumpromotion]

   If you have any questions or changes, please contact
   raceservices@steeplechasers.org.

   thanks,


.. _pre-event-coordination-email:

Pre Event Coordination email
==============================

Before the :term:`event`, an email is sent to to assure proper coordination.

If the race director contracted for finishline and/or for coursemarking, [5 days]
prior to the race, the Pre Event Coordination email is sent.

The email will be something like the following. Note this is configured in the system
and can be changed by a superadmin.

   To: <Contact email>

   From: raceservices@steeplechasers.org

   Cc: raceservices@steeplechasers.org, treasurer@steeplechasers.org,
   <FSRC Lead email>

   Subject: Coordination with FSRC for <Event> on <Date>

   Hi <Contact First Name>,

   Note this is an automated email, so it’s possible you have already
   coordinated on this. If so, please ignore.

   <Event> is coming up on <Date> and we wanted to make sure we have all
   our ducks in a row.

   <FSRC Lead> will be managing your race on race day, and can be
   contacted at <FSRC Lead email> <FSRC Lead phone number>.

   Please let us know how many runners you expect, so that we can make
   sure we have the right number of volunteers to support the race. This
   should be sent as a reply/all to this email.

   [if not coursemarking]

   We plan to be there 30 minutes prior to your start time of <Start
   time> to get the finish line set up.

   [end not coursemarking]

   [if coursemarking]

   We plan to be there 90 minutes prior to your start time of <Start
   time> to get the course marked. Some folks will be arriving 30
   minutes prior to your start time to get the finish line set up.

   [end coursemarking]

   Please take the time to review the :ref:`agreement` and let
   us know as soon as possible if anything has changed, at
   raceservices@steeplechasers.org.

   thanks,


.. _post-event-processing:

Post Event Processing
=======================

After the :term:`event`, a couple of automated tasks take place. This processing
happens [5 days] after the event.

-  :term:`Race` is automatically “renewed” meaning a *renewed-pending* :term:`event` is created
   the following year, on the same date, depending on the date rule specified for this
   race. See :ref:`date-rules` for more information.

   **Note** if the date rule for the :term:`race` is not set, the system creates
   one automatically, based on nth day of week in month.

-  a :ref:`post-event-email` is sent to thank the race
   director for the opportunity to provide our services, to let them
   know they’ve been penciled in for the following year, and to ask
   them to complete a short survey on how well we did


.. _post-event-email:

Post Event email
=================

The Post Event email is sent several days after the event completes. This
email is tailored based on the contracted services and solicits input
through a post event survey.

The email will be something like the following. Note this is configured in the system
and can be changed by a superadmin.

   To: <Contact email>

   From: raceservices@steeplechasers.org

   Cc: raceservices@steeplechasers.org, treasurer@steeplechasers.org

   Subject: Thank You for using FSRC Race Support Services - <Event>
   <Date>

   Hi <Contact First Name>,

   Thank you so much for using FSRC for race support services for
   <Event> on <Date>.

   If you’d like FSRC to post your results to the
   `Results <http://steeplechasers.org/competition/current-results/>`__
   page of our website, please send these to results@steeplechasers.org.
   We recommend that you use our `race results
   template <http://steeplechasers.org/wp-content/uploads/2014/12/raceresultstemplate.xls>`__
   for formatting your results file.

   We have penciled you in for next year on <“renew” Date>. Please let
   us know as soon as possible if you can confirm you’ll be staging your
   event again next year, or if you’re sure you won’t be.

   And we’d love to hear how well you think we performed. Please take a
   very short survey at <survey link>.

   [if premiumpromotion]

   Please don’t forget to send email addresses of your participants to
   communication@steeplechasers.org. These folks will be included in our
   mailings about Frederick area local races.

   [end premiumpromotion]

   thanks,


.. _agreement:

Agreement
=========

The agreement will be similar to the following. Note this is configured in the system and can be changed by a superadmin.

When viewing, this will
be a google doc published view, and when downloading this will be a pdf
document.

    January 30, 2018

    <Contact first name> <Contact last name>

    <Event>

    Dear <Contact first name>:

    You have requested race support services from Frederick Steeplechasers
    Running Club for your event. This is to confirm that we have scheduled
    the race support services as detailed on the following agreement.

    Your organization is responsible for the following:

    - **Finish Line/Timing Services** - Provide race bib numbers with pull-off tags to all
      participants with the name, age and gender of each participant
      recorded on the tags. The runners should be instructed to pin
      the race bib (with the pull-tag in place) on the front where it
      can be clearly seen by the finish line personnel

    - **Standard Promotion**: Add your race to the FSRC website event
      calendar (if not already present):
      https://steeplechasers.org/events/community/add

    - **Premium Promotion:** Provide spreadsheet file of your participants'
      email addresses from the previous year (if available) , and then
      provide the current list at the conclusion of the race. Please
      include a statement in your race waiver as follows: I understand
      that I may receive emails about this race and other races promoted
      by the Frederick Steeplechasers Running Club.

    - **Course Support:** Aid stations and Course Marshals at key locations
      along the route are recommended and are the responsibility of the
      race organizers.

    FSRC is responsible for:

    - **Finish Line/Timing Services**

      - Transport, setup and operation of FSRC equipment (Display
        Clock, Time Machine Race Timer, Finish Line Chute, flags,
        signage and related materials)
      - Timing and scoring, including generation of a list of award
        winners, posting of ordered bib pull-tags with finish times at
        the race site, and delivery of bib pull-tags at the conclusion
        of the event. Note: FSRC does not tally final race results
        beyond the award winners. Race Directors are expected to use the
        delivered bib pull-tags to generate race results.

    - **Course Marking**

      - The race course will be marked with cones, directional signage
        and mile markers

    - **Premium Promotion**

      - Your race will be included in twice-monthly email blasts to
        the FSRC-maintained list of area race participants, starting
        three months prior to your race date.

    - **Results**: Your race results will be published on the FSRC website,
      if desired. Email results to results@steeplechasers.org. Suggested
      format can be found on the `Race Support
      Services <https://steeplechasers.org/race-support-services/>`__
      page of the FSRC website.

    FSRC finish line, timing and course marking services apply only to the
    competitive portion of the event. Walks or “fun runs” associated with
    the event are not part of this agreement and are the sole responsibility
    of the event organizer.

    Thanks


.. _date-rules:

Date Rules view
================

TBA

In this case, “same date” means the Nth day of week in the month, e.g., if the race was the
3rd Saturday this year, it will be “penciled in” for the 3rd Saturday next year. 