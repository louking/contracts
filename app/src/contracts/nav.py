'''
nav - navigation
======================
define navigation bar based on privileges
'''

# standard
from json import dumps

# pypi
from flask import url_for

# before importing Nav, monkey patch MutableMapping to use abc.MutableMapping, see https://stackoverflow.com/a/78863584/799921
import collections
collections.MutableMapping = collections.abc.MutableMapping

from flask_nav import Nav
from flask_nav.elements import Navbar, View, Subgroup, RawTag
from flask_nav.renderers import SimpleRenderer
from dominate.tags import a, ul, li
from dominate.util import raw
from flask_security import current_user, logout_user
from flask import current_app, session

# homegrown
from .dbmodel import SponsorRace

thisnav = Nav()

@thisnav.renderer()
class NavRenderer(SimpleRenderer):
    '''
    this generates nav_renderer renderer, referenced in the jinja2 code which builds the nav
    '''
    def visit_Subgroup(self, node):
        # a tag required by smartmenus
        title = a(node.title, href="#")
        group = ul(_class='subgroup')

        if node.active:
            title.attributes['class'] = 'active'

        for item in node.items:
            group.add(li(self.visit(item)))

        return [title, group]

    def visit_RawTag(self, node):
        return li(raw(node.content), **node.attribs)

@thisnav.navigation()
def nav_menu():
    navbar = Navbar('nav_menu')

    navbar.items.append(View('Home', 'frontend.index'))

    contracts = Subgroup('Contracts')
    client_races = Subgroup('Contract Races')
    services  = Subgroup('Contract Services')
    sponsors  = Subgroup('Signature Races')
    superadmin = Subgroup('Super')

    # event administrative stuff
    if current_user.has_role('event-admin') or current_user.has_role('super-admin'):

        navbar.items.append(client_races)
        client_races.items.append(View('Race Calendar', 'admin.calendar'))
        client_races.items.append(View('Race Table', 'admin.events-superadmin'))
        client_races.items.append(View('Races', 'admin.races'))
        client_races.items.append(View('Courses', 'admin.courses'))
        client_races.items.append(View('Leads', 'admin.leads'))
        client_races.items.append(View('Exceptions', 'admin.eventexceptions'))
        client_races.items.append(View('Date Rules', 'admin.daterules'))
        if not current_user.has_role('super-admin'):
            client_races.items.append(View('Tags', 'admin.tags'))
        else:
            client_races.items.append(View('Tags', 'admin.super-tags'))

    # sponsor stuff
    if current_user.has_role('sponsor-admin') or current_user.has_role('super-admin'):
        navbar.items.append(sponsors)
        
        races = SponsorRace.query.filter_by(display=True).all()
        raceopts = [{'label': r.race, 'value': r.id} for r in races if r.couponprovider=='RunSignUp' and r.couponproviderid]
        
        sponsors.items.append(
            RawTag( 
                # popup_form is referenced in beforedatatablesz.js $("a").click function
                a('Race Registrations', href='#', raceregistrations_popup=dumps({
                    'title': 'Choose Race',
                    'editoropts': {
                        'className': 'choose-race-form',
                        'fields': [
                            {'name': 'race', 'label': 'Race', 'type': 'select2', 'options': raceopts, 'def': 'racesession'},
                        ]
                    },
                    'buttons': [
                        {'label': 'Show Registrations',
                        'action': f'''
                                {{ 
                                    var args = {{race: this.get("race")}};
                                    var error = false;
                                    this.error("");
                                    for (var field in args) {{
                                        this.error(field, "");
                                        if (!args[field]) {{
                                            error = true;
                                            this.error(field, "must be supplied");
                                        }}
                                    }}
                                    if (error) {{
                                        this.error("check field errors");
                                        return;
                                    }}
                                    // args.desc = this.field("club").inst().find(":selected").text() + " - " + this.get("year") + " " + this.get("series");
                                    this.close();
                                    window.location.href = "{url_for('admin.raceregistrations')}?\" + $.param( args );
                                }}'''},
                    ],
                    # name of functions called with standalone editor instance and buttons field from above
                    'onopen': 'navraceregs_onopen',
                    'onclose': 'navraceregs_onclose',
                })
                ).render()
        ))
        sponsors.items.append(View('Sponsorship Summary', 'admin.sponsorsummary'))
        sponsors.items.append(View('Sponsorships', 'admin.sponsorships'))
        sponsors.items.append(View('Query Log', 'admin.sponsorquerylog'))
        if not current_user.has_role('super-admin'):
            sponsors.items.append(View('Tags', 'admin.sponsortags'))
        else:
            sponsors.items.append(View('Tags', 'admin.super-sponsortags'))

    if current_user.has_role('event-admin') or current_user.has_role('sponsor-admin') or current_user.has_role('super-admin'):
        navbar.items.append(View('Clients', 'admin.clients-admin'))

    # superadmin stuff
    if current_user.has_role('super-admin'):

        navbar.items.append(superadmin)
        superadmin.items.append(View('Sponsor Races', 'admin.sponsorraces'))
        superadmin.items.append(View('Sponsor Race Dates', 'admin.sponsorracedates'))
        superadmin.items.append(View('Sponsor Race Variables', 'admin.sponsorracevbls'))
        superadmin.items.append(View('Sponsor Levels', 'admin.sponsorlevels'))
        superadmin.items.append(View('Sponsor Benefits', 'admin.sponsorbenefits'))

        superadmin.items.append(services)
        services.items.append(View('Services', 'admin.services'))
        services.items.append(View('Add-Ons', 'admin.addon'))
        services.items.append(View('Fee Types', 'admin.feetype'))
        services.items.append(View('Fee Based On', 'admin.feebasedon'))

        superadmin.items.append(contracts)
        contracts.items.append(View('Contract Content', 'admin.contracts')),
        contracts.items.append(View('Contract Types', 'admin.contracttypes')),
        contracts.items.append(View('Template Types', 'admin.templatetypes')),
        contracts.items.append(View('Block Types', 'admin.contractblocktypes')),

        superadmin.items.append(View('Contract States', 'admin.states'))

        superadmin.items.append(View('Users', 'userrole.users'))
        superadmin.items.append(View('Roles', 'userrole.roles'))

        navbar.items.append(View('My Account', 'security.change_password'))
        navbar.items.append(View('Debug', 'admin.debug'))

    # finally for non super-admin
    else:
        navbar.items.append(View('My Account', 'security.change_password'))
        navbar.items.append(View('About', 'admin.sysinfo'))

    return navbar

thisnav.init_app(current_app)
