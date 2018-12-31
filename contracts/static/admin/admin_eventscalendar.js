var editor;

$( function() {
  if ( location.pathname != '/admin/calendar' ) return;

  editor = new $.fn.dataTable.Editor ( edoptions );

  function refresh_events() {
    $("td").removeClass('contracts-committed contracts-tentative contracts-available contracts-unavailable');
    $('#calendar').fullCalendar( 'refetchEvents' );
  };

  editor.on( 'submitSuccess', refresh_events);

  // needs to be same in events.js
  editor.on('open', function( e, mode, action ) {
      // set up the buttons
      configureformbuttons( this, action );

      // special processing for contractApproverNotes field to make readonly
      editor.field( 'contractApproverNotes' ).disable();

      return true;
  });

  // prevent field focus issue. see https://stackoverflow.com/a/16126064/799921
  // note this affects subforms as well as event form
  $.ui.dialog.prototype._focusTabbable = $.noop;

  $('#calendar').fullCalendar({
    defaultView: 'month',
    themeSystem: 'jquery-ui',
    contentHeight: 'auto',

    // start week on Sunday
    firstDay: 0, 

    customButtons: {
      tableNav: {
        text: 'Table',
        click: function() {
          window.location.href = tableurl;
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
      left: 'prev,next today prevYear,nextYear tableNav',
      center: 'title',
      right: 'legend'
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
      // editor.field( 'race.id' ).focus();

      // set the triggers which case the form buttons to change
      event_settriggers( editor );

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

      // special processing for contractApproverNotes field to make readonly
      editor.field( 'contractApproverNotes' ).disable();

      // make sure focus is on race field
      // editor.field( 'race.id' ).focus();
        
      // set the triggers which case the form buttons to change
      event_settriggers( editor );

      // force services class initial setup
      editor.field( 'services.id' ).set( editor.field( 'services.id' ).get() );
      
    },  // eventClick: function() {

  })  // $('#calendar').fullCalendar(

  // refresh events every minute to keep calendar updated
  setInterval(refresh_events, 60*1000);

  // legend
  var day_legend = [
    {label:'Available', class:'contracts-available'},
    {label:'Committed', class:'contracts-committed'},
    {label:'Tentative', class:'contracts-tentative'},
    {label:'Unavailable', class:'contracts-unavailable'},
  ];

  var event_legend =[
    {label:'Committed - services', class:'contracts-event-blocked'},
    {label:'Committed - promotion', class:'contracts-event-unblocked'},
    {label:'Tentative', class:'contracts-event-uncommitted'},
    {label:'Canceled', class:'contracts-event-canceled'},
  ];

  create_legend_header('legend-table', 'Days');
  create_legend('legend-table', day_legend);
  create_legend_header('legend-table', 'Events');
  create_legend('legend-table', event_legend);

  $( '#legend' ).dialog({
    autoOpen: false
  }); // $( '#legend' ).dialog({})

})  // $(
  
