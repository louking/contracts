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
from flask_security import current_user
from flask import current_app

thisnav = Nav()

@thisnav.navigation()
def nav_menu():
    navbar = Navbar('nav_menu')

    navbar.items.append(View('Home', 'frontend.index'))

    # normal administrative stuff
    if current_user.has_role('admin') or current_user.has_role('superadmin'):
        navbar.items.append(View('Races', 'admin.races'))
        navbar.items.append(View('Events Table', 'admin.events-superadmin'))
        navbar.items.append(View('Events Calendar', 'admin.calendar'))
        navbar.items.append(View('Clients', 'admin.clients-admin'))
        navbar.items.append(View('Event Leads', 'admin.leads'))
        navbar.items.append(View('Event Courses', 'admin.courses'))
        navbar.items.append(View('Date Rules', 'admin.daterules'))
        navbar.items.append(View('Tags', 'admin.tags'))
        navbar.items.append(View('Event Exceptions', 'admin.eventexceptions'))

    # superadmin stuff
    if current_user.has_role('superadmin'):
        navbar.items.append(View('Users', 'admin.users'))
        navbar.items.append(View('Services', 'admin.services'))
        navbar.items.append(View('Add-Ons', 'admin.addon'))
        navbar.items.append(View('Fee Types', 'admin.feetype'))
        navbar.items.append(View('Fee Based On', 'admin.feebasedon'))
        navbar.items.append(View('Roles', 'admin.roles'))
        navbar.items.append(View('States', 'admin.states'))
        
        # TODO: Contracts won't expand for some reason
        # contracts = Subgroup('Contracts',
        #                      View('Contracts', 'admin.contracts'),
        #                      View('Contract Types', 'admin.contracttypes'),
        #                      View('Block Types', 'admin.contractblocktypes'),
        #                     )
        # navbar.items.append(contracts)
        navbar.items.append(View('Contracts', 'admin.contracts')),
        navbar.items.append(View('Contract Types', 'admin.contracttypes')),
        navbar.items.append(View('Template Types', 'admin.templatetypes')),
        navbar.items.append(View('Block Types', 'admin.contractblocktypes')),

        navbar.items.append(View('Debug', 'admin.debug'))

    return navbar

thisnav.init_app(current_app)
