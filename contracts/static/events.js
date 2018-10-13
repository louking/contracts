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

// set up buttons for edit form after datatables has been initialized
function afterdatatables() {
    editor.on('open', function( e, mode, action ) {
        // set buttons for create
        if ( action == 'create' ) {
            this.buttons( 'Create' );

        // set buttons for edit
        } else if ( action == 'edit' ) {
            this.buttons([
                    {
                        text: 'Resend Contract',
                        action: function () {
                            console.log('Resend Contract');
                        }
                    },
                    {
                        text: 'Mark Invoice Sent',
                        action: function () {
                            this.field( 'invoiceSentDate' ).set( currentdate() );
                            this.submit();
                        }
                    },
                    {
                        text: 'Mark as Paid',
                        action: function () {
                            this.field( 'paymentRecdDate' ).set( currentdate() );
                            this.submit();
                        }
                    },
                    {
                        text: 'Update',
                        action: function () {
                            this.submit();
                        }
                    },
                    {
                        text: 'Update and Send Contract',
                        action: function () {
                            console.log('Update and Send Contract');
                            this.field( 'contractSentDate' ).set( currentdate() );
                            this.submit();
                        }
                    },

                ]);

        // set buttons for remove (only other choice)
        } else {
            this.buttons( 'Delete' );
        }

        return true;
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
