function charts_get_focusid(container, i) {
    // assure unique focusid per chart
    let focusid = 'focus-' + i + '-';
    focusid += container.replace('#', '_');
    return focusid;
}
// line chart with bottom axis days in year, left axis values
// see https://bl.ocks.org/gordlea/27370d1eea8464b04538e6d8ced39e89
function charts_line_chart_annual(options) {
    // options:
    //     data - [{'year':year, values: [{'date':date[yyyy-mm-dd or mm-dd], 'value':value}, ... ]}, ... ]
    //              values need to be sorted by date
    //     margin - 50 OR {top: 50, right: 50, bottom: 50, left: 50} (e.g.), default 40
    //     containerselect - e.g., 'body', '#divname', default 'body'
    //     ytickincrement - y range is bumped up to next integral multiple of this value, default 100
    //     chartheader - optional text - if present, printed in the top center of the chart
    //     yaxislabel - optional text - if present, printed 90 deg rotated, on the left of the chart
    //     daterange - optional array [startdate, enddate] dates in mm/dd format, default ['01-01', '12-31']

    // extend config based on options
    let config = {
        data : null,
        margin : 40,
        containerselect : 'body',
        chartheader : '',
        yaxislabel : '',
        daterange : ['01-01', '12-31'],
        ytickincrement : 100,
    };
    config = Object.assign(config, options);

    // convert margin if necessary
    if (typeof config.margin == 'number') {
        config.margin = {top:config.margin, right:config.margin, bottom:config.margin, left:config.margin};
    }

    // colors copied from matplotlib v2.0 - see https://matplotlib.org/users/dflt_style_changes.html#colors-in-default-property-cycle
    let colorcycle = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728',
                  '#9467bd', '#8c564b', '#e377c2', '#7f7f7f',
                  '#bcbd22', '#17becf'];
    let color = d3.scaleOrdinal()
        .range(['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728',
                  '#9467bd', '#8c564b', '#e377c2', '#7f7f7f',
                  '#bcbd22', '#17becf']);

    // get container
    let container = d3.select(config.containerselect),
        containerjs = document.querySelector(config.containerselect);

    // 2. Use the margin convention practice, for container
    let width = containerjs.clientWidth - config.margin.left - config.margin.right, // Use the container's width
        height = containerjs.clientHeight - config.margin.top - config.margin.bottom, // Use the container's height
        viewbox_width = width + config.margin.left + config.margin.right,
        viewbox_height = height + config.margin.top + config.margin.bottom;

    // 1. Add the SVG to the page and employ #2
    let svg = container.append("svg")
        .attr("width", width + config.margin.left + config.margin.right)
        .attr("height", height + config.margin.top + config.margin.bottom)
      .append("g")
        .attr("transform", "translate(" + config.margin.left + "," + config.margin.top + ")");

    // set up scales and ranges
    let x = d3.scaleTime()
        .range([0, width]);
    let y = d3.scaleLinear()
        .range([height, 0]);

    // 5. X scale will use the date of our data
    let formatDate = d3.timeFormat("%m/%d"),
        bisectDate = d3.bisector(function(d) { return d.date; }).left,
        parseDate = d3.timeParse("%m-%d"),
        lodate = parseDate(config.daterange[0]),
        hidate = parseDate(config.daterange[1]);
    x.domain([lodate, hidate]);

    // see https://bl.ocks.org/d3noob/0e276dc70bb9184727ee47d6dd06e915
    let xAxis = d3.axisBottom(x)
        .tickSize(16)
        .tickFormat(d3.timeFormat("%m/%d"));

    let yAxis = d3.axisLeft(y);

    // ydomaindata is concatenation of all years' data for y.domain(d3.extent),
    // used to determine y domain
    let ydomaindata = [];
    for (i=0; i<config.data.length; i++) {
        config.data[i].values.forEach(function(d) {
            // translate date - maybe remove year first
            let datesplit = d.date.split('-');
            // check if year is present
            // TODO: needs to be special processing if previous year
            if (datesplit.length == 3) {
                d.date = datesplit.slice(1).join('-');
            }
            d.date = parseDate(d.date);
            // force number
            d.value = +d.value;
        });
        ydomaindata = ydomaindata.concat(config.data[i].values);
    };

    // dailydata is used to draw the paths so that there is a point for each day
    let today = new Date().setHours(0,0,0,0);
    let dailydata = [];
    for (i=0; i<config.data.length; i++) {
        let year = config.data[i].year;
        let checkvalues = _.cloneDeep(config.data[i].values);
        let dailyvalues = [];
        // https://stackoverflow.com/questions/563406/add-days-to-javascript-date
        let currvalue = 0;
        for (let thisdate=new Date(lodate); thisdate<=hidate; thisdate.setDate(thisdate.getDate()+1)) {
            while (checkvalues.length > 0 && checkvalues[0].date <= thisdate) {
                let thisitem = checkvalues.shift();
                currvalue = thisitem.value;
            }
            dailyvalues.push({date:new Date(thisdate), value:currvalue});

            // break out after today
            let testdate = new Date(thisdate).setYear(year);
            if (testdate >= today) {
                break;
            }
        }
        dailydata.push( {year: year, values:dailyvalues} );
    }


    // 6. Y scale will use the dataset values
    // force up to next boundary based on ytickincrement
    y.domain([0, Math.ceil(d3.max(ydomaindata, function(d) { return d.value })/config.ytickincrement )*config.ytickincrement]);

    // 3. Call the x axis in a group tag
    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        // see https://bl.ocks.org/d3noob/0e276dc70bb9184727ee47d6dd06e915
        .call(xAxis) // Create an axis component with d3.axisBottom
      // https://bl.ocks.org/d3noob/3c040800ff6457717cca586ae9547dbf
      .selectAll(".tick text")
        .style("text-anchor", "end")
        .attr("dx", "-.8em")
        .attr("dy", ".15em")
        .attr("transform", "rotate(-65)");

    // 4. Call the y axis in a group tag
    svg.append("g")
        .attr("class", "y axis")
        .call(yAxis); // Create an axis component with d3.axisLeft

    // y axis text
    svg.append("text")
        .attr("transform", "rotate(-90)")
        // x and y are flipped due to the rotation. see https://leanpub.com/d3-t-and-t-v4/read#leanpub-auto-the-y-axis-label
        .attr("y", 0 - config.margin.left)
        .attr("x", 0 - (height/2))
        .attr("dy", "1em")
        .style("text-anchor", "middle")
        .text(config.yaxislabel);

    // add heading if we have one
    svg.append("g")
        .attr("class", "heading")
      .append("text")
        .attr("transform", "translate(" + width/2 + ",-10)")
        .style("text-anchor", "middle")
        .text(config.chartheader);

    // 7. d3's line generator
    let line = d3.line()
        .x(function(d) {
            return x(d.date); // set the x values for the line generator
        })
        .y(function(d) {
            return y(d.value); // set the y values for the line generator
        });
        // .curve(d3.curveMonotoneX) // apply smoothing to the line
    
    colormap = [];
    for (let i=0; i<dailydata.length; i++) {
        let year = dailydata[i].year
        colormap.push({'year': year, 'color': colorcycle[i % colorcycle.length]});
    
        svg.append("path")
            .style("stroke", colormap[i].color)
            .datum(dailydata[i].values)
            .attr("class", "line")
            .attr("d", line);
    
        // assure unique focusid per chart
        let thisfocus = svg.append("g")
            .attr("class", "focus")
            .attr("id",charts_get_focusid(config.containerselect, i))
            .style("display", "none");
    
        thisfocus.append("circle")
            .attr("r", 4.5);
    
        thisfocus.append("text")
            .style("text-anchor", "start")
            .attr("x", 4)
            .attr("y", 7)
            .attr("dy", ".35em");
    }
    
    let legend = svg.selectAll(".legend")
        .data(colormap)
      .enter().append("g")
        .attr("class", "legend")
        .attr("transform", function(d, i) { return "translate(" + i * 90 + ",0)"; });
  
    legend.append("rect")
        .attr("y", height + config.margin.bottom - 15)
        .attr("x", 60)
        .attr("width", 15)
        .attr("height", 15)
        .style("fill", function(d) { return d.color });
  
    legend.append("text")
        .attr("x", 15)
        .attr("y", height + config.margin.bottom - 15)
        .attr("dy", ".8em")
        .style("text-anchor", "bottom")
        .text(function(d) { return d.year; });
  
    let mouseoverlay = svg.append("rect")
        .attr("class", "overlay")
        .attr("width", width + config.margin.right)
        .attr("height", height);

    let allfocus = d3.selectAll(".focus");
    mouseoverlay
      .on("mouseover", function() { allfocus.style("display", null); })
      .on("mouseout", function() { allfocus.style("display", "none"); })
      .on("mousemove", mousemove);
  
    function mousemove() {
        let x0 = x.invert(d3.mouse(this)[0]);
        for (let i=0; i<dailydata.length; i++) {
            let j = bisectDate(dailydata[i].values, x0, 1);
            let d;
            // use d0, d1 if in range
            if (j < dailydata[i].values.length) {
                let d0 = dailydata[i].values[j - 1],
                    d1 = dailydata[i].values[j];
                d = x0 - d0.date > d1.date - x0 ? d1 : d0;
            }
            else {
                d = dailydata[i].values[dailydata[i].values.length-1]
            }
            let thisfocus = d3.select('#'+charts_get_focusid(config.containerselect, i));
            thisfocus.attr("transform", "translate(" + x(d.date) + "," + y(d.value) + ")");
            thisfocus.select("text").text(formatDate(d.date) + " " + d.value);
        }
    }

}

// line chart with bottom axis sequential, left axis values
function charts_line_chart_seq(options) {
    // options:
    //     data - [{'linelabel':linelabel, values: [{'x':number, 'value':value}, ... ]}, ... ]
    //              values need to be sorted by date
    //     margin - 50 OR {top: 50, right: 50, bottom: 50, left: 50} (e.g.), default 40
    //     containerselect - e.g., 'body', '#divname', default 'body'
    //     ytickincrement - y range is bumped up to next integral multiple of this value, default 100
    //     xrange - array [startseq, endseq] seq are numeric, startseq may be higher then endseq
    //     chartheader - optional text - if present, printed in the top center of the chart
    //     yaxislabel - optional text - if present, printed 90 deg rotated, on the left of the chart

    // extend config based on options
    let config = {
        data : null,
        margin : 40,
        containerselect : 'body',
        chartheader : '',
        yaxislabel : '',
        xrange : [0, 100],
        ytickincrement : 100,
    };
    config = Object.assign(config, options);

    // convert margin if necessary
    if (typeof config.margin == 'number') {
        config.margin = {top:config.margin, right:config.margin, bottom:config.margin, left:config.margin};
    }

    // colors copied from matplotlib v2.0 - see https://matplotlib.org/users/dflt_style_changes.html#colors-in-default-property-cycle
    let colorcycle = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728',
                  '#9467bd', '#8c564b', '#e377c2', '#7f7f7f',
                  '#bcbd22', '#17becf'];
    let color = d3.scaleOrdinal()
        .range(['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728',
                  '#9467bd', '#8c564b', '#e377c2', '#7f7f7f',
                  '#bcbd22', '#17becf']);

    // get container
    let container = d3.select(config.containerselect),
        containerjs = document.querySelector(config.containerselect);

    // 2. Use the margin convention practice, for container
    let width = containerjs.clientWidth - config.margin.left - config.margin.right, // Use the container's width
        height = containerjs.clientHeight - config.margin.top - config.margin.bottom, // Use the container's height
        viewbox_width = width + config.margin.left + config.margin.right,
        viewbox_height = height + config.margin.top + config.margin.bottom;

    // 1. Add the SVG to the page and employ #2
    let svg = container.append("svg")
        .attr("width", width + config.margin.left + config.margin.right)
        .attr("height", height + config.margin.top + config.margin.bottom)
      .append("g")
        .attr("transform", "translate(" + config.margin.left + "," + config.margin.top + ")");

    // set up scales and ranges
    let x = d3.scaleLinear()
        .range([0, width]);
    let y = d3.scaleLinear()
        .range([height, 0]);

    // incr is 1 for lowx < highx, -1 for lowx > highx
    let lowx = config.xrange[0],
        highx = config.xrange[1],
        incr = (lowx < highx) ? 1 : -1;

    // 5. X scale will use the x of our data
    let bisectX = d3.bisector(function(d, x) {
        if (incr > 0) {
            return d.x - x;
        } else {
            return x - d.x;
        }
    }).left;
    x.domain([lowx, highx]);

    // see https://bl.ocks.org/d3noob/0e276dc70bb9184727ee47d6dd06e915
    let xAxis = d3.axisBottom(x)
        .tickSize(16);

    let yAxis = d3.axisLeft(y);

    // ydomaindata is concatenation of all data for y.domain(d3.extent),
    // used to determine y domain
    let ydomaindata = [];
    for (i=0; i<config.data.length; i++) {
        config.data[i].values.forEach(function(d) {
            // force number
            d.value = +d.value;
        });
        ydomaindata = ydomaindata.concat(config.data[i].values);
    };

    // seqdata is used to draw the paths so that there is a point for each number in the range
    let seqdata = [];
    for (let i=0; i<config.data.length; i++) {
        let linelabel = config.data[i].linelabel;
        let checkvalues = _.cloneDeep(config.data[i].values);
        let seqvalues = [];
        let currvalue = 0;
        let xrange = _.range(lowx, highx+incr, incr);
        for (let j=0; j<xrange.length; j++) {
            let thisx = xrange[j];
            while (checkvalues.length > 0
                    && ((incr > 0 && checkvalues[0].x <= thisx) || (incr < 0 && checkvalues[0].x >= thisx))) {
                let thisitem = checkvalues.shift();
                currvalue = thisitem.value;
            }
            seqvalues.push({x:thisx, value:currvalue});

            // break out after current sequence
            if (config.lastseq > 0 && ((incr > 0 && thisx >= config.lastseq) || (incr < 0 && thisx <= lastseq))) {
                break;
            }
        }
        seqdata.push( {linelabel: linelabel, values:seqvalues} );
    }


    // 6. Y scale will use the dataset values
    // force up to next boundary based on ytickincrement
    y.domain([0, Math.ceil(d3.max(ydomaindata, function(d) { return d.value })/config.ytickincrement )*config.ytickincrement]);

    // 3. Call the x axis in a group tag
    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        // see https://bl.ocks.org/d3noob/0e276dc70bb9184727ee47d6dd06e915
        .call(xAxis) // Create an axis component with d3.axisBottom
      // https://bl.ocks.org/d3noob/3c040800ff6457717cca586ae9547dbf
      .selectAll(".tick text")
        .style("text-anchor", "end")
        .attr("dx", "-.8em")
        .attr("dy", ".15em")
        .attr("transform", "rotate(-65)");

    // 4. Call the y axis in a group tag
    svg.append("g")
        .attr("class", "y axis")
        .call(yAxis); // Create an axis component with d3.axisLeft

    // y axis text
    svg.append("text")
        .attr("transform", "rotate(-90)")
        // x and y are flipped due to the rotation. see https://leanpub.com/d3-t-and-t-v4/read#leanpub-auto-the-y-axis-label
        .attr("y", 0 - config.margin.left)
        .attr("x", 0 - (height/2))
        .attr("dy", "1em")
        .style("text-anchor", "middle")
        .text(config.yaxislabel);

    // add heading if we have one
    svg.append("g")
        .attr("class", "heading")
      .append("text")
        .attr("transform", "translate(" + width/2 + ",-10)")
        .style("text-anchor", "middle")
        .text(config.chartheader);

    // 7. d3's line generator
    let line = d3.line()
        .x(function(d) {
            return x(d.x); // set the x values for the line generator
        })
        .y(function(d) {
            return y(d.value); // set the y values for the line generator
        });
        // .curve(d3.curveMonotoneX) // apply smoothing to the line

    colormap = [];
    for (i=0; i<seqdata.length; i++) {
        let linelabel = seqdata[i].linelabel
        colormap.push({'linelabel': linelabel, 'color': colorcycle[i % colorcycle.length]});

        svg.append("path")
            .style("stroke", colormap[i].color)
            .datum(seqdata[i].values)
            .attr("class", "line")
            .attr("d", line);

        // assure unique focusid per chart
        let thisfocus = svg.append("g")
            .attr("class", "focus")
            .attr("id", charts_get_focusid(config.containerselect, i))
            .style("display", "none");

        thisfocus.append("circle")
            .attr("r", 4.5);

        thisfocus.append("text")
            .style("text-anchor", "start")
            .attr("x", 4)
            .attr("y", 7)
            .attr("dy", ".35em");
    }

    let legend = svg.selectAll(".legend")
        .data(colormap)
      .enter().append("g")
        .attr("class", "legend")
        .attr("transform", function(d, i) { return "translate(" + i * 90 + ",0)"; });

    legend.append("rect")
        .attr("y", height + config.margin.bottom - 15)
        .attr("x", 60)
        .attr("width", 15)
        .attr("height", 15)
        .style("fill", function(d) { return d.color });

    legend.append("text")
        .attr("x", 15)
        .attr("y", height + config.margin.bottom - 15)
        .attr("dy", ".8em")
        .style("text-anchor", "bottom")
        .text(function(d) { return d.linelabel; });

    let mouseoverlay = svg.append("rect")
        .attr("class", "overlay")
        .attr("width", width + config.margin.right)
        .attr("height", height);

    let allfocus = d3.selectAll(".focus");
    mouseoverlay
      .on("mouseover", function() { allfocus.style("display", null); })
      .on("mouseout", function() { allfocus.style("display", "none"); })
      .on("mousemove", mousemove);

    function mousemove() {
        let x0 = x.invert(d3.mouse(this)[0]);
        for (let i=0; i<seqdata.length; i++) {
            let j = bisectX(seqdata[i].values, x0);
            let d;
            // use d0, d1 if in range
            if (j < seqdata[i].values.length) {
                let d0 = seqdata[i].values[j - 1],
                    d1 = seqdata[i].values[j];
                d = x0 - d0.x > d1.x - x0 ? d1 : d0;
            }
            else {
                d = seqdata[i].values[seqdata[i].values.length-1]
            }
            let thisfocus = d3.select('#'+charts_get_focusid(config.containerselect, i));
            thisfocus.attr("transform", "translate(" + x(d.x) + "," + y(d.value) + ")");
            thisfocus.select("text").text(d.x + " " + d.value);
            // console.log('d.x='+d.x+' d.value='+d.value+' x(d.x)='+x(d.x)+' y(d.value)='+y(d.value));
        }
    }

}
