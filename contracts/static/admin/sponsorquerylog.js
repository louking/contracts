if ( ['/admin/sponsorquerylog'].includes(location.pathname) ) {
    console.log('got here');
    function afterdatatables() {
        editor.on('open', function( e, mode, action ) {
            // special processing for field to make readonly
            editor.field('comments').disable();
            editor.buttons([
                {
                    text: 'Cancel',
                    action: function () {
                        editor.close();
                    }
                },
            ]);

            return true;
        });
    }
}
