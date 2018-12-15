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
      },
      legend: {
        text: 'Legend',
        click: function () {
          $( '#legend' ).dialog( 'open' );
        }
      },
    },

    header: {
      left: 'prev,next today prevYear,nextYear',
      center: 'title',
      right: 'servicesQuery legend'
    },
    // aspectRatio: 2,
    height: 450,

    eventSources: [
      { url: '/eventsapi' },
      { url: '/eventexceptionsapi' },
    ],

    // see https://stackoverflow.com/questions/49301290/jquery-fullcalendar-prepend-characters-to-title-output
    eventDataTransform: function( event ) {
      // we don't display the name for non-committed events
      if (event.hasOwnProperty('state')) {
        if (event.state != 'committed') {
          event.title = 'Tentative - please inquire';
          // see https://stackoverflow.com/questions/26681896/fullcalendar-event-cell-background-color
        }
      }

      // make into all day event for frontend display purposes
      event.allDay = true;

      return event;
    },

    eventRender: function (event, element) {
      var dataToFind = moment(event.start).format('YYYY-MM-DD');

      // rendering just sets the class for the date
      // note actual event rendering class needs to be after exception rendering 
      // class in the css file to take precedence

      // for actual events
      if (event.hasOwnProperty('state')) {
        if (event.state == 'committed') {
          $("td[data-date='"+dataToFind+"']").addClass('contracts-committed');
        } else {
          $("td[data-date='"+dataToFind+"']").addClass('contracts-tentative');
        }

      // for exceptions
      } else if (event.hasOwnProperty('exception')) {
        if (event.exception == 'available') {
          $("td[data-date='"+dataToFind+"']").addClass('contracts-available');
          // event itself isn't rendered for availabile exception
          return false;
        } else {
          $("td[data-date='"+dataToFind+"']").addClass('contracts-unavailable');
          // event itself isn't rendered for unavailable exception
          return false;
        }

      }
    },

  })

  // legend
  var day_legend = [
    {label:'Available', class:'contracts-available'},
    {label:'Committed', class:'contracts-committed'},
    {label:'Tentative', class:'contracts-tentative'},
    {label:'Unavailable', class:'contracts-unavailable'},
  ];

  create_legend('legend-table', day_legend);

  $( '#legend' ).dialog({
    autoOpen: false
  }); // $( '#legend' ).dialog({})


})
  
