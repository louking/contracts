$( function() {
  $('#calendar').fullCalendar({
    defaultView: 'month',
    themeSystem: 'jquery-ui',
    contentHeight: 'auto',

    customButtons: {
      servicesQuery: {
        text: 'Request Race Services',
        click: function() {
          window.location.href = servicesqueryurl;
        }
      }
    },

    header: {
      left: 'prev,next today prevYear,nextYear',
      center: 'title',
      right: 'servicesQuery'
    },
    // aspectRatio: 2,
    height: 450,

    eventSources: [
      {
        url: '/eventsapi',
      }
    ],

    // see https://stackoverflow.com/questions/49301290/jquery-fullcalendar-prepend-characters-to-title-output
    eventDataTransform: function( event ) {
      // we don't display the name for non-committed events
      if (event.state != 'committed') {
        event.title = 'Tentative - please inquire';
        // see https://stackoverflow.com/questions/26681896/fullcalendar-event-cell-background-color
      }
      
      // make into all day event for frontend display purposes
      event.allDay = true;

      return event;
    },

    eventRender: function (event, element) {
      var dataToFind = moment(event.start).format('YYYY-MM-DD');
      if (event.state == 'committed') {
        $("td[data-date='"+dataToFind+"']").addClass('contracts-committed');
      } else {
        $("td[data-date='"+dataToFind+"']").addClass('contracts-tentative');
      }
    },

  })
})
  
