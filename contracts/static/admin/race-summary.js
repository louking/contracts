// summarize table, only used when rendering race.summary.jinja2
let racesummary_firstdraw = true;
let rsloyear = 9999;
let rshiyear = 0;

function racesummary_showchart( charttype ) {
    $( '.race-chart' ).hide();
    $( '#' + charttype + '-chart' ).show();
}

function racesummary_drawcallback( settings ) {
    console.log('racesummary_drawcallback()');

    let api = this.api();
    let alldata;

    // get all the row data, as currently filtered
    let data = api.rows({
                    page:'all',
                    search: 'applied',
                    order: 'index',
                }).data();

    // if this is the first draw, look at all the data to set the year under review
    // also chart can be drawn now
    if (racesummary_firstdraw) {
        racesummary_firstdraw = false;
        alldata = api.rows({
                        page:'all',
                        search: 'none',
                        order: 'index',
                    }).data();
        // find year range
        for (let i = 0; i < alldata.length; i++) {
            let thisrow = alldata[i];
            if (thisrow.raceyear < rsloyear) rsloyear = thisrow.raceyear;
            if (thisrow.raceyear > rshiyear) rshiyear = thisrow.raceyear;
        }

        let charttypeselect = '<select id="summary-race-charttype-select" name="charttype">\n';
        let charttypes = [
            {val:'daystorace', text:'days to race'},
            {val:'daysfromreg', text:'days from registration'},
            {val:'date', text:'date'},
        ];
        for (let i=0; i<charttypes.length; i++) {
            charttype = charttypes[i];
            charttypeselect += '   <option value="' + charttype.val + '">' + charttype.text + '</option>\n';
        }
        charttypeselect += '</select>';
        $( charttypeselect ).appendTo('#summary-race-charttype');
        $( '#summary-race-charttype-select' ).select2({
                                            minimumResultsForSearch: Infinity,
                                            width: '200px',
                                        });
        // remember current setting (set after charts drawn)
        summaryrace_charttype = $( '#summary-race-charttype-select' ).val();
        $( '#summary-race-charttype-select' ).on('change', function(event) {
            racesummary_showchart( $( '#summary-race-charttype-select' ).val() );
        });

    } // if (racesummary_firstdraw)

    // draw date chart
    // transform dataset into what chart wants to see
    // [{'year':year, values: [{'date':date[yyyy-mm-dd or mm-dd], 'value':value}, ... ]}, ... ]
    let years_dataset = _.transform(data, function(result, item) {
        // skip invalid items and uncommitted items
        if (!item.hasOwnProperty('race')) {
            return true;
        }
        let raceyear = item.race_date.split('-')[0];
        (result[raceyear] || (result[raceyear] = {
            year:raceyear,
            values:[]
        })).values.push({
            date:item.registration_date,
            daystorace: moment(item.race_date).diff(moment(item.registration_date), 'days'),
            daysfromreg: moment(item.registration_date).diff(moment(item.regopen_date), 'days'),
            // make sure item.amount is number
            value:+item.count
        })
    }, {});
    // sort values
    let years = Object.keys(years_dataset);
    years.sort().reverse();
    let dataset = [];
    let lodate = '12-31',
        hidate = '01-01';
    for (let i=0; i<years.length; i++) {
        let year = years[i];
        let yearobj = years_dataset[year];
        // sort values by date
        yearobj.values = _.sortBy(yearobj.values, ['date']);
        // make a copy because we're messing with the values
        let thisobj = _.cloneDeep(yearobj);

        // TODO: determine cumulative vs frequency algorithm based on pulldown
        // fill dataset with cumulative frequency
        let yearaccum = 0;
        thisobj.values.forEach(function(valueobj) {
            yearaccum += valueobj.value;
            valueobj.value = yearaccum;
        });
        dataset.push(thisobj);

        // calculate date range
        if (moment(yearobj.values[0].date).format('MM-DD') < lodate) {
            lodate = moment(yearobj.values[0].date).format('MM-DD');
        }
        if (moment(yearobj.values[yearobj.values.length-1].date).format('MM-DD') > hidate) {
            hidate = moment(yearobj.values[yearobj.values.length-1].date).format('MM-DD');
        }
    };

    // need to show all charts while drawing, else error calculating width, height
    $( '.race-chart' ).show();

    // date chart
    $('#date-chart svg').remove();
    charts_line_chart_annual({
        data : dataset,
        margin : {top:30, left:60, right:100, bottom:80},
        containerselect : '#date-chart',
        chartheader : 'registrants by date',
        yaxislabel : 'number of registrants',
        daterange : [lodate, hidate],
        ytickincrement : 100,
    });

    // now accumulate values
    // note dataset has already been sorted nicely
    let daystoraceset = _.cloneDeep(dataset);
    let daysfromregset = _.cloneDeep(dataset);
    let maxdays = 0;
    for (let i=0; i<daystoraceset.length; i++) {
        let thisobj = daystoraceset[i];
        thisobj.linelabel = thisobj.year;
        thisobj.values.forEach(function(valueobj) {
            valueobj.x = valueobj.daystorace;
            if (valueobj.x > maxdays) maxdays = valueobj.x;
        });
        thisobj = daysfromregset[i];
        thisobj.linelabel = thisobj.year;
        thisobj.values.forEach(function(valueobj) {
            valueobj.x = valueobj.daysfromreg;
        });
    }

    // days to race chart
    $('#daystorace-chart svg').remove();
    charts_line_chart_seq({
        data : daystoraceset,
        margin : {top:30, left:60, right:100, bottom:80},
        containerselect : '#daystorace-chart',
        chartheader : 'registrants by days to race',
        yaxislabel : 'number of registrants',
        xrange : [maxdays, 0],
        ytickincrement : 100,
    });

    // days from registration chart
    $('#daysfromreg-chart svg').remove();
    charts_line_chart_seq({
        data : daysfromregset,
        margin : {top:30, left:60, right:100, bottom:80},
        containerselect : '#daysfromreg-chart',
        chartheader : 'registrants by days from registration',
        yaxislabel : 'number of registrants',
        xrange : [0, maxdays],
        ytickincrement : 100,
    });

    // can show the current chart now
    racesummary_showchart( $( '#summary-race-charttype-select' ).val() );

} // racesummary_drawcallback

// only define afterdatatables if needed
if ( ['/admin/racesummary'].includes(location.pathname) ) {
    // set up registered filters
    fltr_register('external-filter-race', null, false);

    // set up buttons for edit form after datatables has been initialized
    function afterdatatables() {
        // initialize filters
        fltr_init();

        // prevent field focus issue. see https://stackoverflow.com/a/16126064/799921
        $.ui.dialog.prototype._focusTabbable = $.noop;
    }
} // if [].includes(location.pathname)
