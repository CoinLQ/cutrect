#!/usr/bin/env python
# -*- coding: utf-8 -*-
from os.path import join
from fabric.api import env, task
from utils.fabric.tasks import *
from utils.fabric.init_machine import initMachine, tune_system
from utils.fabric.setup_project import setup_project, public_webpage

@task
def cutrect():
    #  name of your project - no spaces, no special chars
    env.project = 'cutrect'
    env.login_user = 'xiandian'
    env.target_ips = ['192.168.2.227']
    #  git repository of your project
    env.repository = 'https://github.com/CoinLQ/cutrect.git'
    env.default_branch = 'deploy'
    #  hosts to deploy your project, users must be sudoers
    env.hosts = [ "%s@%s" %(env.login_user, ip) for ip in env.target_ips]
    # additional packages to be installed on the server
    env.additional_packages = [
        'git',
    ]
    #  system user, owner of the processes and code on your server
    #  the user and it's home dir will be created if not present
    env.django_user = 'django'
    # user group
    env.django_user_group = env.django_user
    #  the code of your project will be located here
    env.django_user_home = join('/opt', env.django_user)
    #  projects path
    env.projects_path = join(env.django_user_home, 'projects')
    #  the root path of your project
    env.code_root = join(env.projects_path, env.project)
    #  the path where manage.py of this project is located
    env.django_project_root = env.code_root
    #  the Python path to a Django settings module.
    env.django_project_settings = 'settings'
    #  django media dir
    env.django_media_path = '/www/cutrect/media'
    #  django static dir
    env.django_static_path = '/www/cutrect/static'
    #  django media url and root dir
    env.django_media_url = '/media/'
    env.django_media_root = '/www/cutrect'
    #  django static url and root dir
    env.django_static_url = '/static/'
    # env.django_static_root = env.code_root
    env.django_static_root = '/www/cutrect'
    #  do you use south in your django project?
    env.south_used = True
    #  virtualenv root
    env.virtenv = join(env.django_user_home, 'envs', env.project)
    #  some virtualenv options, must have at least one
    env.virtenv_options = ['distribute', 'no-site-packages', ]
    #  location of your pip requirements file
    #  http://www.pip-installer.org/en/latest/requirements.html#the-requirements-file-format
    #  set it to None to not use
    env.requirements_file = join(env.code_root, 'requirements.txt')
    #  always ask user for confirmation when run any tasks
    env.ask_confirmation = False

    #   START gunicorn settings ###
    #  be sure to not have anything running on that port
    env.gunicorn_bind = "127.0.0.1:8100"
    env.gunicorn_logfile = '%(django_user_home)s/logs/projects/%(project)s_gunicorn.log' % env
    env.rungunicorn_script = '%(django_user_home)s/scripts/rungunicorn_%(project)s.sh' % env
    env.gunicorn_workers = 2
    env.gunicorn_worker_class = "eventlet"
    env.gunicorn_loglevel = "info"
    #   END gunicorn settings ###

    #   START nginx settings ###
    env.nginx_server_name = 'ccapi.lqdzj.cn'  # Only domain name, without 'www' or 'http://'
    env.nginx_conf_file = '%(django_user_home)s/configs/nginx/%(project)s.conf' % env
    env.nginx_webpage_conf_file = '%(django_user_home)s/configs/nginx/nginx_webpage.conf' % env
    env.nginx_client_max_body_size = 10  # Maximum accepted body size of client request, in MB
    env.nginx_htdocs = '%(django_user_home)s/htdocs' % env
    # will configure nginx with ssl on, your certificate must be installed
    # more info here: http://wiki.nginx.org/HttpSslModule
    env.nginx_https = False
    #   END nginx settings ###

    ### START china pip settings ###
    env.pip_conf_file = '%(django_user_home)s/configs/pip/pip.conf' % env
    ### END china pip settings ###

    #   START supervisor settings ###
    # http://supervisord.org/configuration.html#program-x-section-settings
    # default: env.project
    env.supervisor_program_name = env.project
    env.supervisorctl = '/usr/bin/supervisorctl'  # supervisorctl script
    env.supervisor_autostart = 'true'  # true or false
    env.supervisor_autorestart = 'true'  # true or false
    env.supervisor_redirect_stderr = 'true'  # true or false
    env.supervisor_stdout_logfile = '%(django_user_home)s/logs/projects/supervisord_%(project)s.log' % env
    env.supervisord_appconf_file = '%(django_user_home)s/configs/supervisord/%(project)s.conf' % env
    env.supervisord_workerconf_file = '%(django_user_home)s/configs/supervisord/%(project)s_worker.conf' % env
    env.supervisord_beatconf_file = '%(django_user_home)s/configs/supervisord/%(project)s_beat.conf' % env
    env.worker_logfile = '%(django_user_home)s/logs/%(project)s/%(project)s_celery_work.log' % env
    env.beat_logfile = '%(django_user_home)s/logs/%(project)s/%(project)s_celery_beat.log' % env
    #  END supervisor settings ###
    env.supervisor_celery_worker_name = 'prod-celery'
