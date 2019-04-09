// summarize table, only called when rendering sponsor.summary.jinja2
var summary_firstdraw = true;
var summary_focusyear;
var loyear = 9999; 
var hiyear = 0;

function summary_drawcallback( settings ) {
    console.log('summary_drawcallback()');

    var api = this.api();

    // if this is the first draw, look at all the data to set the year under review
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

    // get all the row data, as currently filtered
    var data = api.rows({
                    page:'all',
                    search: 'applied',
                    order: 'index',
                }).data();

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

    for (var i=0; i<data.length; i++) {
        var thisrow = data[i];
        // console.log('data['+i+']='+JSON.stringify(data[i]));

        // state must be committed to track
        // if (thisrow.state.state != 'committed') continue;
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
        if (_.includes([summary_focusyear, summary_focusyear-1], raceyear)) {
            var thisrace = thisrow.race.race;
            var sponsor = thisrow.client.client;
            var level = thisrow.level.race_level;
            // console.log('race='+thisrace+' year='+raceyear+' sponsor='+sponsor);
            if (!(thisrace in trends[raceyear])) {
                trends[raceyear][thisrace] = {};
            }
            trends[raceyear][thisrace][sponsor] = {
                race:thisrace,
                raceyear:raceyear,
                state:state,
                sponsor:sponsor, 
                level:level, 
                amount:amount,
            };
        }

        // track yearly data for committed sponsorships
        if (state == 'committed') {
            if (raceyear >= minyear && raceyear <= maxyear) {
                years[raceyear].total += amount;
                years[raceyear].count += 1;
                // this could be done after the loop but keeping it here for readability
                years[raceyear].avg = _.round(years[raceyear].total / years[raceyear].count);
                //{total:0, avg:0, count:0, weeks:{}}
                m = moment(thisrow.dateagreed);
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

    $.each( trends, function(raceyear, races ) {
        $.each( races, function(thisrace, sponsors)  {
            $.each( sponsors, function(sponsor, rec) {
                // handle records for focused year
                var thisrace = rec.race;
                if (rec.raceyear == summary_focusyear) {
                    thisyear = rec;
                    prevyear = trends[summary_focusyear-1][thisrace];
                    if (prevyear != undefined) prevyear = trends[summary_focusyear-1][thisrace][sponsor];

                    // did not sponsor last year
                    if (undefined == prevyear || prevyear.state != 'committed') {
                        if (thisyear.state == 'committed') {
                            trendsummary.new.count += 1;
                            trendsummary.new.amount += thisyear.amount;
                        }

                    // did sponsor last year
                    } else {
                        // committed this year
                        if (thisyear.state == 'committed') {
                        // same amount as last year
                            if (thisyear.amount == prevyear.amount) {
                                trendsummary.same.count += 1;
                                trendsummary.same.amount += 0;  // net is always 0
                            // more than last year
                            } else if (thisyear.amount > prevyear.amount) {
                                trendsummary.up.count += 1;
                                trendsummary.up.amount += (thisyear.amount - prevyear.amount);
                            // less than last year
                            } else if (thisyear.amount < prevyear.amount) {
                                trendsummary.down.count += 1;
                                // this will be negative
                                trendsummary.down.amount += (thisyear.amount - prevyear.amount);
                            }
                        }
                    }

                    // we have solicited a sponsorship
                    if (thisyear.state == 'tentative') {
                        trendsummary.solicited.count += 1;
                    
                    // we haven't solicited yet
                    } else if (thisyear.state == 'renewed-pending') {
                        trendsummary.pending.count += 1;
                    }
                
                // handle records for previous year
                } else {
                    thisyear = trends[summary_focusyear][thisrace];
                    if (thisyear != undefined) thisyear = trends[summary_focusyear][thisrace][sponsor];
                    prevyear = rec;

                    // lost sponsor from last year
                    if (prevyear.state == 'committed') {
                        if (undefined == thisyear || thisyear.state == 'canceled') {
                            trendsummary.lost.count += 1;
                            // record as negative
                            trendsummary.lost.amount -= prevyear.amount;
                        }
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
    var today = moment();
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
