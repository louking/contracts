// googledoc field type plug-in code
(function ($, DataTable) {
 
if ( ! DataTable.ext.editorFields ) {
    DataTable.ext.editorFields = {};
}
 
var Editor = DataTable.Editor;
var _fieldTypes = DataTable.ext.editorFields;
 
_fieldTypes.googledoc = {
    create: function ( conf ) {
        var that = this;
 
        conf._enabled = true;
 
        // Create the elements to use for the input
        conf._input = $(
            '<div id="'+Editor.safeId( conf.id )+'">'+
            '</div>');
 
        return conf._input;
    },
 
    get: function ( conf ) {
        return $(conf._input).attr('value');
    },
 
    set: function ( conf, val ) {
        $('.'+Editor.safeId( conf.id )+'.DTE_FieldType_googledoc').remove();
        $(conf._input).attr( 'value', val );
        if (val != "") {
            $(conf._input).append('<a class="'+Editor.safeId( conf.id )+' DTE_FieldType_googledoc" target=_blank href="https://docs.google.com/document/d/' + $(conf._input).attr( 'value' ) + '/view">contract</a>')
        }
    },
 
    enable: function ( conf ) {
        conf._enabled = true;
        $(conf._input).removeClass( 'disabled' );
    },
 
    disable: function ( conf ) {
        conf._enabled = false;
        $(conf._input).addClass( 'disabled' );
    }
};
 
})(jQuery, jQuery.fn.dataTable);