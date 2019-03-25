// configure form buttons
function sponsor_configureformbuttons( that, action ) {
    // set buttons for create
    if ( action == 'create' ) {
        that.buttons( 'Create' );

    // set buttons for edit
    } else if ( action == 'edit' ) {
        // is current state selection in ['committed']?
        var contractsent = ['committed'].includes( that.field( 'state.id' ).inst('data')[0].text );
        that.buttons([
                {
                    text: 'Resend Agreement',
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
                    className: ( that.field( 'invoicesent' ).get() ) ? 'disabled' : 'enabled',
                    action: function () {
                        if ( ! that.field( 'invoicesent' ).get() ) {                 
                            that.field( 'invoicesent' ).set( currentdate() );
                            that.submit();
                        }                    
                    }
                },
                {
                    text: 'Update and Send Agreement',
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

// set up triggers for configuring sponsor buttons
var sponsor_trigger_fields = [ 'state.id', 'invoicesent' ];
function sponsor_settriggers( editor ) {
    // regenerate the edit buttons if certain fields change
    editor.dependent( sponsor_trigger_fields, function( val, data, callback ) {
        sponsor_configureformbuttons( editor, editor.mode() );
        return {};
    });
}

function sponsor_cleartriggers( editor ) {
    $.each( sponsor_trigger_fields, function(i, field) {
        editor.off( 'change keyup' );
    })
}

// only define afterdatatables if needed
if ( ['/admin/sponsors'].includes(location.pathname) ) {
// set up buttons for edit form after datatables has been initialized
function afterdatatables() {
    // needs to be same in admin_eventscalendar.js
    editor.on('open', function( e, mode, action ) {
        // set up the buttons
        sponsor_configureformbuttons( this, action );

        return true;
    });

    // set the triggers which case the form buttons to change
    sponsor_settriggers( editor );

    // prevent field focus issue. see https://stackoverflow.com/a/16126064/799921
    $.ui.dialog.prototype._focusTabbable = $.noop;
}
} // if [].includes(location.pathname)

