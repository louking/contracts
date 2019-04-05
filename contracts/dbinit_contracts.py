###########################################################################################
# dbinit_contracts - contracts database initialization configuration
#
#       Date            Author          Reason
#       ----            ------          ------
#       10/18/18        Lou King        Create
#
#   Copyright 2018 Lou King
###########################################################################################
'''
dbinit_contracts - contracts database initialization configuration
===================================================================
'''

# homegrown
from dbmodel import State, FeeType, FeeBasedOn, Service, Course, ContractType, TemplateType, ContractBlockType 
from dbmodel import Contract, DateRule, Tag, tags
from dbmodel import EventAvailabilityException
from dbmodel import TAG_PRERACEMAILSENT, TAG_PRERACEMAILINHIBITED
from dbmodel import TAG_POSTRACEMAILSENT, TAG_POSTRACEMAILINHIBITED, TAG_RACERENEWED
from dbmodel import TAG_LEADEMAILSENT
from dbmodel import TAG_PRERACEPREMPROMOEMAILSENT, TAG_PRERACEPREMPROMOEMAILINHIBITED

from dbmodel import STATE_RENEWED_PENDING, STATE_TENTATIVE, STATE_CONTRACT_SENT, STATE_COMMITTED, STATE_CANCELED       

from dbmodel import ModelItem, initdbmodels, priorityUpdater

# define templatetypes
templatetypes = [
    {'templateType' : 'contract', 'description' : 'race services contract', 'contractType' : ContractType.query.filter_by(contractType='race services').one},
    {'templateType' : 'contract email', 'description' : 'race services contract email', 'contractType' : ContractType.query.filter_by(contractType='race services').one},
    {'templateType' : 'pre-race email', 'description' : 'pre-race coordination email with race director', 'contractType' : ContractType.query.filter_by(contractType='race services').one},
    {'templateType' : 'lead email', 'description' : 'pre-race coordination email just with lead', 'contractType' : ContractType.query.filter_by(contractType='race services').one},
    {'templateType' : 'post-race email', 'description' : 'post-race email', 'contractType' : ContractType.query.filter_by(contractType='race services').one},
    {'templateType' : 'accept agreement view', 'description' : 'accept agreement email', 'contractType' : ContractType.query.filter_by(contractType='race services').one},
    {'templateType' : 'accept agreement error view', 'description' : 'accept agreement error view', 'contractType' : ContractType.query.filter_by(contractType='race services').one},
    {'templateType' : 'agreement accepted view', 'description' : 'agreement accepted view', 'contractType' : ContractType.query.filter_by(contractType='race services').one},
    {'templateType' : 'prempromo email', 'description' : 'premium promotion email before start of promotion', 'contractType' : ContractType.query.filter_by(contractType='race services').one},
    {'templateType' : 'sponsor agreement', 'description' : 'sponsor agreement', 'contractType' : ContractType.query.filter_by(contractType='race sponsorship').one},
    {'templateType' : 'sponsor email', 'description' : 'sponsorship agreement sponsor email', 'contractType' : ContractType.query.filter_by(contractType='race sponsorship').one},
]

# define contracttypes
contracttypes = [
    {'contractType' : 'race services', 'description' : 'race services contract'},
    {'contractType' : 'race sponsorship', 'description' : 'signature race sponsorship agreement'},
]

# define blocktypes
blocktypes = [
    {'blockType' : 'sectionprops', 'description' : 'section properties, json object, see https://python-docx.readthedocs.io/en/latest/api/section.html for formatting'},
    {'blockType' : 'para', 'description' : 'normal paragraph'},
    {'blockType' : 'listitem', 'description' : 'item in a list, optionally repeated through array of entries'},
    {'blockType' : 'listitem2', 'description' : 'item in a list indented, optionally repeated through array of entries'},
    {'blockType' : 'tablehdr', 'description' : 'table header, comma delimited'},
    {'blockType' : 'tablerow', 'description' : 'table row, comma delimited, optionally repeated through array of entries'},
    {'blockType' : 'tablerowbold', 'description' : 'table row (bolded), comma delimited, optionally repeated through array of entries'},
    {'blockType' : 'pagebreak', 'description' : 'page break'},
    {'blockType' : 'html', 'description' : 'html template'},
]

# define contracts (contract template blocks)
RACE_AGREEMENT_HEADER = 'RACE SERVICES AGREEMENT\nFREDERICK STEEPLECHASERS RUNNING CLUB - PO BOX 681, FREDERICK, MD 21705-0681'

contractpriority = priorityUpdater(10, 10)
contractmailpriority = priorityUpdater(10, 10)
acceptagreementpriority = priorityUpdater(10, 10)
acceptagreementerrorpriority = priorityUpdater(10, 10)
agreementacceptedpriority = priorityUpdater(10, 10)

# contract for race services contractType
contracts = [
    {   
        'contractType'       : ContractType.query.filter_by(contractType='race services').one, 
        'contractBlockType'  : ContractBlockType.query.filter_by(blockType='sectionprops').one,
        'templateType'       : TemplateType.query.filter_by(templateType='contract').one,
        'blockPriority'      : contractpriority,
        'block'              : '{"left_margin":685800, "right_margin":685800}'
    }, 
    {   
        'contractType'       : ContractType.query.filter_by(contractType='race services').one, 
        'contractBlockType'  : ContractBlockType.query.filter_by(blockType='para').one,
        'templateType'       : TemplateType.query.filter_by(templateType='contract').one,
        'blockPriority'      : contractpriority,
        'block'              : RACE_AGREEMENT_HEADER
    }, 
    {   
        'contractType'       : ContractType.query.filter_by(contractType='race services').one, 
        'contractBlockType'  : ContractBlockType.query.filter_by(blockType='para').one,
        'templateType'       : TemplateType.query.filter_by(templateType='contract').one,
        'blockPriority'      : contractpriority,
        'block'              : '{{ _date_ }}'
    }, 
    {   
        'contractType'       : ContractType.query.filter_by(contractType='race services').one, 
        'contractBlockType'  : ContractBlockType.query.filter_by(blockType='para').one,
        'templateType'       : TemplateType.query.filter_by(templateType='contract').one,
        'blockPriority'      : contractpriority,
        'block'              : '{{ client.contactFirstName }} {{ client.contactLastName }}\n{{ event }} - {{ date }}'
    }, 
    {   
        'contractType'       : ContractType.query.filter_by(contractType='race services').one, 
        'contractBlockType'  : ContractBlockType.query.filter_by(blockType='para').one,
        'templateType'       : TemplateType.query.filter_by(templateType='contract').one,
        'blockPriority'      : contractpriority,
        'block'              : 'Dear {{ client.contactFirstName }},'
    }, 
    {   
        'contractType'       : ContractType.query.filter_by(contractType='race services').one, 
        'contractBlockType'  : ContractBlockType.query.filter_by(blockType='para').one,
        'templateType'       : TemplateType.query.filter_by(templateType='contract').one,
        'blockPriority'      : contractpriority,
        'block'              : 'You have requested race support services from Frederick ' 
                               'Steeplechasers Running Club for your event.  This is to ' 
                               'confirm that we have scheduled the race support services as ' 
                               'detailed on the following agreement.',
    }, 
    {   
        'contractType'       : ContractType.query.filter_by(contractType='race services').one, 
        'contractBlockType'  : ContractBlockType.query.filter_by(blockType='para').one,
        'templateType'       : TemplateType.query.filter_by(templateType='contract').one,
        'blockPriority'      : contractpriority,
        'block'              : 'Your organization is responsible for the following:',
    }, 
    {   
        'contractType'       : ContractType.query.filter_by(contractType='race services').one, 
        'contractBlockType'  : ContractBlockType.query.filter_by(blockType='listitem').one,
        'templateType'       : TemplateType.query.filter_by(templateType='contract').one,
        'blockPriority'      : contractpriority,
        'block'              : '{% if "finishline" in servicenames %}' +
                               'Finish Line/Timing Services: Provide race bib numbers with ' 
                               'pull-off tags to all participants with the name, age and ' 
                               'gender of each participant recorded on the tags. The runners ' 
                               'should be instructed to pin the race bib (with the pull-tag in ' 
                               'place) on the front where it can be clearly seen by the finish ' 
                               'line personnel' +
                               '{% endif %}'
    }, 
    {   
        'contractType'       : ContractType.query.filter_by(contractType='race services').one, 
        'contractBlockType'  : ContractBlockType.query.filter_by(blockType='listitem').one,
        'templateType'       : TemplateType.query.filter_by(templateType='contract').one,
        'blockPriority'      : contractpriority,
        'block'              : 'Standard Promotion: Add your race to the FSRC website event ' 
                               'calendar (if not already present): ' 
                               'https://steeplechasers.org/events/community/add' 
    }, 
    {   
        'contractType'       : ContractType.query.filter_by(contractType='race services').one, 
        'contractBlockType'  : ContractBlockType.query.filter_by(blockType='listitem').one,
        'templateType'       : TemplateType.query.filter_by(templateType='contract').one,
        'blockPriority'      : contractpriority,
        'block'              : '{% if "premiumpromotion" in servicenames %}' 
                               'Premium Promotion: '
                               'We would like to make sure that we are reaching all of your interested participants. '
                               "Provide spreadsheet file of your participants' email addresses from " 
                               'previous year (if available and not already provided), and then ' 
                               'provide the current list at the conclusion of the race. Please ' 
                               'include a statement in your race waiver as follows: "I understand ' 
                               'that I may receive emails about this race and other races promoted ' 
                               'by the Frederick Steeplechasers Running Club."' 
                               '{% endif %}'
    }, 
    {   
        'contractType'       : ContractType.query.filter_by(contractType='race services').one, 
        'contractBlockType'  : ContractBlockType.query.filter_by(blockType='listitem').one,
        'templateType'       : TemplateType.query.filter_by(templateType='contract').one,
        'blockPriority'      : contractpriority,
        'block'              : '{% if "finishline" in servicenames or "coursemarking" in servicenames %}' 
                               'Course Support: Aid stations and Course Marshals at key locations ' 
                               'along the route are recommended and are the responsibility of the ' 
                               'race organizers.'
                               '{% endif %}'
    }, 
    {   
        'contractType'       : ContractType.query.filter_by(contractType='race services').one, 
        'contractBlockType'  : ContractBlockType.query.filter_by(blockType='para').one,
        'templateType'       : TemplateType.query.filter_by(templateType='contract').one,
        'blockPriority'      : contractpriority,
        'block'              : 'FSRC is responsible for:'
    }, 
    {   
        'contractType'       : ContractType.query.filter_by(contractType='race services').one, 
        'contractBlockType'  : ContractBlockType.query.filter_by(blockType='listitem').one,
        'templateType'       : TemplateType.query.filter_by(templateType='contract').one,
        'blockPriority'      : contractpriority,
        'block'              : '{% if "finishline" in servicenames %}'
                               'Finish Line/Timing Services'
                               '{% endif %}'
    }, 
    {   
        'contractType'       : ContractType.query.filter_by(contractType='race services').one, 
        'contractBlockType'  : ContractBlockType.query.filter_by(blockType='listitem2').one,
        'templateType'       : TemplateType.query.filter_by(templateType='contract').one,
        'blockPriority'      : contractpriority,
        'block'              : '{% if "finishline" in servicenames %}' +
                               'Transport, setup and operation of FSRC equipment (Display ' 
                               'Clock, Time Machine Race Timer, Finish Line Chute, flags, ' 
                               'signage and related materials)' +
                               '{% endif %}'
    }, 
    {   
        'contractType'       : ContractType.query.filter_by(contractType='race services').one, 
        'contractBlockType'  : ContractBlockType.query.filter_by(blockType='listitem2').one,
        'templateType'       : TemplateType.query.filter_by(templateType='contract').one,
        'blockPriority'      : contractpriority,
        'block'              : '{% if "finishline" in servicenames %}' +
                               'Timing and scoring, including generation of a list of award ' 
                               'winners, posting of ordered bib pull-tags with finish times at ' 
                               'the race site, and delivery of bib pull-tags at the conclusion ' 
                               'of the event. Note: FSRC does not tally final race results ' 
                               'beyond the award winners. Race Directors are expected to use ' 
                               'the delivered bib pull-tags to generate race results.' 
                               '{% endif %}'
    }, 
    {   
        'contractType'       : ContractType.query.filter_by(contractType='race services').one, 
        'contractBlockType'  : ContractBlockType.query.filter_by(blockType='listitem').one,
        'templateType'       : TemplateType.query.filter_by(templateType='contract').one,
        'blockPriority'      : contractpriority,
        'block'              : '{% if "coursemarking" in servicenames %}' 
                               'Course Marking' 
                               '{% endif %}'
    }, 
    {   
        'contractType'       : ContractType.query.filter_by(contractType='race services').one, 
        'contractBlockType'  : ContractBlockType.query.filter_by(blockType='listitem2').one,
        'templateType'       : TemplateType.query.filter_by(templateType='contract').one,
        'blockPriority'      : contractpriority,
        'block'              : '{% if "coursemarking" in servicenames %}' 
                               'The race course will be marked with cones, directional signage and mile markers' 
                               '{% endif %}'
    }, 
    {   
        'contractType'       : ContractType.query.filter_by(contractType='race services').one, 
        'contractBlockType'  : ContractBlockType.query.filter_by(blockType='listitem').one,
        'templateType'       : TemplateType.query.filter_by(templateType='contract').one,
        'blockPriority'      : contractpriority,
        'block'              : '{% if "premiumpromotion" in servicenames %}' 
                               'Premium Promotion' 
                               '{% endif %}'
    }, 
    {   
        'contractType'       : ContractType.query.filter_by(contractType='race services').one, 
        'contractBlockType'  : ContractBlockType.query.filter_by(blockType='listitem2').one,
        'templateType'       : TemplateType.query.filter_by(templateType='contract').one,
        'blockPriority'      : contractpriority,
        'block'              : '{% if "premiumpromotion" in servicenames %}' 
                               'Your race will be included in twice-monthly email blasts to '
                               'the FSRC-maintained list of area race participants, starting '
                               'three months prior to your race date.' 
                               '{% endif %}'
    }, 
    {   
        'contractType'       : ContractType.query.filter_by(contractType='race services').one, 
        'contractBlockType'  : ContractBlockType.query.filter_by(blockType='listitem').one,
        'templateType'       : TemplateType.query.filter_by(templateType='contract').one,
        'blockPriority'      : contractpriority,
        'block'              : 'Results: Your race results will be published on the FSRC '
                               'website, if desired. Email results to results@steeplechasers.org. '
                               'Suggested format can be found on the Race Support Services '
                               'page of the FSRC website.' 
    }, 
    {   
        'contractType'       : ContractType.query.filter_by(contractType='race services').one, 
        'contractBlockType'  : ContractBlockType.query.filter_by(blockType='para').one,
        'templateType'       : TemplateType.query.filter_by(templateType='contract').one,
        'blockPriority'      : contractpriority,
        'block'              : '{% if "finishline" in servicenames or "coursemarking" in servicenames %}' 
                               'FSRC finish line, timing and course marking services apply only to the '
                               'competitive portion of the event. Walks or "fun runs" associated with the '
                               'event are not part of this agreement and are the sole responsibility of '
                               'the event organizer.' 
                               '{% endif %}'
    }, 
    {   
        'contractType'       : ContractType.query.filter_by(contractType='race services').one, 
        'contractBlockType'  : ContractBlockType.query.filter_by(blockType='para').one,
        'templateType'       : TemplateType.query.filter_by(templateType='contract').one,
        'blockPriority'      : contractpriority,
        'block'              : 'Thanks,\n'
                               'Race Support Team, Frederick Steeplechasers Running Club'
    }, 
    {   
        'contractType'       : ContractType.query.filter_by(contractType='race services').one, 
        'contractBlockType'  : ContractBlockType.query.filter_by(blockType='pagebreak').one,
        'templateType'       : TemplateType.query.filter_by(templateType='contract').one,
        'blockPriority'      : contractpriority,
        'block'              : '',
    }, 
    {   
        'contractType'       : ContractType.query.filter_by(contractType='race services').one, 
        'contractBlockType'  : ContractBlockType.query.filter_by(blockType='para').one,
        'templateType'       : TemplateType.query.filter_by(templateType='contract').one,
        'blockPriority'      : contractpriority,
        'block'              : RACE_AGREEMENT_HEADER
    }, 
    {   
        'contractType'       : ContractType.query.filter_by(contractType='race services').one, 
        'contractBlockType'  : ContractBlockType.query.filter_by(blockType='para').one,
        'templateType'       : TemplateType.query.filter_by(templateType='contract').one,
        'blockPriority'      : contractpriority,
        'block'              : 'Race Name:  {{ event }}\n'
                               'Location: {{ course.course }} - {{ course.address }}\n'
                               'Date/Time of Race:  {{ date }} {{ mainStartTime }}{{ mainTimeAmPm }}\n'
                               'Sponsoring Organization:  {{ client.client }}\n'
                               'Contact Person/Race Director: {{ client.contactFirstName }} {{ client.contactLastName }}\n'
                               'Maximum number of expected finishers: {{ maxParticipants }}'
    }, 
    {   
        'contractType'       : ContractType.query.filter_by(contractType='race services').one, 
        'contractBlockType'  : ContractBlockType.query.filter_by(blockType='para').one,
        'templateType'       : TemplateType.query.filter_by(templateType='contract').one,
        'blockPriority'      : contractpriority,
        'block'              : 'This agreement is between the FREDERICK STEEPLECHASERS RUNNING '
                               'CLUB (FSRC) and {{ client.client }}. The FSRC agrees to provide '
                               'limited race management services for the {{ event }}. '
                               'The Frederick Steeplechasers will provide the indicated services '
                               'for the event as shown below:'
    }, 
    {   
        'contractType'       : ContractType.query.filter_by(contractType='race services').one, 
        'contractBlockType'  : ContractBlockType.query.filter_by(blockType='tablehdr').one,
        'templateType'       : TemplateType.query.filter_by(templateType='contract').one,
        'blockPriority'      : contractpriority,
        'block'              : 'Service,Fee',
    }, 
    {   
        'contractType'       : ContractType.query.filter_by(contractType='race services').one, 
        'contractBlockType'  : ContractBlockType.query.filter_by(blockType='tablerow').one,
        'templateType'       : TemplateType.query.filter_by(templateType='contract').one,
        'blockPriority'      : contractpriority,
        'block'              : '{% for servicefee in servicefees %}'
                               '"{{ servicefee.service }}","${{ servicefee.fee }}"'
                               '{% endfor %}',
    }, 
    {   
        'contractType'       : ContractType.query.filter_by(contractType='race services').one, 
        'contractBlockType'  : ContractBlockType.query.filter_by(blockType='tablerowbold').one,
        'templateType'       : TemplateType.query.filter_by(templateType='contract').one,
        'blockPriority'      : contractpriority,
        'block'              : '"{{ totalfees.service }}","${{ totalfees.fee }}"',
    }, 
    {   
        'contractType'       : ContractType.query.filter_by(contractType='race services').one, 
        'contractBlockType'  : ContractBlockType.query.filter_by(blockType='para').one,
        'templateType'       : TemplateType.query.filter_by(templateType='contract').one,
        'blockPriority'      : contractpriority,
        'block'              : 'In providing the above services, neither the FSRC nor the RRCA '
                               'shall be considered as authorizing, approving, sponsoring or '
                               'endorsing the race or race sponsoring organization. The FSRC '
                               'assumes no responsibility for any aspect of overall race organization '
                               'or performance except as described above. The sponsoring organization '
                               'understands that the service provided by the FSRC is performed by '
                               'volunteers, using a timing methodology that has proven reasonably '
                               'accurate over many years. The accuracy of timing/results may be '
                               'impacted by conditions not under the control of the volunteers or '
                               'race organizers and is therefore not guaranteed. Further, the FSRC '
                               'assumes no liability regarding the race, its organizers, volunteers '
                               'or participants.'
    }, 
    {   
        'contractType'       : ContractType.query.filter_by(contractType='race services').one, 
        'contractBlockType'  : ContractBlockType.query.filter_by(blockType='para').one,
        'templateType'       : TemplateType.query.filter_by(templateType='contract').one,
        'blockPriority'      : contractpriority,
        'block'              : 'The sponsoring organization will carry comprehensive general '
                               'liability insurance (including coverage for products liability '
                               'and negligent acts), with limits of no less than One Million Dollars '
                               '($1,000,000) combined single limit per occurrence. Upon request, the '
                               'sponsoring organization will furnish a certificate of insurance '
                               'indicating that such coverages are in effect.'
    }, 
    {
        'contractType'       : ContractType.query.filter_by(contractType='race services').one, 
        'contractBlockType'  : ContractBlockType.query.filter_by(blockType='para').one,
        'templateType'       : TemplateType.query.filter_by(templateType='contract').one,
        'blockPriority'      : contractpriority,
        'block'              :
                               'Cancellation:\n'
                               'In the event that the client cancels our services after accepting '
                               'this agreement, the client will be responsible for:'
    }, 
    {
        'contractType'       : ContractType.query.filter_by(contractType='race services').one, 
        'contractBlockType'  : ContractBlockType.query.filter_by(blockType='listitem').one,
        'templateType'       : TemplateType.query.filter_by(templateType='contract').one,
        'blockPriority'      : contractpriority,
        'block'              :
                               '{% if "premiumpromotion" in servicenames %}'
                               'Premium Promotion: the full Premium Promotion fee if the race is '
                               'cancelled after the first promotional email has gone out'
                               '{% endif %}'
    }, 
    {
        'contractType'       : ContractType.query.filter_by(contractType='race services').one, 
        'contractBlockType'  : ContractBlockType.query.filter_by(blockType='listitem').one,
        'templateType'       : TemplateType.query.filter_by(templateType='contract').one,
        'blockPriority'      : contractpriority,
        'block'              :
                               '{% if "finishline" in servicenames or "coursemarking" in servicenames %}' 
                               "Finish Line and/or Course Marking: FSRC's cost of insurance ($50) if "
                               'the insurance premium has already been paid (generally 1-3 months prior to race date).'
                               '{% endif %}'
    },
    {   
        'contractType'       : ContractType.query.filter_by(contractType='race services').one, 
        'contractBlockType'  : ContractBlockType.query.filter_by(blockType='para').one,
        'templateType'       : TemplateType.query.filter_by(templateType='contract').one,
        'blockPriority'      : contractpriority,
        'block'              : 'Race Support Team, Frederick Steeplechasers Running Club'
    }, 
]

# contract email
contracts += [
    {   # for button html see https://www.copernica.com/en/blog/post/how-to-create-email-buttons-with-just-html-and-css
        # also https://litmus.com/blog/a-guide-to-bulletproof-buttons-in-email-design
        'contractType'       : ContractType.query.filter_by(contractType='race services').one, 
        'contractBlockType'  : ContractBlockType.query.filter_by(blockType='html').one,
        'templateType'       : TemplateType.query.filter_by(templateType='contract email').one,
        'blockPriority'      : contractmailpriority,
        'block'              : '<p>Hi {{ client.contactFirstName }},</p>\n'
                               '<p>To confirm your date and lock it in on the FSRC schedule, you '
                               'need to accept the Race Support Agreement.</p>\n'
                               '<p>Click to <a href={{ viewcontracturl }}>view</a> or \n'
                               '<a href={{ downloadcontracturl }}>download</a> your Race Support \n'
                               'Agreement for {{ event }} on {{ date }}. \n'
                               'If you need any changes please reply to this email. If everything \n'
                               'looks OK, please click the ACCEPT AGREEMENT button and follow the \n'
                               'directions.</p>\n'
                               # see html see https://www.copernica.com/en/blog/post/how-to-create-email-buttons-with-just-html-and-css
                               # also https://litmus.com/blog/a-guide-to-bulletproof-buttons-in-email-design
                               '<table width="100%" cellspacing="0" cellpadding="0">\n'
                               '  <tr>\n'
                               '      <td>\n'
                               '          <table cellspacing="0" cellpadding="0">\n'
                               '              <tr>\n'
                               '                  <td style="border-radius: 2px;" bgcolor="#0e76bd">\n'
                               '                      <a href="{{ acceptcontracturl }}" target="_blank" style="padding: 8px 12px; border: 1px solid #0e76bd;border-radius: 3px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #ffffff;text-decoration: none;font-weight:bold;display: inline-block;">\n'
                               '                          ACCEPT AGREEMENT             \n'
                               '                      </a>\n'
                               '                  </td>\n'
                               '              </tr>\n'
                               '          </table>\n'
                               '      </td>\n'
                               '  </tr>\n'
                               '</table>\n'
                               '<p>Your invoice should arrive soon after you accept the agreement, \n'
                               "but the payment isn't due until a few days before the race.</p>\n"
                               '<p>In order to get your listing on our \n'
                               '<a href=https://steeplechasers.org/events>website calendar</a>, we provide \n'
                               'the ability for the race director to manage the listing. That way, \n'
                               'you can customize it as you see fit. The link to get started is: \n'
                               '<a href=https://steeplechasers.org/events/community/add>https://steeplechasers.org/events/community/add</a>.</p>\n'
                               '{% if "premiumpromotion" in servicenames %}\n'
                               "<p>We'll add the race to our email promotion around three months \n"
                               'before your race date (or as soon as possible if that date has passed). \n'
                               "Please send along this year's artwork and \n"
                               'registration link when you have it.</p>\n'
                               '{% endif %}'
                               '<p>thanks,<br>\n'
                               'Race Support Team, Frederick Steeplechasers Running Club</p>\n'
    }, 
]

# accept agreement view
contracts += [
    {   
        'contractType'       : ContractType.query.filter_by(contractType='race services').one, 
        'contractBlockType'  : ContractBlockType.query.filter_by(blockType='html').one,
        'templateType'       : TemplateType.query.filter_by(templateType='accept agreement view').one,
        'blockPriority'      : acceptagreementpriority,
        'block'              : '\n'.join([
                               '{% extends "frontend_layout.jinja2" %}',
                               '{% block css %}',
                               '<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">',
                               '{% endblock css %}',
                               '{% block scripts %}',
                               '{% endblock scripts %}',
                               '{% block body %}',
                               '<form class="main" id="form" style="max-width: 480px;margin: 40px auto;" action={{ agreeurl }} method="post">',
                               '  <div id="forminner">',
                               '    <div class="row">',
                               '      <div class="col s12">',
                               '        <h5 class="center-align blue-text text-darken-4">Race Services Agreement - Frederick Steeplechasers Running Club</h4>',
                               '        <p>Please view or download agreement between Frederick Steeplechasers Running Club and ',
                               '        {{ client.contactFirstName }} {{ client.contactLastName }}, {{ client.client }} for {{ date }} ',
                               '        {{ event }}</p>',
                               '        <ul>',
                               '        <li><a target=_blank href={{ viewcontracturl }}>view agreement</a></li>',
                               '        <li><a href={{ downloadcontracturl }}>download agreement</a></li>',
                               '        </ul>',
                               '        <p>To confirm your date and lock it in on the FSRC schedule, fill in your ',
                               '        name and email address, then click the YES, I AGREE button.</p>',
                               '      </div>',
                               '    </div>',
                               '    <div class="row">',
                               '      <div class="input-field col s6">',
                               '        <input id="name" name="name" class="text" type="text" class="validate" required aria-required="true">',
                               '        <label for="name">Name *</label>',
                               '      </div>',
                               '    </div>',
                               '    <div class="row">',
                               '      <div class="input-field col s6">',
                               '        <input id="email" name="email" class="text" type="email" class="validate" required aria-required="true">',
                               '        <label for="email">E-mail *</label>',
                               '      </div>',
                               '    </div>',
                               '    <div class="row">',
                               '      <div class="input-field col s12">',
                               '        <textarea id="notes" name="notes" class="materialize-textarea"></textarea><br><br>',
                               '        <label for="notes">Notes</label>',
                               '      </div>',
                               '    </div>',
                               '    <div class="row">',
                               '      <div class="col s6">',
                               '        <button class="waves-effect waves-light btn submit-btn blue darken-4" type="submit">YES, I AGREE</button>',
                               '      </div>',
                               '    </div>',
                               '  </div>',  # forminner
                               '</form>',
                               '{% endblock body %}',
                              ])
    },
]

# accept agreement error view
contracts += [
    {   
        'contractType'       : ContractType.query.filter_by(contractType='race services').one, 
        'contractBlockType'  : ContractBlockType.query.filter_by(blockType='html').one,
        'templateType'       : TemplateType.query.filter_by(templateType='accept agreement error view').one,
        'blockPriority'      : acceptagreementerrorpriority,
        'block'              : 
                               '{% extends "frontend_layout.jinja2" %}\n'
                               '{% block body %}\n'
                               '<h1>ERROR</h1>\n'
                               'Contract not found or obsolete. Contact '
                               '<a href=mailto:{{ contracts_contact }}>{{ contracts_contact }}</a> \n'
                               'to request an updated contract email.\n'
                               '{% endblock body %}\n'
    }
]

# agreement accepted view
contracts += [
    {   
        'contractType'       : ContractType.query.filter_by(contractType='race services').one, 
        'contractBlockType'  : ContractBlockType.query.filter_by(blockType='html').one,
        'templateType'       : TemplateType.query.filter_by(templateType='agreement accepted view').one,
        'blockPriority'      : agreementacceptedpriority,
        'block'              : 
                               '{% if webview %}\n'
                               '{% extends "frontend_layout.jinja2" %}\n'
                               '{% endif %}\n'
                               '{% block body %}\n'
                               '{% if webview %}\n'
                               '<h1>Race Services Agreement Confirmed</h1>\n'
                               '<p>You will receive an email with the following information.</p>\n'
                               '{% else%}\n'
                               '<p>Your race services agreement is confirmed.</p>\n'
                               '{% endif %}\n'
                               '<p>Thank you for contracting with FSRC for race support services for \n'
                               '{{ event }} on {{ date }}. </p>\n'
                               '<ul>\n'
                               '<li><a target=_blank href={{ viewcontracturl }}>view agreement</a></li>\n'
                               '<li><a href={{ downloadcontracturl }}>download agreement</a></li>\n'
                               '</ul>\n'
                               '{% if "finishline" in servicenames or "coursemarking" in servicenames %}\n'
                               '<p>You will be hearing from us about five days prior to your event for \n'
                               'final coordination on our finish line services.</p>\n'
                               '{% endif %}\n'
                               '{% if "premiumpromotion" in servicenames %}\n'
                               "<p>We'll add the race to our email promotion around three months \n"
                               'before your race date (or as soon as possible if that date has passed). \n'
                               "Please send along this year's artwork and \n"
                               'registration link when you have it. To receive these, please subscribe to our mailings \n'
                               'at <a href=http://eepurl.com/bMW_Wf>http://eepurl.com/bMW_Wf</a>, \n'
                               'and be sure to check the Frederick Area Featured Races option.</p>\n'
                               '<p>After your race, please send email addresses of your participants to \n'
                               '<a href=mailto:communications@steeplechasers.org>communications@steeplechasers.org</a>. \n'
                               'These folks will be included in our mailings about Frederick area local \n'
                               'races. As a reminder, you should include a statement in your waiver \n'
                               'as follows, "I understand that I may receive emails about this race and other \n'
                               'races promoted by the Frederick Steeplechasers Running Club."</p>\n'
                               '{% endif %}\n'
                               '<p>If you have any questions or changes, please contact \n'
                               '<a href=mailto:raceservices@steeplechasers.org>raceservices@steeplechasers.org</a>.</p>\n'
                               '{% endblock body %}\n'
    },
]

# pre-race email
contracts += [
    {   # for button html see https://www.copernica.com/en/blog/post/how-to-create-email-buttons-with-just-html-and-css
        # also https://litmus.com/blog/a-guide-to-bulletproof-buttons-in-email-design
        'contractType'       : ContractType.query.filter_by(contractType='race services').one, 
        'contractBlockType'  : ContractBlockType.query.filter_by(blockType='html').one,
        'templateType'       : TemplateType.query.filter_by(templateType='pre-race email').one,
        'blockPriority'      : contractmailpriority,
        'block'              : '\n'.join([
                                '<p>Hi {{ client.contactFirstName }},</p>'
                                '<p>{{ event }} is coming up on {{ date }} {{ mainStartTime }} at {{ course.course }} {{ course.address }} ',
                                'and we wanted to make sure we have all our ducks in a row.</p>',
                                '{{ lead.name }} will be managing your race on race day, and can be contacted at ',
                                '{{ lead.email }} {{ lead.phone }}.</p>',
                                '<p>Please let us know how many runners you expect, so that we can make sure we have the ',
                                'right number of volunteers to support the race. This should be sent as a reply/all to this email.</p>',
                                '{% if "coursemarking" not in servicenames %}',
                                '<p>We plan to be there 30 minutes prior to your start time of Start time to get the finish line set up.</p>',
                                '{% endif %}',
                                '{% if "coursemarking" in servicenames %}',
                                '<p>We plan to be there 90 minutes prior to your start time of Start time to get the course marked. Some folks ',
                                'will be arriving 30 minutes prior to your start time to get the finish line set up.</p>',
                                '{% endif %}',
                                '<p>Please take the time to review the <a href={{ viewcontracturl }}>agreement</a> and let us know ',
                                'as soon as possible if anything has changed, at raceservices@steeplechasers.org.</p>',
                                '<p>thanks,<br>',
                                'Race Support Team, Frederick Steeplechasers Running Club</p>',
                               ])
    }, 
]

# lead email
contracts += [
    {   # for button html see https://www.copernica.com/en/blog/post/how-to-create-email-buttons-with-just-html-and-css
        # also https://litmus.com/blog/a-guide-to-bulletproof-buttons-in-email-design
        'contractType'       : ContractType.query.filter_by(contractType='race services').one, 
        'contractBlockType'  : ContractBlockType.query.filter_by(blockType='html').one,
        'templateType'       : TemplateType.query.filter_by(templateType='lead email').one,
        'blockPriority'      : contractmailpriority,
        'block'              : '\n'.join([
                                '<p>Hi {{ lead.name }},</p>'
                                '<p>{{ event }} is coming up on {{ date }} {{ mainStartTime }} at {{ course.course }} ',
                                '{{ course.address }}.</p>',
                                "Here's the customer information in case you need to contact them for any reason.",
                                '<table>',
                                '<tr><td>Organization</td><td>{{ client.client }}</td></tr>',
                                '<tr><td>Name</td><td>{{ client.contactFirstName }} {{ client.contactLastName }}</td></tr>',
                                '<tr><td>Email</td><td>{{ client.contactEmail }}</td></tr>',
                                '<tr><td>Phone</td><td>{{ client.clientPhone }}</td></tr>',
                                '</table>',
                                '<p>Our customer has contracted for the ',
                                "following services you'll be providing</p>",
                                '<ul>',
                                '{% for service in servicedescrs %}',
                                '  <li>{{ service }}</li>',
                                '{% endfor %}',
                                '</ul>',
                                '<p>Please record the following and send to raceservices@steeplechasers.org by replying ',
                                'to this email after the race.</p>',
                                '<ul>',
                                '  <li>the names of the volunteers who helped you</li>',
                                '  <li>the total number of finishers</li>',
                                '</ul>',
                                '<p>thanks,<br>',
                                'Race Support Team, Frederick Steeplechasers Running Club</p>',
                               ])
    }, 
]

# post-race email
contracts += [
    {   # for button html see https://www.copernica.com/en/blog/post/how-to-create-email-buttons-with-just-html-and-css
        # also https://litmus.com/blog/a-guide-to-bulletproof-buttons-in-email-design
        'contractType'       : ContractType.query.filter_by(contractType='race services').one, 
        'contractBlockType'  : ContractBlockType.query.filter_by(blockType='html').one,
        'templateType'       : TemplateType.query.filter_by(templateType='post-race email').one,
        'blockPriority'      : contractmailpriority,
        'block'              : '\n'.join([
                                "<p>Hi {{ client.contactFirstName }},</p><p>Thank you so much for using FSRC for race support services for {{ event }}.</p>",
                                "{% if surveylink %}",
                                "<p>If you'd like FSRC to post your results to the Results page of our website, please send these ",
                                "to results@steeplechasers.org. We recommend that you use our ",
                                '<a href="http://steeplechasers.org/wp-content/uploads/2014/12/raceresultstemplate.xls">race results template</a> ',
                                "for formatting your results file.</p>",
                                "{% endif %}",
                                "<p>We will tentatively hold your date {{ nextyeartext }}. It looks like your next race will fall on ",
                                " {{ renew_date }}. When you are ready to confirm, or if you'd like to consider a different date, please let us know. ",
                                "We would also appreciate knowing if you will not be using our services so that we can clear the date on our calendar.</p>",
                                "{% if surveylink %}",
                                "<p>And we'd love to hear how well you think we performed. Please take a ",
                                '<a href="{{ surveylink }}">very short survey</a> to let us know how we did.</p>',
                                '{% if "premiumpromotion" in servicenames %}',
                                "<p>So that your race participants are included in our mailings about Frederick area local races, please send the email addresses ",
                                "of your participants to communications@steeplechasers.org. This will also ensure that we are able to reach out to your runners ",
                                "when we promote your race next year</p>",
                                '{% endif %}',
                                '{% endif %}',
                                "<p>thanks,<br>",
                                "Race Support Team, Frederick Steeplechasers Running Club</p>",
                               ])
    }, 
]

# prempromo email
contracts += [
    {   # for button html see https://www.copernica.com/en/blog/post/how-to-create-email-buttons-with-just-html-and-css
        # also https://litmus.com/blog/a-guide-to-bulletproof-buttons-in-email-design
        'contractType'       : ContractType.query.filter_by(contractType='race services').one, 
        'contractBlockType'  : ContractBlockType.query.filter_by(blockType='html').one,
        'templateType'       : TemplateType.query.filter_by(templateType='prempromo email').one,
        'blockPriority'      : contractmailpriority,
        'block'              : '\n'.join([
                                 '<p>Hi {{ client.contactFirstName }},</p>',
                                 '<p>Thank you so much for using FSRC Premium Promotion for {{ event }}.</p>',
                                 '<p>It looks like your next event will fall on ',
                                 '{{ date }}. Would you like to use our Premium Promotion service again, highlighting your event as a ',
                                 '"featured race" in our every-other-week email blast to 12,000+ local runners?</p>',
                                 "<p>We'll begin advertising your race about 90 days before the event, so if you do want to use our services, ",
                                 "please let us know soon so that we can provide you with maximum exposure.</p>",
                                 '<p>thanks,',
                                 'Race Support Team, Frederick Steeplechasers Running Club</p>',
                               ])
    }, 
]

# sponsorship agreement
contracts += [
    {   
        'contractType'       : ContractType.query.filter_by(contractType='race sponsorship').one, 
        'contractBlockType'  : ContractBlockType.query.filter_by(blockType='html').one,
        'templateType'       : TemplateType.query.filter_by(templateType='sponsor agreement').one,
        'blockPriority'      : 10,
        'block'              : '\n'.join([
                                 '<header>{{ _raceheader_ }}</header>',
                                 '<h1>{{ level.level }} Sponsor Agreement</h1>',
                                 '<p>{{ _date_ }}</p>',
                                 '<p>This agreement is between {{ client.client }} (sponsor) and the Frederick Steeplechasers',
                                 'Running Club.</p>',
                                 '<p>{{ client.client }} agrees to a sponsorship of ${{ amount }}, corresponding to the',
                                 '"{{ level.level }}" sponsor level for the {{ race.race }}, to be held {{ _racedate_ }} ',
                                 'at {{ _raceloc_ }}.</p>',
                                 '<p>The sponsor benefits associated with the {{ level.level }} sponsorship are:</p>',
                                 '<ul>',
                                 '{% for benefit in _benefits_ %}',
                                 '  <li>{{ benefit }}</li>',
                                 '{% endfor %}',
                                 '</ul>',
                                 '<p>Thank you so much for agreeing to be part of this year\'s {{ race.race }}. ',
                                 'We couldn\'t be successful in our support for {{ _racebeneficiary_ }} without you!</p>',
                                 '<p>',
                                 '{{ race.racedirector }}',
                                 '{%- if race.isRDCertified %}',
                                 ', RRCA Certified Race Director',
                                 '{%- endif %}',
                                 '<br>{{ race.raceurl }}',
                                 '<br>Frederick Steeplechasers Running Club',
                                 '<br>{{ race.rdemail }}',
                                 '{%- if race.rdphone %}',
                                 ' {{ race.rdphone }}',
                                 '{%- endif %}',
                                 '</p>',
                                 '{%- if race.isRDCertified %}',
                                 '<img src="{{ _rdcertlogo_ }}", width=1.3in>',
                                 '{%- endif %}',
                                 '<footer><i>The Frederick Steeplechasers Running Club is a 501(3)(c) nonprofit organization. All contributions ',
                                 'are tax-deductible to the fullest extent allowed by law. FSRC Tax ID #51-0211400, RRCA Tax ID #23-7283854 ', 
                                 '(group exemption #2702)</i></footer>',
                               ])
    }, 
    {   'contractType'       : ContractType.query.filter_by(contractType='race sponsorship').one, 
        'contractBlockType'  : ContractBlockType.query.filter_by(blockType='html').one,
        'templateType'       : TemplateType.query.filter_by(templateType='sponsor email').one,
        'blockPriority'      : contractmailpriority,
        'block'              : '<p>Hi {{ client.contactFirstName }},</p>\n'
                               '<p>Thank you so much for your sponsorship of {{ race.race }}!</p>\n'
                               '<p>Click to <a href={{ viewcontracturl }}>view</a> or \n'
                               '<a href={{ downloadcontracturl }}>download</a> your Sponsorship \n'
                               'Agreement for {{ race.race }} on {{ _racedate_ }}. This agreement contains \n'
                               'all your benefits.\n'
                               '{% if couponcode and _couponcount_ %}\n'
                               '<p>For your {{ _couponcount_ }} complimentary entries, please register using coupon code \n'
                               '<b>{{ couponcode }}</b> by {{ _coupondate_ }}.</p>'
                               '{% endif %}\n'
                               '<p>Your invoice should arrive soon.</p>\n'
                               '<p>thanks again,<br>\n'
                               '{{ race.racedirector }}<br>\n'
                               'Race Director, {{ race.race }}\n'
                               'Frederick Steeplechasers Running Club</p>\n'
    }, ]

# define courses here
courses = [
    {'course':'Baker Park', 'address':'21 N. Bentz St, Frederick, MD 21701', 'isStandard':True},
    {'course':'Riverside Park', 'address':'Monocacy Blvd @ Laurel Wood Way, Frederick, MD 21701', 'isStandard':True},
    {'course':'Monocacy Village Park', 'address':'413 Delaware Rd, Frederick, MD 21701', 'isStandard':True},
    {'course':'Whittier', 'address':'2117 Independence St, Frederick, MD 21702', 'isStandard':True},
]

# define states here
states = [
    {'state':STATE_RENEWED_PENDING, 'description':'race was copied automatically to the next year ("renewed") during Post Race Processing or by clicking Renew button. The admin is expected to confirm with race director that the race will happen and that the date and other race details are correct. This is set automatically through Post Race Processing or after clicking Renew.'},
    {'state':STATE_TENTATIVE, 'description':'race director has confirmed race will be run again this year, but is not ready to receive the contract. This is set by the admin.'},
    {'state':STATE_CONTRACT_SENT, 'description':'race director has confirmed the date. Admin has sent contract to race director. This is set automatically.'},
    {'state':STATE_COMMITTED, 'description':'race director has signed contract (electronically). This is set automatically.'},
    {'state':STATE_CANCELED, 'description':"race will not take place, but we still want to keep this in the system so it wasn't deleted"},
]

# define fee types here basedOnField, addOn
feetypes = [
    {'feeType':'fixed',         'description':'fixed fee'},
    {'feeType':'basedOnField',  'description':'fee is based on another field'},
    {'feeType':'addOn',         'description':'service is an add on'},
]

services = [
    {'service':'finishline', 'serviceLong':'Finish Line', 'isCalendarBlocked': True, 'feeType': FeeType.query.filter_by(feeType='basedOnField').one, 'basedOnField':'maxParticipants'},
    {'service':'coursemarking', 'serviceLong':'Course Marking', 'isCalendarBlocked': True, 'feeType': FeeType.query.filter_by(feeType='fixed').one, 'fee':100},
    {'service':'premiumpromotion', 'serviceLong':'Premium Promotion', 'isCalendarBlocked': False, 'feeType':FeeType.query.filter_by(feeType='fixed').one, 'fee':75},
]

feebasedons = [
    {'service':Service.query.filter_by(service='finishline').one, 'fieldValue':200, 'fee':250},
    {'service':Service.query.filter_by(service='finishline').one, 'fieldValue':300, 'fee':300},
    {'service':Service.query.filter_by(service='finishline').one, 'fieldValue':400, 'fee':350},
    {'service':Service.query.filter_by(service='finishline').one, 'fieldValue':1000, 'fee':400},
]

daterules = [
    {'rule':'Easter'},
    {'rule':'date', 'month':'Dec', 'date':25},      # christmas
    {'rule':'Last', 'day':'Mon', 'month':'May'},    # memorial day
    {'rule':'First', 'day':'Mon', 'month':'Sep'},   # labor day
    {'rule':'Second', 'day':'Sat', 'month':'Sep'},  # In the Street / Market Street Mile
    {'rule':'First', 'day':'Sat', 'month':'Aug'},   # Women's Distance Festival
    {'rule':'Third', 'day':'Sun', 'month':'Sep'},   # Rick's Run
    {'rule':'Third', 'day':'Sat', 'month':'Jun'},   # Summer Solstice 8K
    {'rule':'Third', 'day':'Sat', 'month':'Oct'},   # Spook Hill [Mark]
    {'rule':'Last', 'day':'Sat', 'month':'Apr'},    # Makin Hay [Mark]
]

eventexceptions = [
    {'shortDescr': 'Easter', 'daterule': DateRule.query.filter_by(rulename='Easter').one, 'exception':'unavailable'},
    {'shortDescr': 'Christmas', 'daterule': DateRule.query.filter_by(rulename='Dec 25').one, 'exception':'unavailable'},
    {'shortDescr': 'Memorial Day', 'daterule': DateRule.query.filter_by(rulename='Last Mon May').one, 'exception':'available'},
    {'shortDescr': 'Labor Day', 'daterule': DateRule.query.filter_by(rulename='First Mon Sep').one, 'exception':'available'},
    {'shortDescr': 'Market Street Mile', 'daterule': DateRule.query.filter_by(rulename='Second Sat Sep').one, 'exception':'unavailable'},
    {'shortDescr': "Women's Distance Festival", 'daterule': DateRule.query.filter_by(rulename='First Sat Aug').one, 'exception':'unavailable'},
    {'shortDescr': "Rick's Run", 'daterule': DateRule.query.filter_by(rulename='Third Sun Sep').one, 'exception':'unavailable'},
    {'shortDescr': 'Summer Solstice 8K', 'daterule': DateRule.query.filter_by(rulename='Third Sat Jun').one, 'exception':'unavailable'},
    {'shortDescr': 'Spook Hill', 'daterule': DateRule.query.filter_by(rulename='Third Sat Oct').one, 'notes':'Mark Lawrence conflict', 'exception':'unavailable'},
    {'shortDescr': 'Makin Hay', 'daterule': DateRule.query.filter_by(rulename='Last Sat Apr').one, 'notes':'Mark Lawrence conflict', 'exception':'unavailable'},
]


def is_daterule_there(item):
    dr = DateRule(**item)
    return DateRule.query.filter_by(rulename=dr.rulename).one_or_none()

# initialize these tables
basemodelitems = [
    ModelItem(DateRule, daterules, False, is_daterule_there),
    ModelItem(EventAvailabilityException, eventexceptions, False, 'shortDescr'),
    ModelItem(State, states, False, 'state'),
    ModelItem(FeeType, feetypes, False, 'feeType'),
    ModelItem(Service, services, False, 'service'),
    ModelItem(FeeBasedOn, feebasedons),
    ModelItem(Course, courses, False, 'course'),
]

tagmodelitems = [
    ModelItem(Tag, tags, False, 'tag'),
]

contractmodelitems = [
    ModelItem(ContractType, contracttypes),
    ModelItem(TemplateType, templatetypes),
    ModelItem(ContractBlockType, blocktypes),
    ModelItem(Contract, contracts),
]

#----------------------------------------------------------------------
def dbinit_base():
#----------------------------------------------------------------------
    initdbmodels(basemodelitems)

#----------------------------------------------------------------------
def dbinit_tags():
#----------------------------------------------------------------------
    initdbmodels(tagmodelitems)

#----------------------------------------------------------------------
def dbinit_contracts():
#----------------------------------------------------------------------
    initdbmodels(contractmodelitems)