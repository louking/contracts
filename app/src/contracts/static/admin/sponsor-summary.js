// summarize table, only called when rendering sponsor.summary.jinja2
var summary_firstdraw = true;
var summary_focusyear;
var loyear = 9999; 
var hiyear = 0;

// try to initialize a couple of buttons. only one will be initialized, depending on the page this is on
$(function() {
    var navbuttons = ['#sponsorsummary-details-button', '#sponsordetails-summary-button'];
    for (var i = 0; i < navbuttons.length; i++) {
        nbid = navbuttons[i];
        var navbutton = $(nbid);
        navbutton.button();
        navbutton.on('click', function () {
            var that = this;
            var params = location.search;
            window.location.href = $(that).attr('url') + params;
        });
    };
});

function summary_drawcallback( settings ) {
    console.log('summary_drawcallback()');

    var api = this.api();

    // get all the row data, as currently filtered
    var data = api.rows({
                    page:'all',
                    search: 'applied',
                    order: 'index',
                }).data();

    // if this is the first draw, look at all the data to set the year under review
    // also chart can be drawn now
    if (summary_firstdraw) {
        summary_firstdraw = false;
        var alldata = api.rows({
                        page:'all',
                        search: 'none',
                        order: 'index',
                    }).data();
        // find year range
        for (var i = 0; i < alldata.length; i++) {
            var thisrow = alldata[i];
            if (thisrow.raceyear < loyear) loyear = thisrow.raceyear;
            if (thisrow.raceyear > hiyear) hiyear = thisrow.raceyear;
        }

        var yearselect = '<select id="summary-race-year-select" name="year">\n';
        for (var year = hiyear; year >= loyear; year--) {
            yearselect += '   <option value="' + year + '">' + year + '</option>\n';
        }
        yearselect += '</select>';
        $( yearselect ).appendTo('#summary-race-year');
        $( '#summary-race-year-select' ).select2({
                                            minimumResultsForSearch: Infinity
                                        });
        summary_focusyear = Number($( '#summary-race-year-select' ).val());
        $( '#summary-race-year-select' ).on('change', function(event) {
            summary_focusyear = Number($( '#summary-race-year-select' ).val());
            api.draw();
        });
    } // if (summary_firstdraw)

    // scan table to calculate level, trend, yearly data
    var levels = {};
    var trends = {};
    trends[summary_focusyear] = {};
    trends[summary_focusyear-1] = {};
    var years = {};
    var minyear = Math.max(loyear, summary_focusyear-5+1);
    var maxyear = summary_focusyear;
    var loweeknum = 52;
    var hiweeknum = 0;
    for (var year = minyear; year <= maxyear; year++) {
        years[year] = {total:0, avg:0, count:0, weeks:{}}
    }
    var thisyear, prevyear, thisamount, prevamount;

    let today = moment({hour: 0});  // midnight today morning
    let sponsorlastseq = {};

    for (var i=0; i<data.length; i++) {
        var thisrow = data[i];
        // console.log('data['+i+']='+JSON.stringify(data[i]));

        if (today.year() == thisrow.raceyear) {
            sponsorlastseq[thisrow.raceyear] = today.format('MM-DD');
        } else {
            sponsorlastseq[thisrow.raceyear] = '';
        }

        var state = thisrow.state.state;

        // track levels for committed sponsorships
        if (thisrow.raceyear == summary_focusyear && state == 'committed') {
            level = thisrow.level.race_level;
            if (!(level in levels)) {
                // pick up the first amount for this level for sorting
                levels[level] = {name:level, val:0, amount:thisrow.amount};
            }
            levels[level].val += 1;
        }

        // track trends - look at focus year and previous
        var raceyear = Number(thisrow.raceyear);
        var amount = thisrow.amount;
        if (_.includes([summary_focusyear, summary_focusyear-1], raceyear) && thisrow.treatment == 'summarize') {
            var thisrace = thisrow.race.race;
            var sponsor = thisrow.client.client;
            var level = thisrow.level.race_level;
            // console.log(`adding to trends: ${raceyear} "${thisrace}" "${sponsor}"`)
            if (!_.has(trends, [raceyear, thisrace, sponsor])) {
                !_.set(trends, [raceyear, thisrace, sponsor], [])
            }
            trends[raceyear][thisrace][sponsor].push( 
                {
                    race:thisrace,
                    raceyear:raceyear,
                    state:state,
                    sponsor:sponsor, 
                    level:level, 
                    amount:amount,
                }
            );
        }

        // track yearly data for committed sponsorships
        if (state == 'committed' && thisrow.treatment == 'summarize') {
            if (raceyear >= minyear && raceyear <= maxyear) {
                years[raceyear].total += amount;
                years[raceyear].count += 1;
                // this could be done after the loop but keeping it here for readability
                years[raceyear].avg = _.round(years[raceyear].total / years[raceyear].count);
                //{total:0, avg:0, count:0, weeks:{}}
                m = moment(thisrow.dateagreed);
                // if dateagreed is previous year, force to Jan 1 of the race year
                // thisrow.mdateagreed is used for drawing chart
                thisrow.mdateagreed = thisrow.dateagreed
                if (m.year() < raceyear) {
                    m = moment(raceyear + '-01-01')
                    thisrow.mdateagreed = raceyear + '-01-01'
                }
                weeknum = m.week();
                if (weeknum < loweeknum) 
                    loweeknum = weeknum;
                if (weeknum > hiweeknum)
                    hiweeknum = weeknum;
                if (!(weeknum in years[raceyear].weeks)) 
                    years[raceyear].weeks[weeknum] = {amount:0}
                years[raceyear].weeks[weeknum].amount += amount;
            }
        }
    } // for (var i=0; i<data.length; i++)

    // set up levels table
    levelorder = _.sortBy(levels, ['amount']);
    _.reverse( levelorder );

    // clear levels table, then fill in
    $('#levels tbody').find('tr').remove();
    $('#levels tfoot').find('tr').remove();
    var totlevels = 0
    for (var i = 0; i < levelorder.length; i++) {
        var thislevel = levelorder[i];
        $('#levels tbody').append('<tr><td>' + thislevel.name + '</td><td>' + thislevel.val + '</td></tr>');
        totlevels += thislevel.val;
    }
    $('#levels tfoot').append('<tr><td>' + 'TOTAL' + '</td><td>' + totlevels + '</td></tr>');

    // calculate trends
    var trendsummary = {
        lost: {count:0, amount:0},
        new: {count:0, amount:0},
        up: {count:0, amount:0},
        down: {count:0, amount:0},
        same: {count:0, amount:0},
        solicited: {count:0, amount:0},
        pending: {count:0, amount:0},
    }

    // calculate trend
    // *** note logic here must match that in trends.calculateTrend (trends.py) ***
    $.each( trends, function(raceyear, races ) {
        $.each( races, function(thisrace, sponsors)  {
            $.each( sponsors, function(sponsor, sponsorships) {
                // console.log(`trend loop processing ${raceyear} "${thisrace}" "${sponsor}"`)
                // handle records for focused year
                if (raceyear == summary_focusyear) {
                    // filter out canceled and in kind sponsorships
                    thisyear = sponsorships.filter(sship => sship.state != 'canceled' && sship.amount != 0);
                    thisyearfirst = thisyear[0];

                    // continue if no sponsorships to look at
                    if (thisyearfirst == undefined) return true; // continue
                    
                    prevyearsships = _.get(trends, [summary_focusyear-1, thisrace, sponsor], []);

                    // filter prevyear array to only committed, nonzero sponsorships, and calculate amount
                    prevyear = prevyearsships.filter(sship => sship.state == 'committed' && sship.amount != 0);
                    prevamount = prevyear.reduce((sum, s) => sum + s.amount, 0);

                    // calculate amount for thisyear
                    thisamount = thisyear.reduce((sum, s) => sum + s.amount, 0);

                    // did not sponsor last year
                    if (prevyear == undefined || prevyear.length == 0) {
                        if (thisyearfirst.state == 'committed') {
                            trendsummary.new.count += 1;
                            trendsummary.new.amount += thisamount;
                            // console.log(`new,${raceyear},${thisrace},${sponsor},${thisamount}`)
                        }

                    // did sponsor last year
                    } else {
                        // committed this year
                        if (thisyearfirst.state == 'committed') {
                        // same amount as last year
                            if (thisamount == prevamount) {
                                trendsummary.same.count += 1;
                                trendsummary.same.amount += 0;  // net is always 0
                                // console.log(`same,${raceyear},${thisrace},${sponsor},0`)
                                // more than last year
                            } else if (thisamount > prevamount) {
                                trendsummary.up.count += 1;
                                trendsummary.up.amount += (thisamount - prevamount);
                                // console.log(`up,${raceyear},${thisrace},${sponsor},${thisamount - prevamount}`)
                            // less than last year
                            } else if (thisamount < prevamount) {
                                trendsummary.down.count += 1;
                                // this will be negative
                                trendsummary.down.amount += (thisamount - prevamount);
                                // console.log(`down,${raceyear},${thisrace},${sponsor},${thisamount - prevamount}`)
                            }
                        }
                    }

                    // we have solicited a sponsorship
                    if (thisyearfirst.state == 'tentative') {
                        trendsummary.solicited.count += 1;
                        // if we've solicited a sponsor we had from a previous year, 
                        // until they commit their amount from the previous year is viewed as negative
                        if (prevyear != undefined && prevyear.length > 0) {
                            trendsummary.solicited.amount -= prevamount;
                        }
                        // console.log(`solicited,${raceyear},${thisrace},${sponsor},${-prevamount}`)
                    
                    // we haven't solicited yet
                    } else if (thisyearfirst.state == 'renewed-pending') {
                        trendsummary.pending.count += 1;
                        // if a sponsor we had from a previous year hasn't yet been solicitited, 
                        // until they commit their amount from the previous year is viewed as negative
                        if (prevyear != undefined && prevyear.length > 0) {
                            trendsummary.pending.amount -= prevamount;
                        }
                        // console.log(`pending,${raceyear},${thisrace},${sponsor},${-prevamount}`)
                    }
                
                // handle records for previous year
                } else {
                    if (!_.has(trends, [summary_focusyear, thisrace, sponsor])) {
                        _.set(trends, [summary_focusyear, thisrace, sponsor], [])
                    }
                    thisyear = trends[summary_focusyear][thisrace][sponsor];
                    thisyearfirst = thisyear[0];

                    // filter to committed sponsorships that are not in-kind
                    prevyear = sponsorships.filter(sship => sship.state == 'committed' && sship.amount != 0);
                    prevamount = prevyear.reduce((sum, s) => sum + s.amount, 0);

                    // lost sponsor from last year
                    if (prevyear.length != 0 && (thisyear.length == 0 || thisyearfirst.state == 'canceled')) {
                        trendsummary.lost.count += 1;
                        // record as negative
                        trendsummary.lost.amount -= prevamount;
                        // console.log(`lost,${raceyear},${thisrace},${sponsor},${prevamount}`)
                    }
                }
            });
        });
    });

    // render trends table
    $('#trends tbody').find('tr').remove();
    $('#trends tfoot').find('tr').remove();
    var totsponsors = 0;
    var totamount = 0;
    $.each(['lost', 'new', 'up', 'down', 'same', 'solicited', 'pending'], function(i, trend) {
        var count  = trendsummary[trend].count;
        var amount = trendsummary[trend].amount;
        if (!_.includes(['lost', 'solicited', 'pending'], trend)) totsponsors += count;
        totamount += amount;
        $('#trends tbody').append('<tr><td>' 
                        + trend + '</td><td>' 
                        + count + '</td><td>$' 
                        + amount
                        + '</td></tr>');
    });
    $('#trends tfoot').append('<tr><td>' 
                        + 'NET' + '</td><td>' 
                        + totsponsors + '</td><td>$' 
                        + totamount
                        + '</td></tr>');


    // render yearly table
    $('#yearly thead').find('tr').remove();
    $('#yearly tbody').find('tr').remove();
    $('#yearly tfoot').find('tr').remove();
    yearly_head = '<tr><th>Date/Stat</th>';
    for (var year = maxyear; year >= minyear; year--)
        yearly_head += '<th>' + year + '</th>';
    yearly_head += '</tr>';
    $('#yearly thead').append(yearly_head);
    $.each(['total', 'avg', 'count'], function(i, stat) {
        var stat_body = '<tr><td>' + stat + '</td>';
        for (var year = maxyear; year >= minyear; year--) {
            if (_.includes(['total', 'avg'], stat))
                thisstat = '$' + years[year][stat]
            else
                thisstat = years[year][stat];
            stat_body += '<td>' + thisstat + '</td>';
        }
        stat_body += '</tr>';
        $('#yearly tbody').append(stat_body);
    });
    var cdf = {};
    for (week = loweeknum; week <= hiweeknum; week++) {
        var m = moment().year(summary_focusyear)
        var dates = m.week(week).day(0).format('MM/DD') 
            + ' - ' + m.week(week).day(6).format('MM/DD');
        var date_body = '<tr><td>' + dates + '</td>'
        for (var year = maxyear; year >= minyear; year--) {
            if (!(year in cdf))
                cdf[year] = 0;
            if (week in years[year].weeks)
                cdf[year] += years[year].weeks[week].amount;
            // don't show stats for weeks after today
            if (year == today.year() && week > today.week())
                date_body += '<td></td>'
            else
                date_body += '<td>$' + cdf[year] + '</td>';
        }
        date_body += '</tr>';
        $('#yearly tbody').append(date_body);
    }

    // draw chart
    // transform dataset into what chart wants to see
    // [{'label':label, values: [{'date':date[yyyy-mm-dd or mm-dd], 'value':value}, ... ]}, ... ]
    let years_dataset = _.transform(data, function(result, item) {
        // skip invalid items and uncommitted items
        if (!item.hasOwnProperty('state') || item.state.state != 'committed' || item.treatment != 'summarize') {
            return true;
        }
        // skip when year is outside of range
        if (item.raceyear < minyear || item.raceyear > maxyear) {
            return true;
        }
        (result[item.raceyear] || (result[item.raceyear] = {
            label:item.raceyear,
            values:[]})).values.push({x:item.mdateagreed,
            // make sure item.amount is number
            value:+item.amount})
    }, {});
    // sort values
    years = Object.keys(years_dataset);
    years.sort().reverse();
    let dataset = [];
    let lodate = '12-31',
        hidate = '01-01';
    for (var i=0; i<years.length; i++) {
        year = years[i];
        yearobj = years_dataset[year];
        // sort values by date
        yearobj.values = _.sortBy(yearobj.values, ['x']);
        // make a copy because we're messing with the values
        thisobj = _.cloneDeep(yearobj);
        // fill dataset with cumulative frequency
        let yearaccum = 0;
        thisobj.values.forEach(function(valueobj) {
            yearaccum += valueobj.value;
            valueobj.value = yearaccum;
        });
        dataset.push(thisobj);

        // calculate date range
        // this assumes earliest date charted is no earlier than Jan 1
        // * see item.mdateagreed / thisrow.mdateagreed manipulation
        if (moment(yearobj.values[0].x).format('MM-DD') < lodate) {
            lodate = moment(yearobj.values[0].x).format('MM-DD');
        }
        if (moment(yearobj.values[yearobj.values.length-1].x).format('MM-DD') > hidate) {
            hidate = moment(yearobj.values[yearobj.values.length-1].x).format('MM-DD');
        }
    };

    // charts_line_chart_annual({
    let weeklychart = new Chart({
        data : dataset,
        margin : {top:30, left:60, right:100, bottom:80},
        containerselect : '#weekly-chart',
        // chartheader : 'accumulated sponsorship $',
        xrange : [lodate, hidate],
        xaxis : 'date',
        xdirection : 'asc',
        lastseq: sponsorlastseq,
        yaxislabel : 'total sponsorship dollars',
        ytickincrement : 500,
        statstable: {containerid: 'weekly-chart-table', 'headers': ['Year', 'Date', 'Sponsor $']}
    });
    weeklychart.draw();

} // summary_drawcallback

// only define afterdatatables if needed
if ( ['/admin/sponsorsummary'].includes(location.pathname) ) {
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
