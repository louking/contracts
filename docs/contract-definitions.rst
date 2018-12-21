.. _glossary:

Definitions
===============

.. glossary::
    :sorted:

    client
        Name of the entity with whom the contract is being entered with. The contract is sent to the client 
        'Contact Email' for approval.

    course
        The course has an address where the finish line will be set up. Generally we work with loop courses, so
        this is the same as the starting line.

    date rule
        A rule which defines a date on which a :term:`race` or :term:`exception` is created. E.g., Third Sat Aug is
        a date rule.

    event
        :term:`Race` on a particular date. E.g., the event record saves information about the 9/14/2019 Market Street Mile 

    exception
        An exception to the normal rules for allowing races. Normally races are allowed on weekends and not allowed
        on weekdays. So the first Monday of September (Labor Day) is an example of an exception because we will 
        allow races on that day.

    lead
        the leader who will run the finish line operation on the day of the :term:`event`

    race
        A race can be run annually. The 'race' (e.g., Market Street Mile) has information which doesn't generally change, 
        e.g., it's run on the second Saturday of September. Compare to :term:`event` which is a race on a particular date.

    renew
        A :term:`race` is renewed a few days after the :term:`event` for the current year. The :term:`date rule` for the
        race is used to schedule the race for the following year.

    service
        - finishline - timing service done by the race services team
        - coursemarking - marking the course done by the race services team
        - premiumpromotion - advertisement for local races done by the communications team, sent periodically

    state
        - *renewed-pending* - race was copied automatically to the next year (“renewed”) during 
          :ref:`post-event-processing` or by clicking Renew button. The admin is expected to 
          confirm with race director that the :term:`event` will happen and that the date and other 
          :term:`event` details are correct. This is set automatically through :ref:`post-event-processing` or after clicking Renew.

        - *tentative* - race director has confirmed :term:`race` will be run again this year, but is not ready to receive 
          the contract. This is set by the admin.

        - *contract-sent* - race director has confirmed the date. Admin has sent contract to race director. This is 
          set automatically.

        - *committed* - race director has signed contract (electronically). This is set automatically.

        - *canceled* - :term:`event` has been canceled, but we don't want to lose track of it. E.g., if the race 
          owed or paid money it's better to change the state to canceled than to delete the :term:`event`.

        The transition from *renewed-pending* to *tentative* is done by the admin using the :ref:`create-event-view` 
        or :ref:`edit-event-view`. This should be used to help remember which races have
        had some discussion with the race director.
