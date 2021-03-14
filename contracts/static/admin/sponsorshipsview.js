// only define afterdatatables if needed
if ( ['/admin/sponsorshipsview'].includes(location.pathname) ) {
    // set up registered filters
    var d = new Date();
    var year = d.getFullYear().toString();
    fltr_register('external-filter-raceyear', year, true);

    // set up buttons for edit form after datatables has been initialized
    function afterdatatables() {
        // initialize filters
        fltr_init();
    }
} // if [].includes(location.pathname)
