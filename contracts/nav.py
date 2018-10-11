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
from flask_nav.elements import Navbar, View
from flask_security import current_user
from flask import current_app

thisnav = Nav()

@thisnav.navigation()
def nav_menu():
    navbar = Navbar('nav_menu')

    navbar.items.append(View('Home', 'frontend.index'))

    # normal administrative stuff
    if current_user.has_role('admin') or current_user.has_role('superadmin'):
        navbar.items.append(View('Events', 'admin.events-superadmin'))
        navbar.items.append(View('Clients', 'admin.clients-admin'))
        navbar.items.append(View('Leads', 'admin.leads'))
        navbar.items.append(View('Courses', 'admin.courses'))

    # superadmin stuff
    if current_user.has_role('superadmin'):
        navbar.items.append(View('Users', 'admin.users'))
        navbar.items.append(View('Services', 'admin.services'))
        navbar.items.append(View('Add-Ons', 'admin.addon'))
        navbar.items.append(View('Fee Types', 'admin.feetype'))
        navbar.items.append(View('Roles', 'admin.roles'))
        navbar.items.append(View('States', 'admin.states'))
        navbar.items.append(View('Debug', 'admin.debug'))

    return navbar

thisnav.init_app(current_app)
