// TODO: this needs work -- make similar import scheme for clients table

// set editor form width
$.extend( $.fn.DataTable.Editor.display.jqueryui.modalOptions, {
    width: '1200px'
} );

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
