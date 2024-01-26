// set editor form width
$.extend( $.fn.DataTable.Editor.display.jqueryui.modalOptions, {
    width: 'auto',
    // minWidth: 600,  // this doesn't seem to do anything. use .ui-dialog{min-width:600px} in style.css
} );

// configure table buttons
function event_configuretablebuttons( table ) {
    btn = table.button( 'calendar:name' );
    btn.action( function( object, dtapi, button, cnf ){ 
        window.location.href = cnf.url; 
    } );
}

// only define afterdatatables if needed
if ( ['/admin/events'].includes(location.pathname) ) {
// set up buttons for edit form after datatables has been initialized
function afterdatatables() {
    event_configuretablebuttons( _dt_table );

    // needs to be same in admin_eventscalendar.js
    event_setopentrigger( editor );

    // set up dependent field(s)
    event_setdependent ( editor );

    // special action for events view only
    editor.on('open', function( e, mode, action ) {
        // force services class initial setup
        editor.field( 'services.id' ).set( editor.field( 'services.id' ).get() );
        
        return true;
    });

    // set the triggers which case the form buttons to change
    event_settriggers( editor );

    // prevent field focus issue. see https://stackoverflow.com/a/16126064/799921
    $.ui.dialog.prototype._focusTabbable = $.noop;
}
} // if [].includes(location.pathname)

