#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
from os.path import abspath, dirname
from fabric.api import env, puts, abort, cd, hide, task
from fabric.operations import sudo, settings, run
from fabric.contrib import console
from .init_machine import test_configuration, _verify_sudo
from .setup_project import _install_requirements, virtenvrun
from fabric.colors import _wrap_with
green_bg = _wrap_with('42')
red_bg = _wrap_with('41')
fabric_utils_path = dirname(abspath(__file__))


##########################
## START Fabric tasks   ##
##########################


@task
def deploy():
    #  test configuration start
    if not test_configuration():
        if not console.confirm("Configuration test %s! Do you want to continue?" % red_bg('failed'), default=False):
            abort("Aborting at user request.")
    #  test configuration end
    _verify_sudo()
    if env.ask_confirmation:
        if not console.confirm("Are you sure you want to deploy in %s?" % red_bg(env.project.upper()), default=False):
            abort("Aborting at user request.")
    puts(green_bg('Start deploy...'))
    start_time = datetime.now()

    git_pull()
    _install_requirements()
    _prepare_django_project()
    _supervisor_restart()

    end_time = datetime.now()
    finish_message = '[%s] Correctly deployed in %i seconds' % \
    (green_bg(end_time.strftime('%H:%M:%S')), (end_time - start_time).seconds)
    puts(finish_message)


@task
def git_pull():
    with cd(env.code_root):
        sudo('git checkout %s' % env.default_branch)
        sudo('git pull origin %s' % env.default_branch)


########################
## END Fabric tasks   ##
########################

def _prepare_django_project():
    with cd(env.django_project_root):
        virtenvrun('./manage.py migrate --noinput --verbosity=1')
        virtenvrun('./manage.py collectstatic --noinput')


def _supervisor_restart():
    with settings(hide('running', 'stdout', 'stderr', 'warnings'), warn_only=True):
        res = sudo('%(supervisorctl)s restart %(supervisor_program_name)s' % env)

    if 'ERROR' in res:
        print("%s NOT STARTED!" % env.supervisor_program_name)
    else:
        print("%s correctly started!" % env.supervisor_program_name)
