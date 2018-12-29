// set editor form width
$.extend( $.fn.DataTable.Editor.display.jqueryui.modalOptions, {
    width: 'auto',
    minWidth: 600,  // this doesn't seem to do anything. see crudapi.py for patch to handle subforms
} );

// current date for form
function currentdate() {
    var now = new Date()

    var day  = now.getDate().toString().padStart(2, '0');
    var mon  = (now.getMonth()+1).toString().padStart(2, '0');
    var year = now.getFullYear().toString();

    return year + '-' + mon + '-' + day;
}

// configure table buttons
function configuretablebuttons( table ) {
    btn = table.button( 'calendar:name' );
    btn.action( function( object, dtapi, button, cnf ){ 
        window.location.href = cnf.url; 
    } );
}

// configure form buttons
function configureformbuttons( that, action ) {
    // set buttons for create
    if ( action == 'create' ) {
        that.buttons( 'Create' );

    // set buttons for edit
    } else if ( action == 'edit' ) {
        // this can happen from the calendar view, we need to abort to avoid exception
        if ( that.field( 'state.id' ).inst('data').length == 0 ) return;

        // is current state selection in ['committed', 'contract-sent']?
        var contractsent = ['committed', 'contract-sent'].includes( that.field( 'state.id' ).inst('data')[0].text );
        that.buttons([
                {
                    text: 'Resend Contract',
                    className: ( that.field( 'contractDocId' ).get() ) ? 'enabled' : 'disabled',
                    action: function () {
                        if ( that.field( 'contractDocId' ).get() ) {
                            that.submit(null, null, function(data) {
                                data.addlaction = 'resendcontract';
                            });
                        }
                    }
                },
                {
                    text: 'Mark Invoice Sent',
                    className: ( that.field( 'invoiceSentDate' ).get() ) ? 'disabled' : 'enabled',
                    action: function () {
                        if ( ! that.field( 'invoiceSentDate' ).get() ) {                 
                            that.field( 'invoiceSentDate' ).set( currentdate() );
                            that.submit();
                        }                    
                    }
                },
                {
                    text: 'Update and Send Contract',
                    className: ( contractsent ) ? 'disabled' : 'enabled',
                    action: function () {
                        if ( ! contractsent ) {
                            that.submit(null, null, function(data) {
                                data.addlaction = 'sendcontract';
                            });
                        }
                    }
                },
                {
                    text: 'Update',
                    action: function () {
                        that.submit();
                    }
                },
                {
                    text: 'Delete',
                    action: function () {
                        that.close();
                        that.title( 'Delete' )
                            .buttons( 'Confirm Delete' )
                            .message( 'Are you sure you want to delete this event?' )
                            .remove( that.modifier() )
                    }
                },

            ]);

    // set buttons for remove (only other choice)
    } else {
        that.buttons( 'Delete' );
    }
}

// set up triggers for configuring event buttons
var event_trigger_fields = [ 'state.id', 'contractDocId', 'invoiceSentDate' ];
function event_settriggers( editor ) {
    // regenerate the edit buttons if certain fields change
    editor.dependent( event_trigger_fields, function( val, data, callback ) {
        configureformbuttons( editor, editor.mode() );
        return {};
    });

    // save services options
    var toclass = {};
    var classes = [];
    $.each(editor.field('services.id').inst().children(), function(i, thisval) {
        toclass[thisval.value] = 'service_' + thisval.text;
        classes.push( toclass[thisval.value] );
    });

    function set_services_class( val ) {
        // clear all the classes from the main form, then add what has been selected
        $( '#customForm' ).removeClass( classes.join(' ') );
        if (val != '') {
            values = val.split(', ');
            $.each(values, function(i, thisval) {
                $( '#customForm' ).addClass( toclass[thisval] );
            });
        };
        return {};
    };

    // set form class dependent on services
    editor.dependent( 'services.id', set_services_class);
}

function event_cleartriggers( editor ) {
    $.each( event_trigger_fields, function(i, field) {
        // $( editor.field( field ).input() ).off( 'change keyup' );
        editor.off( 'change keyup' );
    })
}

// only define afterdatatables if needed
if ( ['/admin/events'].includes(location.pathname) ) {
// set up buttons for edit form after datatables has been initialized
function afterdatatables() {
    configuretablebuttons( _dt_table );

    // needs to be same in admin_eventscalendar.js
    editor.on('open', function( e, mode, action ) {
        // set up the buttons
        configureformbuttons( this, action );

        // special processing for contractApproverNotes field to make readonly
        editor.field( 'contractApproverNotes' ).disable();

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


// TODO: below needs work -- make import scheme for events and clients tables

// set up tools button
function membertools( e, dt, node, config ) {
    toolsdialog = $( '#dialog-tools' ).dialog({
        title: 'Import Events',
        autoOpen: true,
        modal: true,
        minWidth: 475,
        position: { my: 'left top', at: 'center bottom', of: '.import-buttons' }
    });
}

function setmembertools() {
    $( '#widgets' ).append("\
            <div id='dialog-tools' style='display:none;'>\
                <div class='importfile'>\
                  <p>Import the event list from a CSV file. See <a href='/doc/importevents' target='_blank'>Import Guide</a> for information on the column headers and data format.</p>\
                  <form id='import-events' method='post' enctype='multipart/form-data'>\
                    <input id='choosefileImport' type=file name='file'>\
                    <button id='eventsImport' formaction='/_importevents'>Import</button>\
                  </form>\
                </div>\
            </div>\
            ")

    // handle Import button within Import dialog
    var $importevents = $('#eventsImport');
    $importevents.click( function( event ) {
        event.preventDefault();
        var url = $(this).attr('formaction')
        ajax_import_file(url, '#import-events', false);
        toolsdialog.dialog('close');
    });

    return membertools;
}
