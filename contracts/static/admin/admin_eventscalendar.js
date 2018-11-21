var editor;

$( function() {
  if ( location.pathname != '/admin/calendar' ) return;

  $.getJSON( {
      url: saformurl, 
      success: function(data, textStatus, jqXHR) {
        var edoptions = data.edoptions;
        editor = new $.fn.dataTable.Editor ( edoptions );

        editor.on( 'submitSuccess', function() {
          $("td").removeClass('contracts-committed contracts-tentative contracts-available contracts-unavailable');
          $('#calendar').fullCalendar( 'refetchEvents' );
        });
    } // success: function() {
  }); // $.getJSON(

  $('#calendar').fullCalendar({
    defaultView: 'month',
    themeSystem: 'jquery-ui',
    contentHeight: 'auto',

    customButtons: {
      tableNav: {
        text: 'Table',
        click: function() {
          window.location.href = tableurl;
        }
      }
    },

    header: {
      left: 'prev,next today prevYear,nextYear tableNav',
      center: 'title',
      right: ''
    },
    // aspectRatio: 2,
    height: 450,

    eventSources: [
      { url: '/admin/eventsapi' },
      { url: '/admin/eventexceptionsapi' },
    ],

    // see https://stackoverflow.com/questions/49301290/jquery-fullcalendar-prepend-characters-to-title-output
    eventDataTransform: function( event ) {
      // make into all day event for display purposes
      // event.allDay = true;
      // noop

      return event;
    },  // eventDataTransform: function() {

    eventRender: function( event, element ) {
      var dataToFind = moment(event.start).format('YYYY-MM-DD');

      // rendering just sets the class for the date
      // note actual event rendering class needs to be after exception rendering 
      // class in the css file to take precedence

      // for actual events
      if (event.hasOwnProperty('state')) {
        if (event.hasOwnProperty('blocked') && event.blocked) {
          if (event.state == 'committed') {
            $("td[data-date='"+dataToFind+"']").addClass('contracts-committed');
          } else {
            $("td[data-date='"+dataToFind+"']").addClass('contracts-tentative');
          }
        }

      // for exceptions
      } else if (event.hasOwnProperty('exception')) {
        if (event.exception == 'available') {
          $("td[data-date='"+dataToFind+"']").addClass('contracts-available');
          // event itself isn't rendered for availabile exception
        } else {
          $("td[data-date='"+dataToFind+"']").addClass('contracts-unavailable');
          // event itself isn't rendered for unavailable exception
        }

      }
    },  // eventRender: function() {

    dayClick: function( date, jsEvent, view ) {
      editor.title('Create new entry').buttons('Create').create();
      configureformbuttons( editor, 'create' );
      editor.set( 'date', date.format() );

    },  // dayClick: function() {

    eventClick: function( event, jsEvent, view ) {
      // noop for now for exceptions
      if ( event.hasOwnProperty( 'exception' ) ) return;

      // event_cleartriggers( editor );
      editor.title('Edit entry').buttons('Update').edit( event.data.rowid );
      $.each( editor.order(), function( i, field ) {
        editor.set( field, _.get(event.data, field ) );
      })
      configureformbuttons( editor, 'edit' );
      event_settriggers( editor );

    },  // eventClick: function() {

  })  // $('#calendar').fullCalendar(

})  // $(
  
