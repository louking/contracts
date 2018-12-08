###########################################################################################
# crudapi - CRUD api for this application
#
#       Date            Author          Reason
#       ----            ------          ------
#       07/09/18        Lou King        Create
#
#   Copyright 2018 Lou King
#
###########################################################################################
'''
crudapi - CRUD api for this application
=========================================
'''

# standard
from urllib import urlencode
from json import dumps
from copy import deepcopy

# pypi
from flask import request, current_app, make_response, url_for, jsonify
from datatables import DataTables, ColumnDT
from sqlalchemy import func

# home grown
from loutilities.tables import CrudApi, DataTablesEditor

class parameterError(Exception): pass

# separator for select2 tag list
SEPARATOR = ', '

debug = True

#####################################################
class DteDbRelationship():
#####################################################
    '''
    define relationship for datatables editor db - form interface

    for relationships defined like
    class model()
        dbfield            = relationship( 'mappingmodel', backref=tablemodel, lazy=True )

    * tablemodel - name of model for the table
    * fieldmodel - name of model comprises list in dbfield
    * labelfield - field in model which is used to be displayed to the user
    * valuefield - field in model which is used as value for select and to retrieve record, passed on Editor interface, default 'id' - needs to be a key for model record
    * formfield - field as used on the form
    * dbfield - field as used in the database table (not the model -- this is field in table which has list of model items)
    * uselist - set to True if using tags, otherwise field expects single entry, default True
    * searchbox - set to True if searchbox desired, default False

    e.g.,
        class Parent(Base):
            __tablename__ = 'parent'
            id = Column(Integer, primary_key=True)
            child_id = Column(Integer, ForeignKey('child.id'))
            child = relationship("Child", backref="parents")

        class Child(Base):
            __tablename__ = 'child'
            name = Column(String)
            id = Column(Integer, primary_key=True)

        TODO: add more detail here -- this is confusing

        children = DteDbRelationship(tablemodel=Parent, fieldmodel=Child, labelfield='name', formfield='children', dbfield='children')
    '''
    #----------------------------------------------------------------------
    def __init__(self, **kwargs):
    #----------------------------------------------------------------------
        # the args dict has default values for arguments added by this class
        # caller supplied keyword args are used to update these
        # all arguments are made into attributes for self by the inherited class
        args = dict(tablemodel=None,
                    fieldmodel=None, 
                    labelfield=None,
                    valuefield ='id',
                    formfield=None,
                    dbfield=None,
                    uselist=True,
                    searchbox=False,    # TODO: is this needed?
                    )
        args.update(kwargs)

        # some of the args are required
        reqdfields = ['fieldmodel', 'labelfield', 'formfield', 'dbfield']
        for field in reqdfields:
            if not args[field]:
                raise parameterError, '{} parameters are all required'.format(', '.join(reqdfields))

        # set arguments as class attributes
        for key in args:
            setattr(self, key, args[key])

    #----------------------------------------------------------------------
    def set(self, formrow):
    #----------------------------------------------------------------------
        # set database from form
        if self.uselist:
            # accumulate list of database model instances
            items = []

            # return empty list if no items, rather than list with empty item
            # this allows for multiple keys in formrow[self.formfield], but seems like there'd only be one
            itemvalues = []
            for key in formrow[self.formfield]:
                vallist = formrow[self.formfield][key].split(SEPARATOR)
                # empty list is actually null list with one entry
                if len(vallist) == 1 and not vallist[0]: continue
                # loop through nonempty entries -- will we ever see null entry? hope not else exception on .one() call below
                for ndx in range(len(vallist)):
                    if len(itemvalues) < ndx+1:
                        itemvalues.append({key:vallist[ndx]})
                    else:
                        itemvalues[ndx].update({key:vallist[ndx]})
            if debug: current_app.logger.debug( 'itemvalues={}'.format(itemvalues) )
            for itemvalue in itemvalues:
                queryfilter = itemvalue
                # queryfilter = {self.valuefield : itemvalue}
                thisitem = self.fieldmodel.query.filter_by(**queryfilter).one()
                items.append(thisitem)
            return items
        else:
            itemvalue = formrow[self.formfield] if formrow[self.formfield] else None
            queryfilter = itemvalue
            # queryfilter = {self.valuefield : itemvalue}
            thisitem = self.fieldmodel.query.filter_by(**queryfilter).one_or_none()
            return thisitem

    #----------------------------------------------------------------------
    def get(self, dbrow_or_id):
    #----------------------------------------------------------------------
        # check if id supplied, if so retrieve dbrow
        if type(dbrow_or_id) in [int, str]:
            dbrow = self.tablemodel.query().filter_by(id=dbrow_or_id).one()
        else:
            dbrow = dbrow_or_id

        # get from database to form
        if self.uselist:
            items = {}
            labelitems = []
            valueitems = []
            for item in getattr(dbrow, self.dbfield):
                labelitems.append( str( getattr( item, self.labelfield ) ) )
                valueitems.append( str( getattr( item, self.valuefield ) ) )
            items = { self.labelfield:SEPARATOR.join(labelitems), self.valuefield:SEPARATOR.join(valueitems) }
            return items
        else:
            # get the attribute if specified
            if getattr(dbrow, self.dbfield):
                item = { self.labelfield:getattr(getattr(dbrow, self.dbfield), self.labelfield), 
                         self.valuefield:getattr(getattr(dbrow, self.dbfield), self.valuefield) }
                return item
            # otherwise return None
            else:
                return { self.labelfield:None, self.valuefield:None }

    #----------------------------------------------------------------------
    def options(self):
    #----------------------------------------------------------------------
        # return sorted list of items in the model
        items = [{'label': getattr(item, self.labelfield), 'value': item.id} for item in self.fieldmodel.query.all()]
        items.sort(key=lambda k: k['label'].lower())
        return items

    #----------------------------------------------------------------------
    def new_plus_options(self):
    #----------------------------------------------------------------------
        # return sorted list of items in the model
        items = [{'label': '<new>', 'value': 0}] + self.options()
        return items

#####################################################
class DteDbBool():
#####################################################
    '''
    define helpers for boolean fields

    * formfield - field as used on the form
    * dbfield - field as used in the database
    * truedisplay - how to display True to user (default 'yes')
    * falsedisplay - hot to display False to user (default 'no')
    '''
    #----------------------------------------------------------------------
    def __init__(self, **kwargs):
    #----------------------------------------------------------------------
        # the args dict has default values for arguments added by this class
        # caller supplied keyword args are used to update these
        # all arguments are made into attributes for self by the inherited class
        args = dict(tablemodel=None,
                    formfield=None, 
                    dbfield=None,
                    truedisplay='yes',
                    falsedisplay='no',
                    )
        args.update(kwargs)

        # some of the args are required
        reqdfields = ['formfield', 'dbfield']
        for field in reqdfields:
            if not args[field]:
                raise parameterError, '{} parameters are all required'.format(', '.join(reqdfields))

        # set arguments as class attributes
        for key in args:
            setattr(self, key, args[key])

    #----------------------------------------------------------------------
    def get(self, dbrow_or_id):
    #----------------------------------------------------------------------
        """get from database for form"""
        # check if id supplied, if so retrieve dbrow
        if type(dbrow_or_id) in [int, str]:
            dbrow = self.tablemodel.query().filter_by(id=dbrow_or_id).one()
        else:
            dbrow = dbrow_or_id

        return self.truedisplay if getattr(dbrow, self.dbfield) else self.falsedisplay

    #----------------------------------------------------------------------
    def set(self, formrow):
    #----------------------------------------------------------------------
        """set to database from form"""
        return formrow[self.formfield] == self.truedisplay

    #----------------------------------------------------------------------
    def options(self):
    #----------------------------------------------------------------------
        return [{'label':self.truedisplay,'value':self.truedisplay}, {'label':self.falsedisplay, 'value':self.falsedisplay}]

#####################################################
class DbCrudApi(CrudApi):
#####################################################
    '''
    This class extends CrudApi. This extension uses sqlalchemy to read / write to a database

    Additional parameters for this class:

        db: database object a la sqlalchemy
        model: sqlalchemy model for the table to read/write from
        dbmapping: mapping dict with key for each db field, value is key in form or function(dbentry)
        formmapping: mapping dict with key for each form row, value is key in db row or function(form)
        queryparms: dict of query parameters relevant to this table to retrieve table or rows
        dtoptions: datatables options to override / add

        **dbmapping** is dict like {'dbattr_n':'formfield_n', 'dbattr_m':f(form), ...}
        **formmapping** is dict like {'formfield_n':'dbattr_n', 'formfield_m':f(dbrow), ...}
        if order of operation is important for either of these use OrderedDict

        **clientcolumns** should be like the following. See https://datatables.net/reference/option/columns and 
        https://editor.datatables.net/reference/option/fields for more information
            [
                { 'data': 'service', 'name': 'service', 'label': 'Service Name' },
                { 'data': 'key', 'name': 'key', 'label': 'Key', 'render':'$.fn.dataTable.render.text()' }, 
                { 'data': 'secret', 'name': 'secret', 'label': 'Secret', 'render':'$.fn.dataTable.render.text()' },
                { 'data': 'service', 'name': 'service_id', 
                  'label': 'Service Name',
                  'type': 'selectize', 
                  'options': [{'label':'yes', 'value':1}, {'label':'no', 'value':0}],
                  'opts': { 
                    'searchField': 'label',
                    'openOnFocus': False
                   },
                  '_update' {
                    'endpoint' : <url endpoint to retrieve options from>,
                    'on' : <event>
                    'wrapper' : <wrapper for query response>
                  }
                },
            ]
            * name - describes the column and is used within javascript
            * data - used on server-client interface and should be used in the formmapping key and dbmapping value
            * label - used for the DataTable table column and the Editor form label 
            * optional render key is eval'd into javascript
            * id - is specified by idSrc, and should be in the mapping function but not columns

            additionally the update option can be used to _update the options for any type = 'select', 'selectize'
            * _update - dict with following keys
                * endpoint - url endpoint to retrieve new options 
                * on - event which triggers update. supported events are
                    * 'open' - triggered when form opens (actually when field is focused)
                    * 'change' - triggered when field changes - use wrapper to indicate what field(s) are updated
                * wrapper - dict which is wrapped around query response. value '_response_' indicates where query response should be placed
        
            * _treatment - dict with (only) one of following keys - note this causes override of dbmapping and formmapping configuration
                * boolean - {DteDbBool keyword parameters}
                * relationship - {DteDbRelationship keyword parameters, 'editable' : { 'api':<DbCrudApi()> }}
                    'editable' is set only if it is desired to bring up a form to edit the underlying model row

            * _ColumnDT_args - dict with keyword arguments passed to ColumnDT for serverside processing

        **serverside** - if present table will be displayed through ajax get calls

    '''

    # class specific imports here so users of other classes do not need to install

    #----------------------------------------------------------------------
    def __init__(self, **kwargs):
    #----------------------------------------------------------------------
        if debug: current_app.logger.debug('DbCrudApi.__init__()')

        # the args dict has default values for arguments added by this derived class
        # caller supplied keyword args are used to update these
        # all arguments are made into attributes for self by the inherited class
        args = dict(db = None, 
                    model = None,
                    dbmapping = {},
                    formmapping = {},
                    serverside = False, # duplicated here and in CrudApi because test before super() called
                    queryparams = {},
                    dtoptions = {},
                    filtercoloptions = [],
                    )
        args.update(kwargs)

        # make sure '_treatment', '_unique' and '_ColumnDT_args' column options are removed before invoking DataTables and Editor
        args['filtercoloptions'] += ['_treatment', '_unique', '_ColumnDT_args']

        # make copy of dbmapping and formmapping
        # Need to do this because we update the mapping with functions. 
        # view class gets reinstantiated when page painted, so we'll need to make sure we
        # don't corrupt the original data
        self.formmapping = deepcopy(args['formmapping'])
        self.dbmapping = deepcopy(args['dbmapping'])

        # keep track of columns which must be unique in the database
        self.uniquecols = []

        # for serverside processing, self.servercolumns is built up from column data, always starts with model.id
        if args['serverside']:
            self.servercolumns = [ColumnDT(getattr(args['model'], 'id'), mData=self.dbmapping['id'])]

        # do some preprocessing on columns
        booleandb = {}
        booleanform = {}
        saforms = []
        for col in args['clientcolumns']:
            if debug: current_app.logger.debug('__init__(): col = {}'.format(col))
            # remove readonly fields from dbmapping
            if col.get('type',None) == 'readonly':
                self.dbmapping.pop(col['name'], None)
            
            # need formfield and dbattr for a couple of things
            formfield = col['name'] # TODO: should this come from 'name' or 'data'?
            dbattr = self.formmapping[formfield]

            # maybe this column needs to be unique
            if col.get('_unique', False):
                self.uniquecols.append(dbattr)

            # check for special treatment for column
            treatment = col.get('_treatment', None)
            columndt_args = col.get('_ColumnDT_args', {})
            if debug: current_app.logger.debug('__init__(): treatment = {}'.format(treatment))

            # no special treatment is the norm
            if not treatment:
                if args['serverside']:
                    self.servercolumns.append( ColumnDT(getattr(args['model'], dbattr), mData=formfield, **columndt_args) )
            
            # special treatment required
            else:
                if type(treatment) != dict or len(treatment) != 1 or treatment.keys()[0] not in ['boolean', 'relationship']:
                    raise parameterError, 'invalid treatment: {}'.format(treatment)

                # handle boolean treatment
                if 'boolean' in treatment:
                    thisbool = DteDbBool(tablemodel=args['model'], **treatment['boolean'])
                    col['type'] = 'select2'
                    col['opts'] = { 'minimumResultsForSearch': 'Infinity' }

                    # form processing section
                    ## save handler, get data from database using handler get function, update form to call handler options when options needed
                    booleanform[formfield] = thisbool
                    col['options'] = booleanform[formfield].options

                    # client side table modifies getter to handle boolean values
                    if not args['serverside']:
                        self.formmapping[formfield] = booleanform[formfield].get

                    # server side tables adds ColumnDT to handle boolean values
                    else:
                        self.servercolumns.append( ColumnDT( func.thisbool.get(getattr(thisbool.tablemodel, 'id')) , mData=formfield, **columndt_args) )                        

                    # db processing section
                    ## save handler, set data to db using handler set function
                    booleandb[dbattr] = thisbool
                    self.dbmapping[dbattr] = booleandb[dbattr].set

                # handle relationship treatment
                if 'relationship' in treatment:
                    # now create the relationship
                    thisreln = DteDbRelationship(tablemodel=args['model'], **treatment['relationship'])
                    col['type'] = 'select2'
                    col['opts'] = { 'minimumResultsForSearch': 0 if thisreln.searchbox else 'Infinity', 
                                    'multiple':thisreln.uselist, 
                                    'placeholder': None if thisreln.uselist else '(select)' }
                    if thisreln.uselist:
                        col['separator'] = SEPARATOR
                    # get original formfield and dbattr
                    # TODO: should this come from 'name' or 'data'?
                    ## actually name and data should be the same value, name for editor and data for datatable
                    ## see https://editor.datatables.net/examples/simple/join.html

                    # form processing section
                    ## save handler, get data from form using handler get function, update form to call handler options when options needed
                    # relationshipform[formfield] = thisreln

                    # client side table modifies getter to handle boolean values
                    if not args['serverside']:
                        self.formmapping[formfield] = thisreln.get

                    # server side tables adds ColumnDT to handle boolean values
                    else:
                        # TODO: maybe need to do something with {formfield : {'id': xx, label: yy}} or maybe this will just work?
                        self.servercolumns.append( ColumnDT(func.thisreln.get(getattr(thisreln.tablemodel, 'id')) , mData=formfield, **columndt_args))

                    # db processing section
                    ## save handler, set data to db using handler set function
                    self.dbmapping[dbattr] = thisreln.set
                    
                    ## if this field needs form for editing the record it points at, remember information
                    ## also add <new> option
                    editable = treatment['relationship'].get('editable', {})
                    if debug: current_app.logger.debug('__init__(): labelfield={} editable={}'.format(treatment['relationship']['labelfield'], editable))
                    valuefield = 'id' if 'valuefield' not in treatment['relationship'] else treatment['relationship']['valuefield']
                    if editable:
                        saforms.append({ 'api':editable['api'], 'args': { 'name':treatment['relationship']['labelfield'], 'valuefield':valuefield } })
                        col['options'] = thisreln.new_plus_options
                    else:
                        col['options'] = thisreln.options
                        col['options'] = thisreln.options

                    # convert this column for dt and ed configuration
                    # this conversion happens with super(DbCrudApi, self).__init__(**args) 
                    # column attributes are updated based on 'dtonly', 'edonly' at very end of initialization
                    if 'data' in col:
                        col.setdefault('dt', {}).update({'data':'{}.{}'.format(col['data'],thisreln.labelfield)})
                        col.setdefault('ed', {}).update({'data':'{}.{}'.format(col['data'],thisreln.valuefield)})
                    if 'name' in col:
                        col.setdefault('dt', {}).update({'name':'{}.{}'.format(col['name'],thisreln.labelfield)})
                        col.setdefault('ed', {}).update({'name':'{}.{}'.format(col['name'],thisreln.valuefield)})

        # from pprint import PrettyPrinter
        # pp = PrettyPrinter()
        # if debug: current_app.logger.debug('args["columns"]={}'.format(pp.pformat(args['clientcolumns'])))

        # set up mapping between database and editor form
        # Note: translate '' to None and visa versa
        self.dte = DataTablesEditor(self.dbmapping, self.formmapping, null2emptystring=True)

        # initialize inherited class, and a couple of attributes
        super(DbCrudApi, self).__init__(**args)

        # if any standalone forms required, add to templateargs
        if saforms:
            self.templateargs['saformjsurls'] = lambda: [ saf['api'].saformurl(**saf['args']) for saf in saforms ]

        # save caller's validation method and update validation to local version
        self.callervalidate = self.validate
        self.validate = self.validatedb
        if debug: current_app.logger.debug('updated validate() to validatedb()')

    #----------------------------------------------------------------------
    def get(self):
    #----------------------------------------------------------------------
        
        # this returns editor options for this model class
        # this can be used to have a create or edit form accessed from any type of view
        if request.path[-7:] == '/saform':
            edoptions = self.getedoptions()
            return jsonify( { 'edoptions' : edoptions } )

        # this allows standalone editor form to be created for this model class from another model class
        # through a select2 control on a datatables view
        # NOTE: request.args need to match keyword args in self.saformurl()
        elif request.path[-9:] == '/saformjs':
            ed_options = self.getedoptions()

            # indent all by 4 and use indent=2 to make debugging easy
            edoptsjson = ['    {}'.format(l) for l in dumps(ed_options, indent=2).split('\n')]

            labelfield = request.args['name']
            valuefield = request.args['valuefield']
            js  = [
                   # 'var row;',
                   'var {}_{}_lastval;'.format(labelfield, valuefield),
                   '',
                   'if ( typeof openeditor == "undefined" ) {',
                   '    function openeditor() {',
                   '      editor.open( );',
                   # TODO: need fix for #25
                   '    }',
                   '',
                   '    function closeeditor() {',
                   '      editor.close()',
                   '    }',
                   '}',
                   '',
                   '$( function () {', 
                   '  // handle save, then open editor on submit',
                   '  var fieldname = "{}.{}"'.format(labelfield, valuefield),
                   '  $( editor.field( fieldname ).input() ).on ("select2:open", function () {', 
                   '    {}_{}_lastval = editor.get( fieldname );'.format(labelfield, valuefield),
                   '  } );',
                   '  $( editor.field( fieldname ).input() ).on ("change", function () {', 
                   '    console.log("{} select2 change fired");'.format(labelfield), 
                   '    console.log("editor.get() = " + editor.get( fieldname ));', 
                   '    // only fire if <new> entry',
                   '    if ( editor.get( fieldname ) != 0 ) return;',
                   '',
                   '    closeeditor();', 
                   '',
                   '    {}_editor'.format(labelfield), 
                   '      .buttons( [', 
                   '                 {', 
                   '                  label: "Cancel",', 
                   '                  fn: function () {', 
                   '                        this.close();', 
                   # this is needed here and also on close
                   '                        editor.field( fieldname ).set( {}_{}_lastval );'.format(labelfield, valuefield),
                   '                        openeditor( );', 
                   '                  },', 
                   '                 },', 
                   '                 {', 
                   '                  label: "Create",', 
                   '                  fn: function () {', 
                   '                        this.submit( function(resp) {',
                   '                              this.close();', 
                   '                              openeditor( );', 
                   '                              var newval = {{label:resp.data[0].{}, value:resp.data[0].{}}};'.format(labelfield,self.idSrc),
                   '                              console.log( "newval = " + newval );',
                   '                              editor.field( fieldname ).AddOption( [ newval ] );',
                   '                              editor.field( fieldname ).set( newval.value );',
                   '                           },',
                   '                        )',
                   '                  },', 
                   '                 },', 
                   '                ]', 
                   '      )', 
                   '      .create();', 
                   '  } );',
                   '',
                   '  {}_editor = new $.fn.dataTable.Editor( '.format(labelfield),
            ]

            js += edoptsjson

            js += [
                   '  );',
                   '  // if form closes, reopen editor',
                   '  {}_editor'.format(labelfield),
                   '    .on("close", function () {',
                   # this is needed here and also when cancel button is pressed
                   '      editor.field( fieldname ).set( {}_{}_lastval );'.format(labelfield, valuefield),
                   '      openeditor( );',
                   '  });',
                   '} );',
            ]
            # see https://stackoverflow.com/questions/11017466/flask-return-image-created-from-database
            response = make_response('\n'.join(js))
            response.headers.set('Content-Type', 'application/javascript')            
            return response

        # otherwise handle get from base class
        else:
            return super(DbCrudApi, self).get()

    #----------------------------------------------------------------------
    def saformurl(self, **kwargs):
    #----------------------------------------------------------------------
        '''
        standalone form url
        '''
        # NOTE: keyword arguments need to match request.args access in self.get()
        args = urlencode(kwargs)
        # self.__name__ is endpoint -- see https://github.com/pallets/flask/blob/master/flask/views.py View.as_view method
        url = '{}/saformjs?{}'.format(url_for('.'+self.my_view.__name__), args)
        return url
    
    #----------------------------------------------------------------------
    def register(self):
    #----------------------------------------------------------------------
        # name for view is last bit of fully named endpoint
        name = self.endpoint.split('.')[-1]

        # create the inherited class endpoints, as by product my_view attribute is initialized
        super(DbCrudApi, self).register()
        self.app.add_url_rule('{}/saformjs'.format(self.rule),view_func=self.my_view,methods=['GET',])
        self.app.add_url_rule('{}/saform'.format(self.rule),view_func=self.my_view,methods=['GET',])

    #----------------------------------------------------------------------
    def open(self):
    #----------------------------------------------------------------------
        '''
        retrieve all the data in the indicated table
        '''
        if debug: current_app.logger.debug('DbCrudApi.open()')
        if debug: current_app.logger.debug('DbCrudApi.open: self.db = {}, self.model = {}'.format(self.db, self.model))

        # pull in the data
        query = self.model.query.filter_by(**self.queryparams)

        # not server table, rows will be handled in nexttablerow()
        if not self.serverside:
            self.rows = iter(query.all())
        
        # server table, this is the output to be returned, nexttablerow() is noop
        # note get_response_data transform is not done - name mapping is in self.servercolumns
        else:
            rowTable = DataTables(request.args.to_dict(), query, self.servercolumns)

            output = rowTable.output_result()
            print output

            # check for errors
            if 'error' in output:
                raise parameterError, output['error']

            # # transform rowTable.output_result()['data'] using get_response_data
            # ## loop through data
            # data = output['data']
            # for i in range(len(data)):
            #     rowobj = Dictate(data[i])
            #     newdict = {}
            #     self.dte.get_response_data(rowobj, newdict)
            #     data[i] = newdict

            self.output_result = output

    #----------------------------------------------------------------------
    def nexttablerow(self):
    #----------------------------------------------------------------------
        '''
        since open has done all the work, tell the caller we're done
        '''
        if debug: current_app.logger.debug('DbCrudApi.nexttablerow()')

        # not server table, need to do translation
        if not self.serverside:
            dbrecord = self.rows.next()
            return self.dte.get_response_data(dbrecord)

        # server table
        else:
            # nothing to do, all done in open()
            raise StopIteration

    #----------------------------------------------------------------------
    def close(self):
    #----------------------------------------------------------------------
        if debug: current_app.logger.debug('DbCrudApi.close()')
        pass

    #----------------------------------------------------------------------
    def validatedb(self, action, formdata):
    #----------------------------------------------------------------------
        if debug: current_app.logger.debug('DbCrudApi.validatedb({})'.format(action))

        # check results of caller's validation
        results = self.callervalidate( action, formdata )

        # check if any records conflict with uniqueness requirements
        if action == 'create' and self.uniquecols:
            dbrow = self.model()
            self.dte.set_dbrow(formdata, dbrow)
            for field in self.uniquecols:
                # if debug: current_app.logger.debug('DbCrudApi.validatedb(): checking field "{}":"{}"'.format(field,getattr(dbrow,field)))
                row = self.model.query.filter_by(**{field:getattr(dbrow,field)}).one_or_none()
                # if we found a row that matches, flag error

                if row:
                    results.append({ 'name' : field, 'status' : 'duplicate found, must be unique' })

        return results

    #----------------------------------------------------------------------
    def createrow(self, formdata):
    #----------------------------------------------------------------------
        '''
        creates row in database
        
        :param formdata: data from create form
        :rtype: returned row for rendering, e.g., from DataTablesEditor.get_response_data()
        '''
        # create item
        dbrow = self.model()
        if debug: current_app.logger.debug('createrow(): self.dbmapping = {}'.format(self.dbmapping))
        self.dte.set_dbrow(formdata, dbrow)
        if debug: current_app.logger.debug('createrow(): creating dbrow={}'.format(dbrow.__dict__))
        self.db.session.add(dbrow)
        self.db.session.flush()

        # prepare response
        thisrow = self.dte.get_response_data(dbrow)
        return thisrow

    #----------------------------------------------------------------------
    def updaterow(self, thisid, formdata):
    #----------------------------------------------------------------------
        '''
        updates row in database
        
        :param thisid: id of row to be updated
        :param formdata: data from create form
        :rtype: returned row for rendering, e.g., from DataTablesEditor.get_response_data()
        '''
        if debug: current_app.logger.debug('updaterow({},{})'.format(thisid, formdata))

        # edit item
        dbrow = self.model.query.filter_by(id=thisid).one()
        if debug: current_app.logger.debug('editing id={} dbrow={}'.format(thisid, dbrow.__dict__))
        self.dte.set_dbrow(formdata, dbrow)
        if debug: current_app.logger.debug('after edit id={} dbrow={}'.format(thisid, dbrow.__dict__))

        # prepare response
        thisrow = self.dte.get_response_data(dbrow)
        return thisrow

    #----------------------------------------------------------------------
    def deleterow(self, thisid):
    #----------------------------------------------------------------------
        '''
        deletes row in database
        
        :param thisid: id of row to be updated
        :rtype: returned row for rendering, e.g., from DataTablesEditor.get_response_data()
        '''
        dbrow = self.model.query.filter_by(id=thisid).one()
        if debug: current_app.logger.debug('deleting id={} dbrow={}'.format(thisid, dbrow.__dict__))
        self.db.session.delete(dbrow)

        return []

    #----------------------------------------------------------------------
    def commit(self):
    #----------------------------------------------------------------------
        self.db.session.commit()

    #----------------------------------------------------------------------
    def rollback(self):
    #----------------------------------------------------------------------
        self.db.session.rollback()

#####################################################
class DbCrudApiRolePermissions(DbCrudApi):
#####################################################
    '''
    This class extends DbCrudApi which, in turn, extends CrudApi. This extension uses flask_security
    to do role checking for the current user.

    Caller should use roles_accepted OR roles_required but not both.

    Additional parameters for this class:

        roles_accepted: None, 'role', ['role1', 'role2', ...] - user must have at least one of the specified roles
        roles_required: None, 'role', ['role1', 'role2', ...] - user must have all of the specified roles
    '''
    from flask_security import current_user

    #----------------------------------------------------------------------
    def __init__(self, **kwargs):
    #----------------------------------------------------------------------
        if debug: current_app.logger.debug('DbCrudApiRolePermissions.__init__()')

        # the args dict has default values for arguments added by this derived class
        # caller supplied keyword args are used to update these
        # all arguments are made into attributes for self by the inherited class
        args = dict(roles_accepted=None, roles_required=None)
        args.update(kwargs)

        # this initialization needs to be done before checking any self.xxx attributes
        super(DbCrudApiRolePermissions, self).__init__(**args)

        # Caller should use roles_accepted OR roles_required but not both
        if self.roles_accepted and self.roles_required:
            raise parameterError, 'use roles_accepted OR roles_required but not both'

        # assure None or [ 'role1', ... ]
        if self.roles_accepted and type(self.roles_accepted) != list:
            self.roles_accepted = [ self.roles_accepted ]
        if self.roles_required and type(self.roles_required) != list:
            self.roles_required = [ self.roles_required ]

    #----------------------------------------------------------------------
    def permission(self):
    #----------------------------------------------------------------------
        '''
        determine if current user is permitted to use the view
        '''
        if debug: current_app.logger.debug('DbCrudApiRolePermissions.permission()')
        if debug: current_app.logger.debug('permission: roles_accepted = {} roles_required = {}'.format(self.roles_accepted, self.roles_required))

        # if no roles are asked for, permission granted
        if not self.roles_accepted and not self.roles_required:
            allowed = True

        # if user has any of the roles_accepted, permission granted
        elif self.roles_accepted:
            allowed = False
            for role in self.roles_accepted:
                if self.current_user.has_role(role):
                    allowed = True
                    break

        # if user has all of the roles_required, permission granted
        elif self.roles_required:
            allowed = True
            for role in self.roles_required:
                if not self.current_user.has_role(role):
                    allowed = False
                    break
        
        return allowed


