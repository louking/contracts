// generic datatables / Editor handling

// data is an list of objects for rendering or url for ajax retrieval of similar object
// buttons is a JSON parsable string, as it references editor which hasn't been instantiated yet
// options is an object with the following keys
//     dtopts:       options to be passed to DataTables instance, 
//                   except for data: and buttons: options, passed in data, buttons
//     editoropts:   options to be passed to Editor instance, 
//                   if not present, Editor will not be configured
//     updateopts:   options to configure Editor select fields with
//                   see crudapi.py for more details
//     yadcfopts:    yadcf options to be passed to yadcf 
//                   if not present, yadcf will not be configured

var editor, _dt_table;

function datatables(data, buttons, options, files) {

    // convert render to javascript
    if (options.dtopts.hasOwnProperty('columns')) {
        for (i=0; i<options.dtopts.columns.length; i++) {
            if (options.dtopts.columns[i].hasOwnProperty('render')) {
                options.dtopts.columns[i].render = eval(options.dtopts.columns[i].render)
            }
        }        
    }
    // convert display and render to javascript
    if (options.editoropts !== undefined) {
        if (options.editoropts.hasOwnProperty('fields')) {
            for (i=0; i<options.editoropts.fields.length; i++) {
                if (options.editoropts.fields[i].hasOwnProperty('render')) {
                    options.editoropts.fields[i].render = eval(options.editoropts.fields[i].render)
                }
                if (options.editoropts.fields[i].hasOwnProperty('display')) {
                    options.editoropts.fields[i].display = eval(options.editoropts.fields[i].display)
                }
            }        
        }
    }

    // configure editor if requested
    if (options.editoropts !== undefined) {
        $.extend(options.editoropts,{table:'#datatable'})
        editor = new $.fn.dataTable.Editor ( options.editoropts );

        if (options.updateopts !== undefined) {
            for (i=0; i<options.updateopts.length; i++) {
                if (options.updateopts[i].on == 'open') {
                    editor.dependent( options.updateopts[i].name, options.updateopts[i].url, {event:'focus'} )
                } else if (options.updateopts[i].on == 'change') {
                    editor.dependent( options.updateopts[i].name, options.updateopts[i].url, {event:'change'} )
                }
            }
        }

        // set Editor files if supplied
        if (files) {
            $.fn.dataTable.Editor.files = files
        }
    }

    // set up buttons, special care for editor buttons
    var button_options = [];
    for (i=0; i<buttons.length; i++) {
        button = buttons[i];
        if ($.inArray(button, ['create', 'edit', 'remove']) >= 0) {
            button_options.push({extend:button, editor:editor});
        } else {
            button_options.push(button);
        }
    };

    $.extend(options.dtopts, {buttons:button_options});

    // assume data is url if serverSide is truthy
    if (options.dtopts.serverSide) {
        $.extend(options.dtopts, { ajax: data });

    // otherwise assume it is object containing the data to render
    } else {
        $.extend(options.dtopts, { data: data });
    };

    // define the table
    _dt_table = $('#datatable').DataTable ( options.dtopts );

    // any column filtering required? if so, define the filters
    if (options.yadcfopts !== undefined) {
        yadcf.init(_dt_table, options.yadcfopts);
    }

    // take care of any initialization which needs to be done after datatables is initialized
    if (typeof afterdatatables !== "undefined") {
        afterdatatables();
    };
}

// from https://github.com/select2/select2/issues/1246#issuecomment-17428249
// $.ui.dialog.prototype._allowInteraction = function(e) {
//     return !!$(e.target).closest('.ui-dialog, .ui-datepicker, .select2-drop').length;
// };

// patch for select2 search. see https://stackoverflow.com/questions/19787982/select2-plugin-and-jquery-ui-modal-dialogs
if ($.ui && $.ui.dialog && $.ui.dialog.prototype._allowInteraction) {
    var ui_dialog_interaction = $.ui.dialog.prototype._allowInteraction;
    $.ui.dialog.prototype._allowInteraction = function(e) {
        if ($(e.target).closest('.select2-dropdown').length) return true;
        return ui_dialog_interaction.apply(this, arguments);
    };
}

