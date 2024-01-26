/**
 * dismiss form
 */
function dismiss_button() {
    this.close();
}

/**
 * submit form
 */
function submit_button() {
    this.submit();
}

/**
 * handle open for race registrations popup editor
 * 
 * @param {Editor} standalone editor 
 * @param {Buttons} buttons 
 */
function navraceregs_onopen(editor, buttons) {

}

/**
 * handle close for race registrations popup editor
 * 
 * @param {Editor} standalone editor 
 * @param {Buttons} buttons 
 */
function navraceregs_onclose(editor, buttons) {

}

$(function() {

    // special link processing for navigation
    $("a").click(function( event ){
        // use form to gather url arguments
        var raceregistration_opts = $(this).attr('raceregistrations_popup');
        if (raceregistration_opts) {
            event.preventDefault();
            var opts = JSON.parse(raceregistration_opts);

            // convert functions for buttons - see http://stackoverflow.com/questions/3946958/pass-function-in-json-and-execute
            // this assumes buttons is array of objects
            // TODO: handle full http://editor.datatables.net/reference/api/buttons() capability, i.e., string or single object
            for (i=0; i<opts.buttons.length; i++) {
                // note eval doesn't work on 'function() { ... }' so we leave out the function() and create it here
                if (opts.buttons[i].action) opts.buttons[i].action = new Function(opts.buttons[i].action);
            }

            var naveditor = new $.fn.dataTable.Editor ( opts.editoropts )
                .title( opts.title )
                .buttons( opts.buttons )
                .edit( null, false )
                .open();
            if (opts.onopen) {
                var navonopen = eval(opts.onopen)
                // note we just opened the standalone editor
                // the link click is the only way this editor can be opened
                navonopen(naveditor, opts.buttons);
            }
            // onclose should do any cleanup required
            if (opts.onclose) {
                var navonclose = eval(opts.onclose)
                naveditor.on('close', function(e, mode, action) {
                    navonclose(naveditor, opts.buttons);
                })
            }
        }
    });

});

// these functions are used by events.js and admin_eventscalendar.js

// current date for form
function currentdate() {
    var now = new Date()

    var day  = now.getDate().toString().padStart(2, '0');
    var mon  = (now.getMonth()+1).toString().padStart(2, '0');
    var year = now.getFullYear().toString();

    return year + '-' + mon + '-' + day;
}

// configure form buttons
function event_configureformbuttons( that, action ) {
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
        event_configureformbuttons( editor, editor.mode() );
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

/**
 * check current form date against daterule configured for the race that this
 * form references
 * 
 * @param {editor} editor - editor instance
 * @param {str} action - action being performed when the form was opened
 */
let check_date_in_progress = false;
function event_checkdate( editor, action ) {
    if (check_date_in_progress) return;
    check_date_in_progress = true;

    // Ajax request to check date
    let urlparams = setParams({
        date: editor.get('date'),
        race_id: editor.get('race.id')
    });
    $.ajax( {
        // application specific: my application has different urls for different methods
        url: `/admin/_checkdate?${urlparams}`,
        type: 'get',
        dataType: 'json',
        success: function ( json ) {
            // check success, if not successful display alert
            if (!json.success) {
                alert(json.cause);
            }
            check_date_in_progress = false;
        }
    } );
}

/**
 * common behavior when event form opened
 * 
 * @param {editor} editor - editor instance
 */
function event_setopentrigger( editor ) {
    editor.on('open', function( e, mode, action ) {
        // set up the buttons
        event_configureformbuttons( this, action );
  
        // special processing for contractApproverNotes field to make readonly
        editor.field( 'contractApproverNotes' ).disable();
  
        return true;
    });  
}

/**
 * set dependent fields 
 * 
 * @param {editor} editor - editor instance
 */
function event_setdependent( editor ) {
    editor.dependent( 'date', function( val, data, callback ) {
        event_checkdate( editor, editor.mode() );
        return {};
    });
}

/**
 * unset dependent fields 
 * 
 * @param {editor} editor - editor instance
 */
function event_unsetdependent( editor ) {
    editor.undependent( 'date' );
}