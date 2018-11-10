// set editor form width
$.extend( $.fn.DataTable.Editor.display.jqueryui.modalOptions, {
    width: '1200px'
} );

// current date for form
function currentdate() {
    var now = new Date()

    var day  = now.getDate().toString().padStart(2, '0');
    var mon  = (now.getMonth()+1).toString().padStart(2, '0');
    var year = now.getFullYear().toString();

    return year + '-' + mon + '-' + day;
}

// configure form buttons
function configurebuttons( that, action ) {
    // set buttons for create
    if ( action == 'create' ) {
        that.buttons( 'Create' );

    // set buttons for edit
    } else if ( action == 'edit' ) {
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
                    text: 'Mark as Paid',
                    className: ( that.field( 'paymentRecdDate' ).get() ) ? 'disabled' : 'enabled',
                    action: function () {
                        if ( ! that.field( 'paymentRecdDate' ).get() ) {                 
                            that.field( 'paymentRecdDate' ).set( currentdate() );
                            that.submit();
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

            ]);

    // set buttons for remove (only other choice)
    } else {
        that.buttons( 'Delete' );
    }
}

// set up buttons for edit form after datatables has been initialized
function afterdatatables() {
    editor.on('open', function( e, mode, action ) {
        // set up the buttons
        configurebuttons( this, action );

        // special processing for contractApproverNotes field to make readonly
        editor.field( 'contractApproverNotes' ).disable();
        
        return true;
    });

    // regenerate the edit buttons if certain fields change
    editor.dependent([ 'state.id', 'contractDocId', 'invoiceSentDate', 'paymentRecdDate' ], function( val, data, callback ) {
        // TODO: how to determine action?
        console.log('dependent fired');
        configurebuttons( editor, editor.mode() );
        return {};
    });
}


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
