// only define afterdatatables if needed
if (location.pathname == '/admin.daterules') {
function afterdatatables() {
    // we don't want to see the rulename field; this is updated automatically
    editor.field('rulename').hide()
}
} // if location.pathname