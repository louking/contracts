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

    event
        :term:`Race` on a particular date. E.g., the event record saves information about the 9/14/2019 Market Street Mile 

    lead
        the leader who will run the finish line operation on the day of the :term:`event`

    race
        A race can be run annually. The 'race' (e.g., Market Street Mile) has information which doesn't generally change, 
        e.g., it's run on the second Saturday of September. Compare to :term:`event` which is a race on a particular date.

    service
        - finishline - timing service done by the race services team
        - coursemarking - marking the course done by the race services team
        - premiumpromotion - advertisement for local races done by the communications team, sent periodically

    state
        - *pending* - race was copied automatically to the next year (“renewed”) during 
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

        The transition from *pending* to *tentative* is done by the admin using the :ref:`create-event-view` 
        or :ref:`edit-event-view`. This should be used to help remember which races have
        had some discussion with the race director.
