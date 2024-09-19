###########################################################################################
# dbmodel - database model for contracts database
#
#       Date            Author          Reason
#       ----            ------          ------
#       06/29/18        Lou King        Create
#
#   Copyright 2018 Lou King.  All rights reserved
###########################################################################################

# standard
import os.path
from configparser import SafeConfigParser
from copy import deepcopy
from datetime import datetime

# pypi
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.associationproxy import association_proxy

from flask_sqlalchemy import SQLAlchemy
from flask_security import current_user, UserMixin, RoleMixin
from flask import current_app

class parameterError(Exception): pass

# set up database - SQLAlchemy() must be done after app.config SQLALCHEMY_* assignments
from loutilities.user.model import db, LocalUserMixin, ManageLocalTables, EMAIL_LEN

# separator for SponsorRace CC fields
SPONSORRACE_CC_SEPARATOR = ';'

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
Text = db.Text
UniqueConstraint = db.UniqueConstraint
ForeignKey = db.ForeignKey
relationship = db.relationship
backref = db.backref
object_mapper = db.object_mapper
Base = db.Model

# some string sizes
URL_LEN = 2047      # https://stackoverflow.com/questions/417142/what-is-the-maximum-length-of-a-url-in-different-browsers
RACE_LEN = 256
DATE_LEN = 10
TIME_LEN = 8
DATETIME_LEN = DATE_LEN + 1 + TIME_LEN
STATE_LEN = 16
NAME_LEN = 256
EMAIL_LEN = 100
SERVICE_LEN = 20
TAG_LEN = 30
FIELD_LEN = 30
COURSE_LEN = 100
ROLENAME_LEN = 32
ADDRESS_LEN = 200
ADDRCITY_LEN = 64
ADDRSTATE_LEN = 32
ADDRSTREET_LEN = 128
ADDRZIP_LEN = 10
FEETYPE_LEN = 20
ALGNAME_LEN = 10
ORGANIZATION_LEN = 100
NOTES_LEN = 1024
DESCR_LEN = 512
FID_LEN = 128   # not taking chance, but 44 per https://stackoverflow.com/questions/38780572/is-there-any-specific-for-google-drive-file-id
SNAILADDR_LEN = 256
TITLE_LEN = 64
PHONE_LEN = 13
CONTRACT_TYPE_LEN = 30
TEMPLATE_TYPE_LEN = 30
CONTRACT_BLOCK_LEN = 2048
CONTRACT_BLOCK_TYPE_LEN = 20
EXCEPTION_LEN = 50
RULENAME_LEN = 100
LEVEL_LEN = 50
BENEFIT_LEN = 256
PROVIDER_LEN = 32
PROVIDERID_LEN = 128
COUPONCODE_LEN = 32
TREND_LEN = 32
LOGOFILENAME_LEN = 128
BENEFICIARY_LEN = 128
RACELOC_LEN = 128
SLUG_LEN = 32
VALUE_LEN = 128
TREATMENT_LEN = 32

class Lead(Base):
    __tablename__ = 'lead'
    id          = Column( Integer, primary_key=True )
    name        = Column( String(NAME_LEN) )
    email       = Column( String(EMAIL_LEN) )
    phone       = Column( String(PHONE_LEN) )
    roles       = Column( Text )
    active      = Column( Boolean )

    version_id          = Column(Integer, nullable=False, default=1)
    __mapper_args__ = {
        'version_id_col' : version_id
    }

class ContractType(Base):
    __tablename__ = 'contracttype'
    id                 = Column( Integer, primary_key=True )
    contractType       = Column( String(CONTRACT_TYPE_LEN) )
    description        = Column( String(DESCR_LEN) )

    version_id          = Column(Integer, nullable=False, default=1)
    __mapper_args__ = {
        'version_id_col' : version_id
    }
    
class TemplateType(Base):
    __tablename__ = 'templatetype'
    id              = Column( Integer, primary_key=True )
    templateType    = Column( String(TEMPLATE_TYPE_LEN) )
    description     = Column( String(DESCR_LEN) )
    contractTypeId  = Column( Integer, ForeignKey('contracttype.id' ) )
    contractType    = relationship( 'ContractType', backref='contracttypes', lazy=True )

    version_id          = Column(Integer, nullable=False, default=1)
    __mapper_args__ = {
        'version_id_col' : version_id
    }

class ContractBlockType(Base):
    __tablename__ = 'contractblocktype'
    id              = Column( Integer, primary_key=True )
    blockType       = Column( String(CONTRACT_BLOCK_TYPE_LEN) )
    description     = Column( String(DESCR_LEN) )
    
    version_id          = Column(Integer, nullable=False, default=1)
    __mapper_args__ = {
        'version_id_col' : version_id
    }
    
class Contract(Base):
    __tablename__ = 'contract'
    id                  = Column( Integer, primary_key=True )
    contractTypeId      = Column( Integer, ForeignKey('contracttype.id' ) )
    contractType        = relationship( 'ContractType', backref='contracts', lazy=True )
    blockPriority       = Column( Integer, nullable=False )
    contractBlockTypeId = Column( Integer, ForeignKey('contractblocktype.id' ) )
    contractBlockType   = relationship( 'ContractBlockType', backref='contracts', lazy=True )
    templateTypeId      = Column( Integer, ForeignKey('templatetype.id' ) )
    templateType        = relationship( 'TemplateType', backref='contracts', lazy=True )
    block               = Column( String(CONTRACT_BLOCK_LEN) )

    # track last update - https://docs.sqlalchemy.org/en/13/dialects/mysql.html#mysql-timestamp-onupdate
    update_time         = Column(DateTime,
                                 default=datetime.now,
                                 onupdate=datetime.now
                                 )

    version_id          = Column(Integer, nullable=False, default=1)
    __mapper_args__ = {
        'version_id_col' : version_id
    }

class FeeType(Base):
    __tablename__ = 'feetype'
    id          = Column( Integer, primary_key=True )
    feeType     = Column( String(FEETYPE_LEN) ) # e.g., fixed, basedOnField, addOn
    # feeHandling = Column( String(ALGNAME_LEN) ) # e.g., fixed, basedOnField, addOn
    description = Column( String(DESCR_LEN) )

    version_id          = Column(Integer, nullable=False, default=1)
    __mapper_args__ = {
        'version_id_col' : version_id
    }

# see http://docs.sqlalchemy.org/en/latest/orm/basic_relationships.html Many To Many
eventservice_table = Table('eventservice', Base.metadata,
    Column( 'event_id', Integer, ForeignKey('event.id' ) ),
    Column( 'service_id', Integer, ForeignKey('service.id' ), nullable=False ),
    )

serviceaddon_table = Table(
    'serviceaddon',
    Base.metadata,
    Column( 'service_id', ForeignKey('service.id'), primary_key=True ),
    Column( 'addon_id', ForeignKey('addon.id'), primary_key=True )
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
    addons    = relationship( 'AddOn', secondary=serviceaddon_table, back_populates='services')

    # track last update - https://docs.sqlalchemy.org/en/13/dialects/mysql.html#mysql-timestamp-onupdate
    update_time         = Column(DateTime,
                                 default=datetime.now,
                                 onupdate=datetime.now
                                 )

    version_id          = Column(Integer, nullable=False, default=1)
    __mapper_args__ = {
        'version_id_col' : version_id
    }

# see http://docs.sqlalchemy.org/en/latest/orm/basic_relationships.html Many To Many
eventtag_table = Table('eventtag', Base.metadata,
    Column( 'event_id', Integer, ForeignKey('event.id' ) ),
    Column( 'tag_id', Integer, ForeignKey('tag.id' ), nullable=False ),
    )

# events tag text
class Tag(Base):
    __tablename__ =  'tag'
    id                = Column( Integer, primary_key=True ) 
    tag               = Column( String(TAG_LEN) )
    description       = Column( String(DESCR_LEN) )
    isBuiltIn         = Column( Boolean )   # True if tag configured below

    version_id          = Column(Integer, nullable=False, default=1)
    __mapper_args__ = {
        'version_id_col' : version_id
    }

## as the built in tag text is used in code and will be stored in the database, these can't be changed by user
## (or in the code without very careful consideration of the migration plan)
## hyphens are avoided because these would cause wrapping in table displays
TAG_PRERACEMAILSENT         = 'preraceemailsent'
TAG_POSTRACEMAILSENT        = 'postraceemailsent'
TAG_PRERACEPREMPROMOEMAILSENT = 'preracepremoromoemailsent'
TAG_PRERACERENEWEDREMINDEREMAILSENT = 'preracerenwdreminderemailsent'
TAG_PRERACERENEWEDCANCELED = 'preracerenewedcanceled'
TAG_PRERACEMAILINHIBITED    = 'inhibitpreraceemail'
TAG_POSTRACEMAILINHIBITED   = 'inhibitpostraceemail'
TAG_PRERACEPREMPROMOEMAILINHIBITED = 'inhibitpreracepremoromoemail'
TAG_RACERENEWED             = 'racerenewed'
TAG_LEADEMAILSENT           = 'leademailsent'

## these tags are used to initialize the database in dbinit_contracts.py, 
## That file is one time use, so changing
## the tags structure will have no effect after the project is deployed
tags = [
    {'tag':TAG_PRERACEMAILSENT, 'description':'pre-race email has been sent', 'isBuiltIn':True},
    {'tag':TAG_PRERACEMAILINHIBITED, 'description':'admin wants to inhibit pre-race email', 'isBuiltIn':True},
    {'tag':TAG_POSTRACEMAILSENT, 'description':'post-race email has been sent', 'isBuiltIn':True},
    {'tag':TAG_POSTRACEMAILINHIBITED, 'description':'admin wants to inhibit post-race email', 'isBuiltIn':True},
    {'tag':TAG_RACERENEWED, 'description':'race has been renewed, or admin wants to to inhibit race renewal', 'isBuiltIn':True},
    {'tag':TAG_LEADEMAILSENT, 'description':'email has been sent to lead just before race', 'isBuiltIn':True},
    {'tag':TAG_PRERACEPREMPROMOEMAILSENT, 'description':"email has been sent for premium promotion only event that hasn't yet been renewed", 'isBuiltIn':True},
    {'tag':TAG_PRERACEPREMPROMOEMAILINHIBITED, 'description':"admin wants to inhibit email to premium promotion only event that hasn't yet been renewed", 'isBuiltIn':True},
    {'tag': TAG_PRERACERENEWEDREMINDEREMAILSENT,
     'description': "email has been sent for finish line event that hasn't yet been renewed",
     'isBuiltIn': True},
    {'tag': TAG_PRERACERENEWEDCANCELED,
     'description': "canceled finish line event that hasn't yet been renewed because we haven't heard back from race director",
     'isBuiltIn': True},
]

# see http://docs.sqlalchemy.org/en/latest/orm/basic_relationships.html Many To Many
sponsortag_table = Table('sponsorshiptag', Base.metadata,
    Column( 'sponsor_id', Integer, ForeignKey('sponsor.id' ) ),
    Column( 'sponsortag_id', Integer, ForeignKey('sponsortag.id' ), nullable=False ),
    )


# sponsor tag text
class SponsorTag(Base):
    __tablename__ =  'sponsortag'
    id                = Column( Integer, primary_key=True )
    tag               = Column( String(TAG_LEN) )
    description       = Column( String(DESCR_LEN) )
    isBuiltIn         = Column( Boolean )   # True if tag configured below

    version_id          = Column(Integer, nullable=False, default=1)
    __mapper_args__ = {
        'version_id_col' : version_id
    }

## as the built in tag text is used in code and will be stored in the database, these can't be changed by user
## (or in the code without very careful consideration of the migration plan)
## hyphens are avoided because these would cause wrapping in table displays
SPONSORTAG_RACERENEWED = 'sponsorshiprenewed'

## these tags are used to initialize the database in dbinit_contracts.py,
## That file is one time use, so changing
## the tags structure will have no effect after the project is deployed
sponsortags = [
    {'tag':SPONSORTAG_RACERENEWED, 'description':'sponsorship has been renewed', 'isBuiltIn':True},
]

# for a given service, fieldValues are sorted
# fee is based on the largest fieldValue <= basedOnField 
class FeeBasedOn(Base):
    __tablename__ =  'feebasedon'
    id         = Column( Integer, primary_key=True )
    serviceId  = Column( Integer, ForeignKey('service.id' ), nullable=False )
    service    = relationship( 'Service', backref='feeBasedOns', lazy=True )
    fieldValue = Column( Integer )
    fee        = Column( Integer )

    version_id          = Column(Integer, nullable=False, default=1)
    __mapper_args__ = {
        'version_id_col' : version_id
    }

class Course(Base):
    __tablename__ = 'course'
    id          = Column( Integer, primary_key=True ) 
    course      = Column( String(COURSE_LEN) )
    address     = Column( String(ADDRESS_LEN) )
    isStandard  = Column( Boolean ) # true if standard city course
    
    version_id          = Column(Integer, nullable=False, default=1)
    __mapper_args__ = {
        'version_id_col' : version_id
    }

# see http://docs.sqlalchemy.org/en/latest/orm/basic_relationships.html Many To Many
eventaddon_table = Table('eventaddon', Base.metadata,
    Column( 'event_id', Integer, ForeignKey('event.id' ) ),
    Column( 'addon_id', Integer, ForeignKey('addon.id' ), nullable=False ),
    )

class AddOn(Base):
    __tablename__ = 'addon'
    id          = Column( Integer, primary_key=True ) 
    shortDescr  = Column( String(SERVICE_LEN) )
    longDescr   = Column( String(NOTES_LEN) )
    fee         = Column( Integer )
    priority    = Column( Integer )
    # eventId     = Column( Integer, ForeignKey('event.id' ), nullable=False )
    is_upricing = Column( Boolean ) # True if using unit pricing
    up_basedon  = Column( Text )    # field unit pricing is based on
    up_subfixed = Column ( Integer )# how many to subtract off field for the unit pricing
    services    = relationship( 'Service', secondary=serviceaddon_table, back_populates='addons')
    
    # track last update - https://docs.sqlalchemy.org/en/13/dialects/mysql.html#mysql-timestamp-onupdate
    update_time         = Column(DateTime,
                                 default=datetime.now,
                                 onupdate=datetime.now
                                 )

    version_id          = Column(Integer, nullable=False, default=1)
    __mapper_args__ = {
        'version_id_col' : version_id
    }

# system tag text
STATE_RENEWED_PENDING   = 'renewed-pending'
STATE_TENTATIVE         = 'tentative'
STATE_CONTRACT_SENT     = 'contract-sent'
STATE_COMMITTED         = 'committed'
STATE_CANCELED          = 'canceled'
class State(Base):
    __tablename__ = 'state'
    id          = Column( Integer, primary_key=True ) 
    state       = Column( String(STATE_LEN) )
    description = Column( String(DESCR_LEN) )
    
    version_id          = Column(Integer, nullable=False, default=1)
    __mapper_args__ = {
        'version_id_col' : version_id
    }

class Client(Base):
    __tablename__ = 'client'
    id                  = Column( Integer, primary_key=True ) 
    client              = Column( String(ORGANIZATION_LEN) )
    clientUrl           = Column( String(URL_LEN) )
    clientPhone         = Column( String(PHONE_LEN) )
    clientAddr          = Column( String(SNAILADDR_LEN) )
    contactFirstName    = Column( String(NAME_LEN) )
    contactLastName     = Column( String(NAME_LEN) )
    contactEmail        = Column( String(EMAIL_LEN) )
    contactTitle        = Column( String(TITLE_LEN) )
    notes               = Column( String(NOTES_LEN) )
    
    version_id          = Column(Integer, nullable=False, default=1)
    __mapper_args__ = {
        'version_id_col' : version_id
    }

    @hybrid_property
    def name(self):
        return self.contactFirstName + ' ' + self.contactLastName

class Race(Base):
    __tablename__ = 'race'
    id                  = Column( Integer, primary_key=True ) 
    race                = Column( String(RACE_LEN) )
    daterule_id         = Column( Integer, ForeignKey('daterule.id') )
    daterule            = relationship( 'DateRule', backref='racerules', lazy=True )
    notes               = Column( String(NOTES_LEN) )

    version_id          = Column(Integer, nullable=False, default=1)
    __mapper_args__ = {
        'version_id_col' : version_id
    }

class Event(Base):
    __tablename__ = 'event'
    id                  = Column( Integer, primary_key=True )
    date                = Column( String(DATE_LEN) )
    eventUrl            = Column( String(URL_LEN) )
    registrationUrl     = Column( String(URL_LEN) )

    # see http://docs.sqlalchemy.org/en/latest/orm/basic_relationships.html Many To One
    race_id             = Column( Integer, ForeignKey('race.id') )
    race                = relationship( 'Race', backref='events', lazy=True )
    state_id            = Column( Integer, ForeignKey('state.id') )
    state               = relationship( 'State', backref='events', lazy=True )
    lead_id             = Column( Integer, ForeignKey('lead.id') )
    lead                = relationship( 'Lead', backref='events', lazy=True, foreign_keys=[lead_id] )
    markinglead_id      = Column( Integer, ForeignKey('lead.id') )
    markinglead         = relationship( 'Lead', backref='markingevents', lazy=True, foreign_keys=[markinglead_id] ) 
    course_id           = Column( Integer, ForeignKey('course.id') )
    course              = relationship( 'Course', backref='events', lazy=True )
    client_id           = Column( Integer, ForeignKey('client.id') )
    client              = relationship( 'Client', backref='events', lazy=True )

    mainStartTime       = Column( String(TIME_LEN) )
    mainDistance        = Column( Float )
    mainDistanceUnits   = Column( Enum('M',  'km') )
    funStartTime        = Column( String(TIME_LEN) )
    funDistance         = Column( Float )
    funDistanceUnits    = Column( Enum('M', 'km') )

    # see http://docs.sqlalchemy.org/en/latest/orm/basic_relationships.html Many To Many
    services            = relationship( 'Service', secondary=eventservice_table, backref='events', lazy=True )
    finishersPrevYear   = Column( Integer )
    finishersCurrYear   = Column( Integer )
    maxParticipants     = Column( Integer )
    # see http://docs.sqlalchemy.org/en/latest/orm/basic_relationships.html Many To Many, https://stackoverflow.com/a/46019895/799921
    addOns              = relationship( 'AddOn', secondary=eventaddon_table, backref='events', lazy=True, order_by=AddOn.priority )
    contractSentDate    = Column( String(DATETIME_LEN) )
    contractSignedDate  = Column( String(DATETIME_LEN) )
    invoiceSentDate     = Column( String(DATE_LEN) )
    isOnCalendar        = Column( Boolean )
    contractDocId       = Column( String(FID_LEN) )
    invoiceDocId        = Column( Text )
    notes               = Column( String(NOTES_LEN) )

    # added when contract approved
    contractApprover    = Column( String(NAME_LEN) )
    contractApproverEmail = Column( String(EMAIL_LEN) )
    contractApproverNotes = Column( String(NOTES_LEN) )

    # set to True if contract updated after initially approved
    isContractUpdated     = Column( Boolean, default=False )

    # tags
    tags                = relationship( 'Tag', secondary=eventtag_table, backref='events', lazy=True )

    version_id          = Column(Integer, nullable=False, default=1)
    __mapper_args__ = {
        'version_id_col' : version_id
    }

class EventAvailabilityException(Base):
    __tablename__ = 'eventavailabilityexception'
    id            = Column( Integer, primary_key=True )
    shortDescr    = Column( String(EXCEPTION_LEN) )
    # see http://docs.sqlalchemy.org/en/latest/orm/basic_relationships.html One To One
    daterule_id   = Column( Integer, ForeignKey('daterule.id') )
    daterule      = relationship( 'DateRule', backref='eventexceptions', lazy=True )
    exception     = Column( Enum( 'available',  'unavailable' ) )
    notes         = Column( String(NOTES_LEN) )
    
    version_id          = Column(Integer, nullable=False, default=1)
    __mapper_args__ = {
        'version_id_col' : version_id
    }

class DateRule(Base):
    __tablename__ = 'daterule'
    id          = Column( Integer, primary_key=True )
    rulename    = Column( String(RULENAME_LEN), unique=True )
    rule        = Column( Enum('First',  'Second', 'Third', 'Fourth', 'Fifth', 'Last', 'Date', 'Easter') )
    day         = Column( Enum('Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'))
    month       = Column( Enum('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'))
    date        = Column( Integer )
    deltaday    = Column( Integer, default=0 )  # 0 this day
                                                # positive # days after this day
                                                # negative # days before this day
    addldays    = Column( Integer, default=0 )  # 0 just this day
                                                # positive if the next days are included 
                                                # negative if previous days are included
    year        = Column( Integer ) # 0/null means yearly; specified for specific year applicability
    
    version_id          = Column(Integer, nullable=False, default=1)
    __mapper_args__ = {
        'version_id_col' : version_id
    }

    # build rulename automatically
    def __init__(self, **kwargs):
        super(DateRule, self).__init__(**kwargs)
        if self.rule == 'Easter':
            self.rulename = 'Easter'
        elif self.rule == 'Date':
            if not self.year:
                self.rulename = '{} {}'.format(self.month, self.date)
            else:
                self.rulename = '{} {}, {}'.format(self.month, self.date, self.year)
        else:
            self.rulename = '{} {} {}'.format(self.rule, self.day, self.month)
            if self.year:
                self.rulename += ', {}'.format(self.year)
            # handle text 0 if present
            if self.deltaday and int(self.deltaday):
                self.rulename += ', {} days from'.format(self.deltaday)
            if self.addldays and int(self.addldays):
                self.rulename += ", {} add'l days".format(self.addldays)

# sponsor
# sponsor races
class Sponsor(Base):
    __tablename__ = 'sponsor'
    id           = Column( Integer, primary_key=True )

    raceyear            = Column( Integer )
    racecontact         = Column( String(NAME_LEN) )
    amount              = Column( Integer )
    couponcode          = Column( String(COUPONCODE_LEN) )  # or "promo code"
    trend               = Column( String(TREND_LEN) )
    contractDocId       = Column( String(FID_LEN) )
    # logofilename        = Column( String(LOGOFILENAME_LEN) )

    # see http://docs.sqlalchemy.org/en/latest/orm/basic_relationships.html Many To One
    race_id             = Column( Integer, ForeignKey('sponsorrace.id') )
    race                = relationship( 'SponsorRace', backref='sponsors', lazy=True )
    client_id           = Column( Integer, ForeignKey('client.id') )
    client              = relationship( 'Client', backref='sponsors', lazy=True )
    state_id            = Column( Integer, ForeignKey('state.id') )
    state               = relationship( 'State', backref='sponsors', lazy=True )
    level_id            = Column( Integer, ForeignKey('sponsorlevel.id') )
    level               = relationship( 'SponsorLevel', backref='sponsors', lazy=True )

    datesolicited       = Column( String(DATE_LEN) )
    dateagreed          = Column( String(DATE_LEN) )
    invoicesent         = Column( String(DATE_LEN) )

    RegSiteUpdated      = Column( Enum('no',  'yes', 'n/a') )
    isWebsiteUpdated    = Column( Boolean )
    isLogoReceived      = Column( Boolean )
    isSponsorThankedFB  = Column( Boolean )

    notes               = Column( String(NOTES_LEN) )

    # tags
    tags                = relationship( 'SponsorTag', secondary=sponsortag_table, backref='sponsors', lazy=True )

    version_id          = Column(Integer, nullable=False, default=1)
    __mapper_args__ = {
        'version_id_col' : version_id
    }

# sponsor races
class SponsorRace(Base):
    __tablename__ = 'sponsorrace'
    id           = Column( Integer, primary_key=True )
    race         = Column( String(RACE_LEN) )
    raceshort    = Column( String(RACE_LEN) )
    racedirector = Column( String(NAME_LEN) )
    rdphone          = Column( String(PHONE_LEN) )
    rdemail          = Column( String(EMAIL_LEN) )
    isRDCertified    = Column( Boolean )
    raceurl      = Column( String(URL_LEN) )
    sponsorurl   = Column( String(URL_LEN) )
    email        = Column( String(EMAIL_LEN) )      # obsolete, see email_from
    email_from   = Column( Text ) 
    query_cc     = Column( Text )
    agreement_cc = Column( Text )
    # logofilename = Column( String(LOGOFILENAME_LEN) )
    couponprovider = Column( String(PROVIDER_LEN) )
    couponproviderid = Column( String(PROVIDERID_LEN) )
    description      = Column( String(DESCR_LEN) )
    display          = Column( Boolean )
    viewkey          = Column( Text )
    cacheupdatets    = Column( Integer, nullable=False, default=0 )
    timezone         = Column( Text )

    version_id          = Column(Integer, nullable=False, default=1)
    __mapper_args__ = {
        'version_id_col' : version_id
    }

# sponsor race dates
class SponsorRaceDate(Base):
    __tablename__ = 'sponsorracedate'
    id           = Column( Integer, primary_key=True )
    # see http://docs.sqlalchemy.org/en/latest/orm/basic_relationships.html Many To One
    race_id        = Column( Integer, ForeignKey('sponsorrace.id') )
    race           = relationship( 'SponsorRace', backref='dates', lazy=True )
    raceyear       = Column( Integer )
    racedate       = Column( String(DATE_LEN) )
    beneficiary    = Column( String(BENEFICIARY_LEN) )
    raceloc        = Column( String(RACELOC_LEN) )

    version_id          = Column(Integer, nullable=False, default=1)
    __mapper_args__ = {
        'version_id_col' : version_id
    }

# sponsor race dates
class SponsorRaceVbl(Base):
    __tablename__ = 'sponsorracevbl'
    id           = Column( Integer, primary_key=True )
    variable     = Column( String(SLUG_LEN) )
    value        = Column( String(VALUE_LEN) )
    race_id      = Column( Integer, ForeignKey('sponsorrace.id') )
    race         = relationship( 'SponsorRace', backref='variables', lazy=True )

    version_id          = Column(Integer, nullable=False, default=1)
    __mapper_args__ = {
        'version_id_col' : version_id
    }

# sponsor rache registration cache
class SponsorRaceRegCache(Base):
    __tablename__ = 'sponsorraceregcache'
    id              = Column( Integer, primary_key=True )
    registration_id = Column( Integer )
    event_id        = Column( Integer, index=True )
    event_name      = Column( Text )
    registration_date = Column( DateTime )
    last_modified_ts = Column( Integer ) # timestamp
    first_name      = Column ( Text )
    last_name       = Column ( Text )
    email           = Column ( Text )
    gender          = Column ( Text )
    dob             = Column ( Date )
    is_active       = Column( Boolean )
    removed_reason  = Column( Text )

# sponsor levels / sponsor benefits
# see http://docs.sqlalchemy.org/en/latest/orm/basic_relationships.html Many To Many
sponsorlevelbenefit_table = Table('sponsorlevelbenefit', Base.metadata,
    Column( 'level_id', Integer, ForeignKey('sponsorlevel.id' ) ),
    Column( 'benefit_id', Integer, ForeignKey('sponsorbenefit.id' ), nullable=False ),
    )

# sponsor levels
class SponsorLevel(Base):
    __tablename__ = 'sponsorlevel'
    id             = Column( Integer, primary_key=True )
    level          = Column( String(LEVEL_LEN) )
    minsponsorship = Column( Integer )
    couponcount    = Column( Integer )
    display        = Column( Boolean )
    maxallowed     = Column( Integer )  # leave null if no limit
    treatment      = Column( String(TREATMENT_LEN) )
    description    = Column( String(DESCR_LEN) )
    # see http://docs.sqlalchemy.org/en/latest/orm/basic_relationships.html Many To One
    race_id        = Column( Integer, ForeignKey('sponsorrace.id') )
    race           = relationship( 'SponsorRace', backref='levels', lazy=True )

    race_short     = association_proxy('race', 'raceshort')

    version_id          = Column(Integer, nullable=False, default=1)
    __mapper_args__ = {
        'version_id_col' : version_id
    }

    @hybrid_property
    def race_level(self):
        return self.race.raceshort + '/' + self.level

    # # expression required for filter. see https://stackoverflow.com/questions/19780178/sqlalchemy-hybrid-expression-with-relationship
    # @race_level.expression
    # def race_level(cls):
    #     from sqlalchemy.sql.functions import concat
    #     return concat(cls.race_short, '/', cls.level)

# sponsor benefits
class SponsorBenefit(Base):
    __tablename__ = 'sponsorbenefit'
    id          = Column( Integer, primary_key=True )
    race_id     = Column( Integer, ForeignKey('sponsorrace.id') )
    race        = relationship( 'SponsorRace', backref='benefits', lazy=True )
    benefit     = Column( String(BENEFIT_LEN) )
    order       = Column( Integer )
    description = Column( String(DESCR_LEN) )
    # see http://docs.sqlalchemy.org/en/latest/orm/basic_relationships.html Many To Many
    levels       = relationship( 'SponsorLevel', secondary=sponsorlevelbenefit_table, backref='benefits', lazy=True )

    version_id          = Column(Integer, nullable=False, default=1)
    __mapper_args__ = {
        'version_id_col' : version_id
    }

# sponsor query log
class SponsorQueryLog(Base):
    __tablename__ = 'sponsorquerylog'
    id              = Column( Integer, primary_key=True )
    time            = Column( String(DATETIME_LEN) )
    organization    = Column( String(ORGANIZATION_LEN) )
    name            = Column( String(NAME_LEN) )
    phone           = Column( String(PHONE_LEN) )
    city            = Column( String(ADDRCITY_LEN) )
    state           = Column( String(ADDRSTATE_LEN) )
    street          = Column( String(ADDRSTREET_LEN) )
    zipcode         = Column( String(ADDRZIP_LEN) )
    email           = Column( String(EMAIL_LEN) )
    race            = Column( String(RACE_LEN) )
    amount          = Column( Integer )
    level           = Column( String(LEVEL_LEN) )
    comments        = Column( String(NOTES_LEN) )

# copied by update_local_tables
class LocalUser(LocalUserMixin, Base):
    __tablename__ = 'localuser'
    id                  = Column(Integer(), primary_key=True)
    interest_id         = Column(Integer, ForeignKey('localinterest.id'))
    interest            = relationship('LocalInterest', backref=backref('users'))
    version_id          = Column(Integer, nullable=False, default=1)
    __mapper_args__ = {
        'version_id_col' : version_id
    }

# note update_local_tables only copies Interests for current application (g.loutility)
class LocalInterest(Base):
    __tablename__ = 'localinterest'
    id                  = Column(Integer(), primary_key=True)
    interest_id         = Column(Integer)

    version_id          = Column(Integer, nullable=False, default=1)
    __mapper_args__ = {
        'version_id_col' : version_id
    }

#####################################################
class priorityUpdater(): 
#####################################################
    # increment priority for each of the blocks
    def __init__(self, initial, increment):
        self.priority = initial - increment
        self.increment = increment

    def __call__(self):
        self.priority += self.increment
        return self.priority

#####################################################
class ModelItem():
#####################################################
    '''
    used within dbinit_xx modules 

    :param model: database model to initialize
    :param items: list of item objects, with object keys matching column names
        item object value may be function with no parameters to resolve at runtime
    :param cleartable: False if items are to be merged. True if table is to be cleared before initializing.
        default True
    :param checkkeys: if cleartable == False, list of keys to check to decide if record is 
        to be added. If there is a record in the table with values matching this item's for these
        keys, the record is updated.
        Alternately, a function can be supplied f(item) to check against db, returns the record
        if item found, None otherwise. For convenience, scalar key can be supplied (i.e., not a list).

        if key has '/', this means dbfield/itemkey, where itemkey may be dotted notation.
        E.g., race_id/race.id
    '''

    #----------------------------------------------------------------------
    def __init__(self, model, items, cleartable=True, checkkeys=[]):
    #----------------------------------------------------------------------
        self.model = model
        self.items = items
        self.cleartable = cleartable
        self.checkkeys = checkkeys

#####################################################
class getmodelitems():
#####################################################
    #----------------------------------------------------------------------
    def __init__(self, model, queries):
    #----------------------------------------------------------------------
        '''
        returns a (class) function to retrieve a model item or items based on value, at runtime

        :param model: model to retrieve from
        :param queries: query dicts to retrieve with
            if queries is a list of dicts, returned function will return a list
            if queries is a dict, returned function will return a value
        '''
        self.model = model
        self.queries = queries

    #----------------------------------------------------------------------
    def __call__(self):
    #----------------------------------------------------------------------
        '''
        class instance behaves as a function f, use f() to call
        '''
        # islist = isinstance(self.vals, list)
        islist = isinstance(self.queries, list)

        # will process as list now, but will remove list later
        if islist:
            queries = self.queries
        else:
            queries = [self.queries]

        items = []
        # for val in vals:
        for query in queries:
            thisquery = deepcopy(query)

            # resolve any callable values in query
            for attr in thisquery:
                if callable(thisquery[attr]):
                    thisquery[attr] = thisquery[attr]()

            item = db.session.query(self.model).filter_by(**thisquery).one()
            items.append(item)

        # return list if vals was list
        if islist:
            return items
        else:
            return items[0]


#----------------------------------------------------------------------
def initdbmodels(modelitems):
#----------------------------------------------------------------------
    '''
    initialize database models

    :param modelitems: list of ModelItem objects
    '''
    # clear desired tables in reverse order to avoid constraint errors
    clearmodels = [mi.model for mi in modelitems if mi.cleartable]
    clearmodels.reverse()
    for model in clearmodels:
        for modelrow in db.session.query(model).all():
            current_app.logger.debug('deleting id={} modelrow={}'.format(modelrow.id, modelrow.__dict__))
            db.session.delete(modelrow)

    # build tables
    for modelitem in modelitems:
        model = modelitem.model

        # maybe items is list of strings, like csv file
        if len(modelitem.items) > 0 and isinstance(modelitem.items[0], str):
            from csv import DictReader
            ITEMS = DictReader(modelitem.items)
            items = []
            for item in ITEMS:
                items.append(item)
        
        # otherwise assume items are objects
        else:
            items = modelitem.items

        cleartable = modelitem.cleartable
        checkkeys = modelitem.checkkeys

        # if caller supplied function to check item existence, use it
        if callable(checkkeys):
            itemexists = checkkeys
        
        # otherwise, checkkeys is list of keys to filter, create function to check
        else:
            # allow scalar
            if not isinstance(checkkeys, list):
                checkkeys = [checkkeys]

            def itemexists(item):
                query = {}
                # for top level keys, just add to top level query
                # for secondary keys add additional filters 
                # note only allows two levels, and is a bit brute force
                for key in checkkeys:
                    keys = key.split('/')

                    # just a key here
                    if len(keys) == 1:
                        query[key] = item[key]
                    
                    # something like race_id/race.id, where race_id is attribute of model, race is key of item, and id is attribute of race
                    elif len(keys) == 2:
                        modelid, dottedkeys = keys
                        thiskey, thisattr = dottedkeys.split('.')
                        query[modelid] = getattr(item[thiskey], thisattr)
                    
                    # bad configuration, like x/y/z
                    else:
                        raise parameterError('invalid key has too many parts: {}, item {}'.format(key, item))


                # return query result
                thisquery = model.query.filter_by(**query)
                return thisquery.one_or_none()

        for item in items:
            resolveitem = {}
            for key in item:
                if not callable(item[key]):
                    resolveitem[key] = item[key]
                else:
                    resolveitem[key] = item[key]()

            if not cleartable:
                thisitem = itemexists(resolveitem)
            
            # maybe we need to add
            # note thisitem not initialized if cleartable
            if cleartable or not thisitem:
                current_app.logger.info( 'initdbmodels(): adding {}'.format(resolveitem) )
                db.session.add( model(**resolveitem) )
            
            # if item exists, update it with resolved data
            elif thisitem:
                current_app.logger.info( 'initdbmodels(): updating old: {}, new: {}'.format(thisitem.__dict__, resolveitem) )
                # thisitem.__dict__.update(resolveitem)
                for key in resolveitem:
                    setattr(thisitem, key, resolveitem[key])


        # need to commit within loop because next model might use this model's data
        db.session.commit()

# supporting functions
def update_local_tables():
    '''
    keep LocalUser table consistent with external db User table
    '''
    # appname needs to match Application.application
    localtables = ManageLocalTables(db, 'contracts', LocalUser, LocalInterest, hasuserinterest=True)
    localtables.update()

