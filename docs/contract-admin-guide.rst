===========================================
Administrator's Guide
===========================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

The current method of tracking race support business involves
maintenance of a Google Sheet (tab per year, row per weekend date). The
columns track all of the information required to generate the contract,
along with additional information for tracking when the invoice and
contract are sent, and when the payment and signed contract are
received. When the treasurer fills in all the fields required to go to
contract, a volunteer downloads the sheet and generates a Word file via
mail merge (saved as pdf). The treasurer emails the contract to the
client race director. The race director must sign the contract and
either scan/email or return via US Mail.

Enter **contractility**.

This tool will automate much of the contract management flow. The
requirements for the tool are captured in `Race Support Contract
Management
Requirements <https://docs.google.com/document/d/1WH2uHDB06FFOISQa5W9lNAxFINLMT44cMLdPIk848WE/edit?usp=sharing>`__.

Tool’s Primary Goals: Reduce the volunteer labor associated with
managing our race support business.

a) generate and track contracts with our race support clients. Reduce the processing related to signing contracts for both FSRC volunteer and race director. (Priority 1)

b) Make it easier to manage the data associated with our race support business with less manual manipulation of spreadsheets. (Priority 2)

c) Provide an availability calendar to aid race directors in selecting race dates. (Priority 2)

d) Automate status emails to race directors (Priority 2)

Tool’s secondary goal: support other agreements between FSRC and clients, e.g., for race sponsorship.

This document shows the race services contract flow.

To read this document, start at `Event Overview view <#use-cases-what-to-do...>`__ to see the admin’s process flow, and
`User Calendar view <#_fbv50flijk8q>`__ to see the users’ process flow. Follow the flow using the links provided.

In addition to the admin and user process flows mentioned above, there
are some automated processes:

-  Before the race an automated email is generated. See `Pre Race Coordination email <#pre-race-coordination-email>`__ for details.

-  After the race there are some actions which take place. See `Post Race Processing <#post-race-processing>`__ for details.

**Notes**

-  in this document the terms “contract” and “agreement” are used interchangeably.

Use Cases (What To Do...)
=========================

When We Learn About a New Race
------------------------------

Race has Finish Line Services
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Race has Only Premium Promotion
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When Race Details are Confirmed by Race Director
------------------------------------------------

When Race Director Accepts Agreement
------------------------------------

.. _section-1:

Event Overview view
===================

The main administrative interface is a table of all the races in the
database. The admin can create a new race, or select a race for Edit,
Notes, Delete or Renew operations.

Notice the State column. The State can be updated automatically by the
tool or the admin can update it through the administrative interface.
This can have one of the following values

-  Pending - race was copied automatically to the next year (“renewed”) during `Post Race Processing <#post-race-processing>`__ or by clicking Renew button. The admin is expected to confirm with race director that the race will happen and that the date and other race details are correct. This is set automatically through `Post Race Processing <#post-race-processing>`__ or after clicking Renew.

-  Tentative - race director has confirmed race will be run again this year, but is not ready to receive the contract. This is set by the admin.

-  Contract Sent - race director has confirmed the date. Admin has sent contract to race director. This is set automatically.

-  Committed - race director has signed contract (electronically). This is set automatically.

-  Blocked - race date is blocked because of FSRC constraints. This is set by the admin.

Clicking the buttons will take you to specific views or perform some
action.

-  New - takes you to `Create Race view <#admin-calendar-view>`__

-  Edit (requires single selection) - takes you to `Edit Race view <#edit-race-view>`__

-  Notes (requires single selection) - takes you to `Edit Notes view <#edit-notes-view>`__

-  Delete (requires single selection) - shows popup “are you sure”, and if click OK deletes race. Actually race is marked as “deleted” and can be recovered if desired [beyond scope of this document]

-  Renew (requires selection of one or more races) - shows popup “are you sure”, and if click OK renews selected races.

This isn’t shown, but there will also be a way to filter the table
display down to only show the events which are in a particular State.
This is useful to look for committed races, tentative races, etc.

The transition from Pending to Tentative is done by the admin using the
`Create Race view <#admin-calendar-view>`__ or `Edit Race
view <#edit-race-view>`__. This is optional, but could be useful if the
admin wants to remember which races have had some discussion with the
race director.

.. _section-2:

Admin Calendar view
===================

TBA

.. _section-3:

Create Race view
================

The Create Race view is one way a race entry is created in the tool.
Generally this is used when a request is received for a new race. See
`Post Race Processing <#_za1n0r81lz8r>`__ for details on how existing
races are automatically “renewed” for the following year.

===================== ============================================================
    **Create new entry** 
----------------------------------------------------------------------------------
===================== ============================================================
Date \*:             
Event \*:            
State \*:             (Pending, Tentative, Contract Sent, Committed, Blocked)
Event link:          
FSRC Lead:            (select list of finish line leaders)
Distance:            
Start time:          
Course:              
Standard Course:      (select Y or N)
Organization:        
Organization link:   
Contact First Name:  
Contact Last Name:   
Contact email:       
Registration link:   
Services:             (one or more of finishline, coursemarking, premiumpromotion)
Prev Year #Finishers: (a number, or NEW if new race, or blank if unknown)
Notes:               
===================== ============================================================

After Create button is submitted, `Event Overview
view <#use-cases-what-to-do...>`__ is displayed

Note admin can set state to “Blocked” if FSRC wants to show the date
isn’t available but there are no races scheduled

Edit Race view
==============

The Edit Race view can be used to update the specifics about the race,
and to generate a contract.

===================== ============================================================
**Edit entry**       
----------------------------------------------------------------------------------
===================== ============================================================
Date \*:             
Event \*:            
State \* :            (Pending, Tentative, Contract Sent, Committed, Blocked)
Event link:          
FSRC Lead:            (select list of finish line leaders)
Distance:            
Start time:          
Course:              
Standard Course:      (select Y or N)
Organization:        
Organization link:   
Contact First Name:  
Contact Last Name:   
Contact email:        referred to as “race director email” in this document
Registration link:   
Services:             (one or more of finishline, coursemarking, premiumpromotion)
Prev Year #Finishers: (a number, or NEW if new race, or blank if unknown)
Notes:               
===================== ============================================================

After Save or Save and Generate Contract buttons, `Event Overview
view <#use-cases-what-to-do...>`__ is displayed to admin.

After Save and Generate Contract button is submitted, `Contract
Email <#contract-email>`__ is sent to race director (Contact email),
treasurer, raceservices. The event state is automatically moved to
Contract Sent.

Resend Contract is only active if contact has been sent. If in Contract
Sent state `Contract email <#contract-email>`__ will be resent. If in
Committed state `Agreement Accepted email <#agreement-accepted-email>`__
will be resent.

Edit Notes view
===============

The Edit Notes view can be used to update the specifics about the race,
and to generate a contract.

============== ====================
**Edit entry**
============== ====================
Date:          read only date
Event:         read only event name
Notes:        
============== ====================

After Save button is submitted, `Event Overview
view <#use-cases-what-to-do...>`__ is displayed to admin.

.. _section-4:

Contract email
==============

The contract email is sent to give the race director access to the
agreement. The race director may view the agreement, download the
agreement and accept the agreement directly from this email.

When the Save and Send Contract button is clicked, this email will come
up in a gmail compose window to allow it to be tailored by the admin
before sending. [TBD whether this is possible]

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

   Mark Lawrence

   Race Support Chair, Frederick Steeplechasers Running Club

When race director clicks ACCEPT AGREEMENT, the link takes them to the
`Accept Agreement view <#accept-agreement-view>`__.

Accept Agreement view
=====================

The Accept Agreement view is used to capture the race director’s consent
to the Race Support Agreement.

+---------------------------+-------------------------------------------------------------------+
| **Accept Agreement**                                                                          |
+---------------------------+-------------------------------------------------------------------+
| Please view or download agreement between Frederick Steeplechasers Running Club and           |
|                                                                                               |
| -  `view agreement <#agreement>`__                                                            |
| -  `download agreement <#agreement>`__                                                        |
|                                                                                               |                    
| To confirm your date and lock it in on the FSRC schedule, fill in your name and email         |
+---------------------------+-------------------------------------------------------------------+
| Notes:                    |                                                                   |                      
+---------------------------+-------------------------------------------------------------------+
| Name:                     |                                                                   |                      
+---------------------------+-------------------------------------------------------------------+
| Email:                    |                                                                   |
+---------------------------+-------------------------------------------------------------------+

The race director is given the option to view or download the agreement
using links in the form.

When the YES, I AGREE button is clicked, the event state moves to
Committed.

-  The `Agreement Accepted email <#agreement-accepted-email>`__ is sent capturing the commitment

-  The `Agreement Accepted view <#agreement-accepted-view>`__ is displayed

Agreement Accepted view
=======================

The Agreement Accepted view is displayed when the race director agrees
to the Race Support Agreement.

   Thank you for contracting with FSRC for race support services for
   <Event> on <Date>.

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
   should include a statement in your waiver as follows, “I understand
   that I may receive emails about this race and other races promoted by
   the Frederick Steeplechasers Running Club.”

   [end premiumpromotion]

   If you have any questions or changes, please contact
   raceservices@steeplechasers.org.

Agreement Accepted email
========================

The Agreement Accepted email is sent when the race director accepts the
agreement. This contains the same information as was displayed in the
browser view after accepting.

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

   Mark Lawrence

   Race Support Chair, Frederick Steeplechasers Running Club

Pre Race Coordination email
===========================

Before the race, an email is sent to to assure proper coordination.

If the race contracted for finishline and/or for coursemarking, 5 days
prior to the race, Pre Race Coordination email is sent.

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

   Please take the time to review the `agreement <#agreement>`__ and let
   us know as soon as possible if anything has changed, at
   raceservices@steeplechasers.org.

   thanks,

   Mark Lawrence

   Race Support Chair, Frederick Steeplechasers Running Club

Post Race Processing
====================

After the race, a couple of automated tasks take place. This processing
happens [5?] days after the event.

-  Event is automatically “renewed” meaning a Pending event is created
      the following year, on the same date. In this case, “same date”
      means the Nth day of week in the month, e.g., if the race was the
      3rd Saturday this year, it will be “penciled in” for the 3rd
      Saturday next year

-  a `Post Race email <#post-race-email>`__ is sent to thank the race
      director for the opportunity to provide our services, to let them
      know they’ve been penciled in for the following year, and to ask
      them to complete a short survey on how well we did

Post Race email
===============

The Post Race email is sent several days after the event completes. This
email is tailored based on the contracted services and solicits input
through a post race survey.

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

   Mark Lawrence

   Race Support Chair, Frederick Steeplechasers Running Club

User Calendar View
==================

The race directors and admins can get an overview of date availability
using the User Calendar view.

================= === === === === === ==========================
Sun               Mon Tue Wed Thu Fri Sat
================= === === === === === ==========================
29                30  1   2   3   4   5
                                     
                                      Blocked
6                 7   8   9   10  11  12
                                     
                                      Johnny’s Shuffle
13                14  15  16  17  18  19
                                     
Furry and Fast 5K                    
20                21  22  23  24  25  26
                                     
                                      Tentative - please inquire
27                28  29  30  31  1   2
                                     
                                      Tentative - please inquire
================= === === === === === ==========================

Clicking Request Race Services takes the race director to the `Race
Services Request view <#race-services-request-view>`__.

If an admin is logged in and viewing this page, clicking on a day will
bring up the `Create Race view <#admin-calendar-view>`__ or `Edit Race
view <#edit-race-view>`__ as appropriate.

Race Services Request view
==========================

The Race Services Request view is used by the race director to request
race services. This form generates an email to
raceservices@steeplechasers.org.

+-----------------------------------+--------------------------------------------------------------+
| **Race Services Request**                                                                        |
+-----------------------------------+--------------------------------------------------------------+
| Race directors who want to request a reservation with our race support services team, who want   |
| to sign up for premium promotion, or who want more information should fill out as much of this   |
| form as possible.                                                                                |
|                                                                                                  |
| We will use ‘contact email’ to get back to you as soon as possible, normally within two business |
| days.                                                                                            |
|                                                                                                  |
| Fields marked with a \* are required                                                             |
+-----------------------------------+--------------------------------------------------------------+
| Contact Name \*:                  |                                                              |
+-----------------------------------+--------------------------------------------------------------+
| Contact Email \*:                 |                                                              |
+-----------------------------------+--------------------------------------------------------------+
| Organization:                     |                                                              |
+-----------------------------------+--------------------------------------------------------------+
| Subject \*:                       | Request Details for Race, Request Information about          |
|                                   | Services,Other (please explain below)                        |
+-----------------------------------+--------------------------------------------------------------+
| Event Name:                       |                                                              |
+-----------------------------------+--------------------------------------------------------------+
| Event Date:                       |                                                              |
+-----------------------------------+--------------------------------------------------------------+
| Event Website:                    |                                                              |
+-----------------------------------+--------------------------------------------------------------+
| Distance:                         |                                                              |
+-----------------------------------+--------------------------------------------------------------+
| miles/km:                         | miles, km                                                    |
+-----------------------------------+--------------------------------------------------------------+
| - Check if this is a new race                                                                    |
+-----------------------------------+--------------------------------------------------------------+
| Expected Number of Finishers:     | less than 200, 201 - 300, 301- 400, 401 - 500                |
+-----------------------------------+--------------------------------------------------------------+
| - Finish Line and Timing                                                                         |
| - Course Marking                                                                                 |
| - Premium Promotion                                                                              |
+-----------------------------------+--------------------------------------------------------------+
| Your Comments or Questions:                                                                      |
+-----------------------------------+--------------------------------------------------------------+

Agreement
=========

The agreement will be similar to the following. When viewing, this will
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

-  | **Finish Line/Timing Services**
      | - Provide race bib numbers with pull-off tags to all
        participants with the name, age and gender of each participant
        recorded on the tags. The runners should be instructed to pin
        the race bib (with the pull-tag in place) on the front where it
        can be clearly seen by the finish line personnel

-  **Standard Promotion**: Add your race to the FSRC website event
      calendar (if not already present):
      https://steeplechasers.org/events/community/add

-  **Premium Promotion:** Provide spreadsheet file of your participants'
      email addresses from the previous year (if available) , and then
      provide the current list at the conclusion of the race. Please
      include a statement in your race waiver as follows: I understand
      that I may receive emails about this race and other races promoted
      by the Frederick Steeplechasers Running Club.

-  **Course Support:** Aid stations and Course Marshals at key locations
      along the route are recommended and are the responsibility of the
      race organizers.

FSRC is responsible for:

-  | **Finish Line/Timing Services**
      | - Transport, setup and operation of FSRC equipment (Display
        Clock, Time Machine Race Timer, Finish Line Chute, flags,
        signage and related materials)
      | - Timing and scoring, including generation of a list of award
        winners, posting of ordered bib pull-tags with finish times at
        the race site, and delivery of bib pull-tags at the conclusion
        of the event. Note: FSRC does not tally final race results
        beyond the award winners. Race Directors are expected to use the
        delivered bib pull-tags to generate race results.

-  | **Course Marking**
      | - The race course will be marked with cones, directional signage
        and mile markers

-  | **Premium Promotion**
      | - Your race will be included in twice-monthly email blasts to
        the FSRC-maintained list of area race participants, starting
        three months prior to your race date.

-  **Results**: Your race results will be published on the FSRC website,
      if desired. Email results to results@steeplechasers.org. Suggested
      format can be found on the `Race Support
      Services <https://steeplechasers.org/race-support-services/>`__
      page of the FSRC website.

FSRC finish line, timing and course marking services apply only to the
competitive portion of the event. Walks or “fun runs” associated with
the event are not part of this agreement and are the sole responsibility
of the event organizer.

Thanks

Mark Lawrence, Race Support Chair, Frederick Steeplechasers Running Club

240-285-4703

mark.lawrence@steeplechasers.org
