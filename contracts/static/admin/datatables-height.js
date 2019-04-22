// adapted from https://datatables.net/forums/discussion/comment/104797/#Comment_104797

// call from $(document).ready() if desired
function firstDataTableScrollAdjust() {
    // first render of data table
    jsDataTableScrollAdjust();
    
    window.onresize = function() {
        // adjust the hight of the data table on a browser resize event
        jsDataTableScrollAdjust();
    };
}

function jsDataTableScrollAdjust() {
    if(_dt_table) {
        var height = jsGetDataTableHeightPx() + "px";
        $('.dataTables_scrollBody:has(#datatable)').css('max-height', height);
        $('.DTFC_LeftBodyLiner').css('max-height', height);
        _dt_table.draw();
    }
}

/**
 * Gets the data table height based upon the browser page
 * height and the data table vertical position.
 * 
 * @return  Data table height, in pixels.
 */
function jsGetDataTableHeightPx() {
     // set default return height
    var retHeightPx = 350;

    // no nada if there is no dataTable (container) element
    var dataTable = document.getElementById("datatable");
    if(!dataTable) {
        return retHeightPx;
    }

    // do nada if we can't determine the browser height
    var pageHeight = $(window).height();
    if(pageHeight < 0) {
        return retHeightPx;
    }

    // determine the data table height based upon the browser page height
    var dataTableHeight = pageHeight - 320; //default height
    var dataTablePos = $("#datatable").offset();
    var dataTableInfoHeight = $('#datatable_info').height();
    var fudge = 15; // for some reason need this to avoid window scroll bar
    if(dataTablePos != null && dataTablePos.top > 0) {
        // the data table height is the page height minus the top of the data table,
        // minus the info at the bottom
        dataTableHeight = pageHeight - dataTablePos.top - dataTableInfoHeight - fudge;

        // clip height to min. value
        retHeightPx = Math.max(100, dataTableHeight);
    }
    return retHeightPx;
}
