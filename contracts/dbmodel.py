###########################################################################################
# dbmodel - database model for racesupportcontracts database
#
#       Date            Author          Reason
#       ----            ------          ------
#       06/29/18        Lou King        Create
#
#   Copyright 2018 Lou King.  All rights reserved
###########################################################################################

# standard
import os.path
from ConfigParser import SafeConfigParser

# pypi
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from flask_sqlalchemy import SQLAlchemy
from flask_security import current_user, UserMixin, RoleMixin
from flask_dance.consumer.backend.sqla import OAuthConsumerMixin

# set up database - SQLAlchemy() must be done after app.config SQLALCHEMY_* assignments
db = SQLAlchemy()
Table = db.Table
Column = db.Column
Integer = db.Integer
Float = db.Float
Boolean = db.Boolean
String = db.String
Date = db.Date
Time = db.Time
DateTime = db.DateTime
Sequence = db.Sequence
Enum = db.Enum
UniqueConstraint = db.UniqueConstraint
ForeignKey = db.ForeignKey
relationship = db.relationship
backref = db.backref
object_mapper = db.object_mapper
Base = db.Model

# some string sizes
URL_LEN = 2047      # https://stackoverflow.com/questions/417142/what-is-the-maximum-length-of-a-url-in-different-browsers
EVENT_LEN = 256
DATE_LEN = 10
TIME_LEN = 5
DATETIME_LEN = DATE_LEN + 1 + TIME_LEN
STATE_LEN = 16
NAME_LEN = 256
EMAIL_LEN = 100
SERVICE_LEN = 20
FIELD_LEN = 30
COURSE_LEN = 50
ROLENAME_LEN = 32
ADDRESS_LEN = 100
FEETYPE_LEN = 15
ALGNAME_LEN = 10
ORGANIZATION_LEN = 30
NOTES_LEN = 1024
DESCR_LEN = 512
FID_LEN = 128   # not taking chance, but 44 per https://stackoverflow.com/questions/38780572/is-there-any-specific-for-google-drive-file-id

class Lead(Base):
    __tablename__ = 'lead'
    id          = Column( Integer, primary_key=True )
    name        = Column( String(NAME_LEN) )
    email       = Column( String(EMAIL_LEN) )

class FeeType(Base):
    __tablename__ = 'feetype'
    id          = Column( Integer, primary_key=True )
    feeType     = Column( String(FEETYPE_LEN) ) # e.g., fixed, basedOnField, addOn
    # feeHandling = Column( String(ALGNAME_LEN) ) # e.g., fixed, basedOnField, addOn
    description = Column( String(DESCR_LEN) )

eventservice_table = Table('eventservice', Base.metadata,
    Column( 'event_id', Integer, ForeignKey('event.id' ) ),
    Column( 'service_id', Integer, ForeignKey('service.id' ), nullable=False ),
    )

class Service(Base):
    __tablename__ =  'service'
    id                = Column( Integer, primary_key=True ) 
    service           = Column( String(SERVICE_LEN) )
    serviceLong       = Column( String(DESCR_LEN) )
    isCalendarBlocked = Column( Boolean )
    feeTypeId         = Column( Integer, ForeignKey('feetype.id' ), nullable=False )
    feeType           = relationship( 'FeeType', backref='services', lazy=True )
    fee               = Column( Integer )              # must be set for feeType = fixed
    basedOnField      = Column( String(FIELD_LEN) )    # must be set for feeType = basedOnField

# for a given service, fieldValues are sorted
# fee is based on the smallest fieldValue >= basedOnField 
class FeeBasedOn(Base):
    __tablename__ =  'feebasedon'
    id         = Column( Integer, primary_key=True )
    serviceId  = Column( Integer, ForeignKey('service.id' ), nullable=False )
    service    = relationship( 'Service', backref='feeBasedOns', lazy=True )
    fieldValue = Column( Integer )
    fee        = Column( Integer )

class Course(Base):
    __tablename__ = 'course'
    id          = Column( Integer, primary_key=True ) 
    course      = Column( String(COURSE_LEN) )
    address     = Column( String(ADDRESS_LEN) )
    isStandard  = Column( Boolean ) # true if standard city course

class AddOn(Base):
    __tablename__ = 'addon'
    id          = Column( Integer, primary_key=True ) 
    shortDescr  = Column( String(SERVICE_LEN) )
    longDescr   = Column( String(NOTES_LEN) )
    fee         = Column( Integer )
    eventId     = Column( Integer, ForeignKey('event.id' ), nullable=False )

class State(Base):
    __tablename__ = 'state'
    id          = Column( Integer, primary_key=True ) 
    state       = Column( String(STATE_LEN) )
    description = Column( String(DESCR_LEN) )

class Event(Base):
    __tablename__ = 'event'
    id                  = Column( Integer, primary_key=True )
    event               = Column( String(EVENT_LEN) )
    date                = Column( String(DATE_LEN) )
    eventUrl            = Column( String(URL_LEN) )

    # see http://docs.sqlalchemy.org/en/latest/orm/basic_relationships.html Many To One
    state_id            = Column( Integer, ForeignKey('state.id') )
    state               = relationship( 'State', backref='events', lazy=True )
    lead_id             = Column( Integer, ForeignKey('lead.id') )
    lead                = relationship( 'Lead', backref='events', lazy=True )
    course_id           = Column( Integer, ForeignKey('course.id') )
    course              = relationship( 'Course', backref='events', lazy=True )

    mainStartTime       = Column( String(TIME_LEN) )
    mainDistance        = Column( Float )
    mainDistanceUnits   = Column( Enum('M',  'km') )
    funStartTime        = Column( String(TIME_LEN) )
    funDistance         = Column( Float )
    funDistanceUnits    = Column( Enum('M', 'km') )
    organization        = Column( String(ORGANIZATION_LEN) )
    organizationUrl     = Column( String(URL_LEN) )
    contactFirstName    = Column( String(NAME_LEN) )
    contactFullName     = Column( String(NAME_LEN) )
    contactEmail        = Column( String(EMAIL_LEN) )
    registrationUrl     = Column( String(URL_LEN) )
    # see http://docs.sqlalchemy.org/en/latest/orm/basic_relationships.html Many To Many
    services            = relationship( 'Service', secondary=eventservice_table, backref='events', lazy=True )
    finishersPrevYear   = Column( Integer )
    finishersCurrYear   = Column( Integer )
    maxParticipants     = Column( Integer )
    addOns              = relationship( 'AddOn', backref='event', lazy=True )
    contractSentDate    = Column( String(DATETIME_LEN) )
    contractSignedDate  = Column( String(DATETIME_LEN) )
    invoiceSentDate     = Column( String(DATE_LEN) )
    paymentRecdDate     = Column( String(DATE_LEN) )
    isOnCalendar        = Column( Boolean )
    contractDocId       = Column( String(FID_LEN) )
    notes               = Column( String(NOTES_LEN) )

# adapted from 
#   http://flask-dance.readthedocs.io/en/latest/backends.html#sqlalchemy
#   
class RolesUsers(Base):
    __tablename__ = 'roles_users'
    id = Column(Integer(), primary_key=True)
    user_id = Column('user_id', Integer(), ForeignKey('user.id'))
    role_id = Column('role_id', Integer(), ForeignKey('role.id'))

class Role(Base, RoleMixin):
    __tablename__ = 'role'
    id = Column(Integer(), primary_key=True)
    name = Column(String(ROLENAME_LEN), unique=True)
    description = Column(String(DESCR_LEN))

class User(Base, UserMixin):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    email               = Column( String(EMAIL_LEN), unique=True )
    name                = Column( String(NAME_LEN) )
    given_name          = Column( String(NAME_LEN) )
    last_login_at       = Column( DateTime() )
    current_login_at    = Column( DateTime() )
    last_login_ip       = Column( String(100) )
    current_login_ip    = Column( String(100) )
    login_count         = Column( Integer )
    active              = Column( Boolean() )
    confirmed_at        = Column( DateTime() )
    roles               = relationship('Role', secondary='roles_users',
                          backref=backref('users', lazy='dynamic'))

class OAuth(OAuthConsumerMixin, Base):
    provider_user_id    = Column( String(EMAIL_LEN), unique=True )
    user_id             = Column( Integer, ForeignKey(User.id) )
    user                = relationship(User)


#--------------------------------------------------------------------------
def init_db(defineowner=True):
#--------------------------------------------------------------------------
    # must wait until user_datastore is initialized before import
    from racesupportcontracts import user_datastore

    # TODO: move the following to config file
    # define states here
    states = [
        {'state':'pending', 'description':'race was copied automatically to the next year ("renewed") during Post Race Processing or by clicking Renew button. The admin is expected to confirm with race director that the race will happen and that the date and other race details are correct. This is set automatically through Post Race Processing or after clicking Renew.'},
        {'state':'tentative', 'description':'race director has confirmed race will be run again this year, but is not ready to receive the contract. This is set by the admin.'},
        {'state':'contract-sent', 'description':'race director has confirmed the date. Admin has sent contract to race director. This is set automatically.'},
        {'state':'committed', 'description':'race director has signed contract (electronically). This is set automatically.'},
        {'state':'blocked', 'description':'race date is blocked because of club constraints. This is set by the admin.'},
    ]

    # define fee types here basedOnField, addOn
    feetypes = [
        {'feeType':'fixed',         'description':'fixed fee'},
        {'feeType':'basedOnField',  'description':'fee is based on another field'},
        {'feeType':'addOn',         'description':'service is an add on'},
    ]

    # define initial leads here
    leads = [
        {'name':'to be added'}
    ]

    courses = [
        {'course':'to be added'}
    ]

    # initialize these tables
    modelitems = [
        (State, states),
        (FeeType, feetypes),
        (Lead, leads),
        (Course, courses),
    ]
    for model, items in modelitems:
        for item in items:
            db.session.add( model(**item) )

    # special processing for user roles because need to remember the roles when defining the owner
    # define user roles here
    userroles = [
        {'name':'superadmin', 'description':'everything'},
        {'name':'admin'     , 'description':'all but users / roles'},
        {'name':'notes'     , 'description':'can only edit notes'},
    ]

    # initialize roles, remembering what roles we have    
    allroles = {}
    for userrole in userroles:
        rolename = userrole['name']
        allroles[rolename] = Role.query.filter_by(name=rolename).first() or user_datastore.create_role(**userrole)
    
    # define owner if desired
    if defineowner:
        from flask import current_app
        rootuser = current_app.config['APP_OWNER']
        owner = User.query.filter_by(email=rootuser).first()
        if not owner:
            owner = user_datastore.create_user(email=rootuser)
            for rolename in allroles:
                user_datastore.add_role_to_user(owner, allroles[rolename])

    # and we're done, let's accept what we did
    db.session.commit()
