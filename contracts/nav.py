'''
nav - navigation
======================
define navigation bar based on privileges
'''

# standard

# pypi
from flask_nav import Nav
from flask_nav.elements import Navbar, View, Subgroup
from flask_nav.renderers import SimpleRenderer
from dominate import tags
from flask_security import current_user, logout_user
from flask import current_app, session

thisnav = Nav()

@thisnav.renderer()
class NavRenderer(SimpleRenderer):
    def visit_Subgroup(self, node):
        # 'a' tag required by smartmenus
        title = tags.a(node.title, href="#")
        group = tags.ul(_class='subgroup')

        if node.active:
            title.attributes['class'] = 'active'

        for item in node.items:
            group.add(tags.li(self.visit(item)))

        return [title, group]

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
        sponsors.items.append(View('Race Registrations', 'admin.raceregistrations'))
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
