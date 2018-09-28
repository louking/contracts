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
from loutilities.tables import CrudApi, DataTablesEditor
from flask import request, current_app

class parameterError(Exception): pass

#####################################################
class DteDbRelationship():
#####################################################
    '''
    define relationship for datatables editor db - form interface

    for relationships defined like
    class model()
        dbfield            = relationship( 'mappingmodel', backref='event', lazy=True )

    * model - name of model comprises list in dbfield
    * modelfield - field in model which is used to be displayed to the user
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

        children = DteDbRelationship(Child, 'name', 'children', 'children')
        
    '''
    def __init__(self, **kwargs):
        # the args dict has default values for arguments added by this class
        # caller supplied keyword args are used to update these
        # all arguments are made into attributes for self by the inherited class
        args = dict(model=None, 
                    modelfield=None,
                    formfield=None,
                    dbfield=None,
                    uselist=True,
                    searchbox=False,
                    )
        args.update(kwargs)

        # some of the args are required
        reqdfields = ['model', 'modelfield', 'formfield', 'dbfield']
        for field in reqdfields:
            if not args[field]:
                raise parameterError, '{} parameters are all required'.format(', '.join(reqdfields))

        # set arguments as class attributes
        for key in args:
            setattr(self, key, args[key])

    def set(self, formrow):
        if self.uselist:
            # return empty list if no items, rather than list with empty item
            itemnames = [this for this in formrow[self.formfield].split(',') if this]
            print 'itemnames={}'.format(itemnames)
            items = []
            for itemname in itemnames:
                queryfilter = {self.modelfield : itemname}
                thisitem = self.model.query.filter_by(**queryfilter).one()
                items.append( thisitem )
            return items
        else:
            itemname = formrow[self.formfield] if formrow[self.formfield] else None
            queryfilter = {self.modelfield : itemname}
            return self.model.query.filter_by(**queryfilter).one()

    def get(self, dbrow):
        if self.uselist:
            return ','.join(getattr(item, self.modelfield) for item in getattr(dbrow, self.dbfield))
        else:
            return getattr(getattr(dbrow, self.dbfield), self.modelfield)

    def options(self):
        return [getattr(item, self.modelfield) for item in self.model.query.all()]

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
    def __init__(self, **kwargs):
        # the args dict has default values for arguments added by this class
        # caller supplied keyword args are used to update these
        # all arguments are made into attributes for self by the inherited class
        args = dict(formfield=None, 
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

    def get(self, dbrow):
        return self.truedisplay if getattr(dbrow, self.dbfield) else self.falsedisplay

    def set(self, formrow):
        return formrow[self.formfield] == self.truedisplay

    def options(self):
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
                * relationship - {DteDbRelationship keyword parameters}

        **servercolumns** - if present table will be displayed through ajax get calls

    '''

    # class specific imports here so users of other classes do not need to install

    def __init__(self, **kwargs):
        current_app.logger.debug('DbCrudApi.__init__()')

        # the args dict has default values for arguments added by this derived class
        # caller supplied keyword args are used to update these
        # all arguments are made into attributes for self by the inherited class
        args = dict(db = None, 
                    model = None,
                    dbmapping = {},
                    formmapping = {},
                    queryparams = {},
                    dtoptions = {},
                    )
        args.update(kwargs)

        super(DbCrudApi, self).__init__(**args)

        self.pagejsfiles = ['datatables.js'] + self.pagejsfiles

        # do some preprocessing on columns
        self.booleandb = {}
        self.booleanform = {}
        self.relationshipdb = {}
        self.relationshipform = {}
        for col in self.clientcolumns:
            # remove readonly fields from dbmapping
            if col.get('type',None) == 'readonly':
                self.dbmapping.pop(col['name'], None)
            
            # handle special treatment for column
            treatment = col.pop('_treatment', None)
            if treatment:
                if type(treatment) != dict or len(treatment) != 1 or treatment.keys()[0] not in ['boolean', 'relationship']:
                    raise parameterError, 'invalid treatment: {}'.format(treatment)

                # handle boolean treatment
                if 'boolean' in treatment:
                    thisbool = DteDbBool(**treatment['boolean'])
                    col['type'] = 'select2'
                    col['opts'] = { 'minimumResultsForSearch': 'Infinity' }
                    # get original formfield and dbattr
                    formfield = col['name'] # TODO: should this come from 'name' or 'data'?
                    dbattr = self.formmapping[formfield]    # need to collect dbattr name before updating self.formmapping
                    # form processing section
                    ## save handler, get data from form using handler get function, update form to call handler options when options needed
                    self.booleanform[formfield] = thisbool
                    self.formmapping[formfield] = self.booleanform[formfield].get
                    col['options'] = self.booleanform[formfield].options
                    # db processing section
                    ## save handler, set data to db using handler set function
                    self.booleandb[dbattr] = thisbool
                    self.dbmapping[dbattr] = self.booleandb[dbattr].set

                # handle relationship treatment
                if 'relationship' in treatment:
                    thisbool = DteDbRelationship(**treatment['relationship'])
                    col['type'] = 'select2'
                    col['opts'] = { 'minimumResultsForSearch': 0 if thisbool.searchbox else 'Infinity', 'multiple':thisbool.uselist }
                    if thisbool.uselist:
                        col['separator'] = ','
                    # get original formfield and dbattr
                    formfield = col['data'] # TODO: should this come from 'name' or 'data'?
                    dbattr = self.formmapping[formfield]    # need to collect dbattr name before updating self.formmapping
                    # form processing section
                    ## save handler, get data from form using handler get function, update form to call handler options when options needed
                    self.booleanform[formfield] = thisbool
                    self.formmapping[formfield] = self.booleanform[formfield].get
                    col['options'] = self.booleanform[formfield].options
                    # db processing section
                    ## save handler, set data to db using handler set function
                    self.booleandb[dbattr] = thisbool
                    self.dbmapping[dbattr] = self.booleandb[dbattr].set

        # set up mapping between database and editor form
        # Note: translate '' to None and visa versa
        self.dte = DataTablesEditor(self.dbmapping, self.formmapping, null2emptystring=True)

    def open(self):
        '''
        retrieve all the data in the indicated table
        '''
        current_app.logger.debug('DbCrudApi.open()')
        current_app.logger.debug('DbCrudApi.open: self.db = {}, self.model = {}'.format(self.db, self.model))

        # pull in the data
        query = self.model.query.filter_by(**self.queryparams)
        self.rows = iter(query.all())

        # THIS CAN'T BE CALLED FROM self._renderpage
        # params = request.args.to_dict()
        # rowTable = self.DataTables(params, query, self.servercolumns)
        # self.outputResult = rowTable.output_result()

    def nexttablerow(self):
        '''
        since open has done all the work, tell the caller we're done
        '''
        current_app.logger.debug('DbCrudApi.nexttablerow()')

        dbrecord = self.rows.next()
        return self.dte.get_response_data(dbrecord)

    def close(self):
        current_app.logger.debug('DbCrudApi.close()')
        pass

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
        self.dte.set_dbrow(formdata, dbrow)
        current_app.logger.debug('creating dbrow={}'.format(dbrow.__dict__))
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
        # edit item
        dbrow = self.model.query.filter_by(id=thisid).one()
        current_app.logger.debug('editing id={} dbrow={}'.format(thisid, dbrow.__dict__))
        self.dte.set_dbrow(formdata, dbrow)
        current_app.logger.debug('after edit id={} dbrow={}'.format(thisid, dbrow.__dict__))

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
        current_app.logger.debug('deleting id={} dbrow={}'.format(thisid, dbrow.__dict__))
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

    def __init__(self, **kwargs):
        current_app.logger.debug('DbCrudApiRolePermissions.__init__()')

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

    def permission(self):
        '''
        determine if current user is permitted to use the view
        '''
        current_app.logger.debug('DbCrudApiRolePermissions.permission()')
        current_app.logger.debug('permission: roles_accepted = {} roles_required = {}'.format(self.roles_accepted, self.roles_required))

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


