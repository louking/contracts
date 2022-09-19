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
