// summarize table, only used when rendering race.summary.jinja2
let racesummary_firstdraw = true;
let rsloyear = 9999;
let rshiyear = 0;
let racesummary_charts = [];
let years;

function racesummary_showchart( charttype ) {
    $( '.race-chart' ).hide();
    $( '#' + charttype + '-chart' ).show();
}

function racesummary_setshowlabels ( numyears ) {
    let labels = [];
    if (numyears != -1) {
        labels = years.slice(0, numyears);
    }
    for (let i=0; i<racesummary_charts.length; i++) {
        let chart = racesummary_charts[i];
        chart.setshowlabels(labels);
    }
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
            {val:'daysfromreg', text:'days from registration open'},
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

        let numyearselect = '<select id="summary-race-numyear-select" name="numyear">\n';
        let numyearsoptions = [
            {val:'-1', text:'all'},
            {val:'5', text:'5'},
            {val:'4', text:'4'},
            {val:'3', text:'3'},
            {val:'2', text:'2'},
            {val:'1', text:'1'},
        ];
        for (let i=0; i<numyearsoptions.length; i++) {
            numyear = numyearsoptions[i];
            numyearselect += '   <option value="' + numyear.val + '">' + numyear.text + '</option>\n';
        }
        numyearselect += '</select>';
        $( numyearselect ).appendTo('#summary-race-numyears');
        $( '#summary-race-numyear-select' ).select2({
                                            minimumResultsForSearch: Infinity,
                                            width: '75px',
                                        });
        $( '#summary-race-numyear-select' ).on('change', function(event) {
            racesummary_setshowlabels( $( '#summary-race-numyear-select' ).val() );
        });

    } // if (racesummary_firstdraw)

    // clear racesummary_charts each draw
    racesummary_charts = [];

    // draw date chart
    // transform dataset into what chart wants to see
    // [{'label':year, values: [{'x':date[yyyy-mm-dd or mm-dd], 'value':value}, ... ]}, ... ]
    let years_dataset = _.transform(data, function(result, item) {
        // skip invalid items and uncommitted items
        if (!item.hasOwnProperty('race')) {
            return true;
        }
        let raceyear = item.race_date.split('-')[0];
        (result[raceyear] || (result[raceyear] = {
            label:raceyear,
            values:[]
        })).values.push({
            x:item.registration_date,
            daystorace: moment(item.race_date).diff(moment(item.registration_date), 'days'),
            daysfromreg: moment(item.registration_date).diff(moment(item.regopen_date), 'days'),
            race_date: item.race_date,
            regopen_date: item.regopen_date,
            // make sure item.amount is number
            value:+item.count
        })
    }, {});
    // sort values
    years = Object.keys(years_dataset);
    years.sort().reverse();
    let dataset = [];
    let lodate = '12-31',
        hidate = '01-01';
    let today = moment({hour: 0});  // midnight today morning
    let datelastseq = {};
    for (let i=0; i<years.length; i++) {
        let year = years[i];
        let yearobj = years_dataset[year];
        // sort values by date
        yearobj.values = _.sortBy(yearobj.values, ['x']);
        // make a copy because we're messing with the values
        let thisobj = _.cloneDeep(yearobj);

        if (today.year() == thisobj.label) {
            datelastseq[thisobj.label] = today.format('MM-DD');
        } else {
            datelastseq[thisobj.label] = moment(thisobj.values[0].race_date).format('MM-DD');
        }

        // TODO: determine cumulative vs frequency algorithm based on pulldown
        // fill dataset with cumulative frequency
        let yearaccum = 0;
        thisobj.values.forEach(function(valueobj) {
            yearaccum += valueobj.value;
            valueobj.value = yearaccum;
        });
        dataset.push(thisobj);

        // calculate date range
        if (moment(yearobj.values[0].x).format('MM-DD') < lodate) {
            lodate = moment(yearobj.values[0].x).format('MM-DD');
        }
        if (moment(yearobj.values[yearobj.values.length-1].x).format('MM-DD') > hidate) {
            hidate = moment(yearobj.values[yearobj.values.length-1].x).format('MM-DD');
        }
    };

    // need to show all charts while drawing, else error calculating width, height
    $( '.race-chart' ).show();

    // date chart
    $('#date-chart svg').remove();
    let datechart = new Chart({
        data : dataset,
        margin : {top:30, left:60, right:100, bottom:80},
        containerselect : '#date-chart',
        chartheader : 'registrants by date',
        xrange : [lodate, hidate],
        xaxis: 'date',
        xdirection: 'asc',
        yaxislabel : 'number of registrants',
        ytickincrement : 100,
        lastseq: datelastseq,
    });
    datechart.draw();
    racesummary_charts.push(datechart);

    // now accumulate values
    // note dataset has already been sorted nicely
    let daystoraceset = _.cloneDeep(dataset);
    let daysfromregset = _.cloneDeep(dataset);
    let daystoracelastseq = {};
    let daysfromreglastseq = {};
    let maxdays = 0;

    for (let i=0; i<daystoraceset.length; i++) {
        let thisobj = daystoraceset[i];
        if (today.year() == thisobj.label) {
            daystoracelastseq[thisobj.label] = moment(thisobj.values[0].race_date).diff(today, 'days');
        } else {
            daystoracelastseq[thisobj.label] = 0;
        }
        thisobj.values.forEach(function(valueobj) {
            valueobj.x = valueobj.daystorace;
            if (valueobj.x > maxdays) maxdays = valueobj.x;
        });
        thisobj = daysfromregset[i];
        if (today.year() == thisobj.label) {
            daysfromreglastseq[thisobj.label] = moment(today).diff(thisobj.values[0].regopen_date, 'days');
        } else {
            daysfromreglastseq[thisobj.label] = moment(thisobj.values[0].race_date).diff(moment(thisobj.values[0].regopen_date), 'days');
        }
        thisobj.values.forEach(function(valueobj) {
            valueobj.x = valueobj.daysfromreg;
        });
    }

    // days to race chart
    $('#daystorace-chart svg').remove();
    let daystoracechart = new Chart({
        data : daystoraceset,
        margin : {top:30, left:60, right:100, bottom:80},
        containerselect : '#daystorace-chart',
        chartheader : 'registrants by days to race',
        xrange : [maxdays, 0],
        xdirection : 'desc',
        yaxislabel : 'number of registrants',
        ytickincrement : 100,
        lastseq : daystoracelastseq,
    });
    daystoracechart.draw();
    racesummary_charts.push(daystoracechart);

    // days from registration chart
    $('#daysfromreg-chart svg').remove();
    let daysfromregopenchart = new Chart({
        data : daysfromregset,
        margin : {top:30, left:60, right:100, bottom:80},
        containerselect : '#daysfromreg-chart',
        chartheader : 'registrants by days from registration open',
        xrange : [0, maxdays],
        xdirection : 'asc',
        yaxislabel : 'number of registrants',
        ytickincrement : 100,
        lastseq : daysfromreglastseq,
    });
    daysfromregopenchart.draw();
    racesummary_charts.push(daysfromregopenchart);

    // can show the current chart now
    racesummary_showchart( $( '#summary-race-charttype-select' ).val() );

    // show labels based on current setting
    racesummary_setshowlabels( $( '#summary-race-numyear-select' ).val() );

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
