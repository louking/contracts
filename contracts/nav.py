###########################################################################################
# nav - navigation 
#
#       Date            Author          Reason
#       ----            ------          ------
#       07/06/18        Lou King        Create (from https://raw.githubusercontent.com/louking/rrwebapp/master/rrwebapp/nav.py)
#
#   Copyright 2018 Lou King.  All rights reserved
#
###########################################################################################
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
from flask_security import current_user
from flask import current_app

thisnav = Nav()

@thisnav.renderer()
class NavRenderer(SimpleRenderer):
    def visit_Subgroup(self, node):
        group = tags.ul(_class='subgroup')
        title = tags.div(node.title)

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
    events    = Subgroup('Events')
    services  = Subgroup('Services')
    sponsors  = Subgroup('Sponsorships')

    # event administrative stuff
    if current_user.has_role('event-admin') or current_user.has_role('super-admin'):

        # note calendar is in menu twice
        navbar.items.append(View('Calendar', 'admin.calendar'))

        navbar.items.append(events)
        events.items.append(View('Calendar', 'admin.calendar'))
        events.items.append(View('Table', 'admin.events-superadmin'))
        events.items.append(View('Races', 'admin.races'))
        events.items.append(View('Courses', 'admin.courses'))
        events.items.append(View('Leads', 'admin.leads'))
        events.items.append(View('Exceptions', 'admin.eventexceptions'))
        events.items.append(View('Tags', 'admin.tags'))
        if current_user.has_role('super-admin'):
            # replace Tags with super_tags
            events.items.pop()
            events.items.append(View('Tags', 'admin.super-tags'))

        navbar.items.append(View('Date Rules', 'admin.daterules'))

    # sponsor stuff
    if current_user.has_role('sponsor-admin') or current_user.has_role('super-admin'):
        navbar.items.append(sponsors)
        sponsors.items.append(View('Summary', 'admin.sponsorsummary'))
        sponsors.items.append(View('Sponsorships', 'admin.sponsorships'))
        sponsors.items.append(View('Query Log', 'admin.sponsorquerylog'))

    if current_user.has_role('event-admin') or current_user.has_role('sponsor-admin') or current_user.has_role('super-admin'):
        navbar.items.append(View('Clients', 'admin.clients-admin'))

    # superadmin stuff
    if current_user.has_role('super-admin'):

        sponsors.items.append(View('Races', 'admin.sponsorraces'))
        sponsors.items.append(View('Race Dates', 'admin.sponsorracedates'))
        sponsors.items.append(View('Race Variables', 'admin.sponsorracevbls'))
        sponsors.items.append(View('Levels', 'admin.sponsorlevels'))
        sponsors.items.append(View('Benefits', 'admin.sponsorbenefits'))

        navbar.items.append(View('Users', 'admin.users'))
        navbar.items.append(View('Roles', 'admin.roles'))

        events.items.append(View('States', 'admin.states'))

        navbar.items.append(services)
        services.items.append(View('Services', 'admin.services'))
        services.items.append(View('Add-Ons', 'admin.addon'))
        services.items.append(View('Fee Types', 'admin.feetype'))
        services.items.append(View('Fee Based On', 'admin.feebasedon'))

        navbar.items.append(contracts)
        contracts.items.append(View('Contracts', 'admin.contracts')),
        contracts.items.append(View('Contract Types', 'admin.contracttypes')),
        contracts.items.append(View('Template Types', 'admin.templatetypes')),
        contracts.items.append(View('Block Types', 'admin.contractblocktypes')),

        navbar.items.append(View('Debug', 'admin.debug'))

    # finally for non super-admin
    else:
        navbar.items.append(View('About', 'admin.sysinfo'))

    return navbar

thisnav.init_app(current_app)
