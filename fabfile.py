###########################################################################################
# fabfile  -- deployment using Fabric
#
#   Copyright 2019 Lou King
###########################################################################################
'''
fabfile  -- deployment using Fabric
=================================================================

'''

from fabric.api import env, run, cd

USERNAME = 'contractsmgr'
APP_NAME = 'contracts'
WSGI_SCRIPT = 'contracts.wsgi'

project_dir = ''

def sandbox():
    server = 'sandbox.contracts.loutilities.com'
    global project_dir
    project_dir = '/var/www/{}/{}'.format(server, APP_NAME)
    env.hosts = ["{}@{}".format(USERNAME, server)]

def beta():
    server = 'beta.contracts.loutilities.com'
    global project_dir
    project_dir = '/var/www/{}/{}'.format(server, APP_NAME)
    env.hosts = ["{}@{}".format(USERNAME, server)]

def prod():
    server = 'www.contracts.loutilities.com'
    global project_dir
    project_dir = '/var/www/{}/{}'.format(server, APP_NAME)
    env.hosts = ["{}@{}".format(USERNAME, server)]

def deploy(branchname='master'):
    with cd(project_dir):
        run('git pull')
        run('git checkout {}'.format(branchname))
        run('cp -R ../libs/js  contracts/static')
        run('cp -R ../libs/css contracts/static')
        # must source bin/activate before each command which must be done under venv
        # because each is a separate process
        run('source bin/activate; pip install -r requirements.txt')
        run('source bin/activate; alembic -c contracts/alembic.ini upgrade head')
        run('touch {}'.format(WSGI_SCRIPT))
