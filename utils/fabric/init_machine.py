#!/usr/bin/env python
# -*- coding: utf-8 -*-
from copy import copy
from datetime import datetime
from os.path import abspath, dirname, join
from fabric.api import env, puts, abort, hide, task
from fabric.operations import sudo, settings, run
from fabric.contrib import console
from fabric.contrib.files import upload_template

from fabric.colors import _wrap_with, green

green_bg = _wrap_with('42')
red_bg = _wrap_with('41')
fabric_utils_path = dirname(abspath(__file__))

@task
def initMachine():
    #  test configuration start
    if not test_configuration():
        if not console.confirm("Configuration test %s! Do you want to continue?" % red_bg('failed'), default=False):
            abort("Aborting at user request.")
    #  test configuration end
    if env.ask_confirmation:
        if not console.confirm("Are you sure you want to setup %s?" % red_bg(env.project.upper()), default=False):
            abort("Aborting at user request.")
    puts(green_bg('Start setup...'))
    start_time = datetime.now()

    _verify_sudo
    sysctl()
    _create_django_user()
    _setup_directories()
    _upload_pip_conf()
    _install_dependencies()
    _install_virtualenv()
    _upload_db_init_script()
    end_time = datetime.now()
    finish_message = '[%s] Correctly finished in %i seconds' % \
    (green_bg(end_time.strftime('%H:%M:%S')), (end_time - start_time).seconds)
    puts(finish_message)

@task
def test_configuration(verbose=True):
    errors = []
    parameters_info = []
    if 'project' not in env or not env.project:
        errors.append('Project name missing')
    elif verbose:
        parameters_info.append(('Project name', env.project))
    if 'repository' not in env or not env.repository:
        errors.append('Repository url missing')
    elif verbose:
        parameters_info.append(('Repository url', env.repository))
    if 'hosts' not in env or not env.hosts:
        errors.append('Hosts configuration missing')
    elif verbose:
        parameters_info.append(('Hosts', env.hosts))
    if 'django_user' not in env or not env.django_user:
        errors.append('Django user missing')
    elif verbose:
        parameters_info.append(('Django user', env.django_user))
    if 'django_user_group' not in env or not env.django_user_group:
        errors.append('Django user group missing')
    elif verbose:
        parameters_info.append(('Django user group', env.django_user_group))
    if 'django_user_home' not in env or not env.django_user_home:
        errors.append('Django user home dir missing')
    elif verbose:
        parameters_info.append(('Django user home dir', env.django_user_home))
    if 'projects_path' not in env or not env.projects_path:
        errors.append('Projects path configuration missing')
    elif verbose:
        parameters_info.append(('Projects path', env.projects_path))
    if 'code_root' not in env or not env.code_root:
        errors.append('Code root configuration missing')
    elif verbose:
        parameters_info.append(('Code root', env.code_root))
    if 'django_project_root' not in env or not env.django_project_root:
        errors.append('Django project root configuration missing')
    elif verbose:
        parameters_info.append(('Django project root', env.django_project_root))
    if 'django_project_settings' not in env or not env.django_project_settings:
        env.django_project_settings = 'settings'
    if verbose:
        parameters_info.append(('django_project_settings', env.django_project_settings))
    if 'django_media_path' not in env or not env.django_media_path:
        errors.append('Django media path configuration missing')
    elif verbose:
        parameters_info.append(('Django media path', env.django_media_path))
    if 'django_static_path' not in env or not env.django_static_path:
        errors.append('Django static path configuration missing')
    elif verbose:
        parameters_info.append(('Django static path', env.django_static_path))
    if 'south_used' not in env:
        errors.append('"south_used" configuration missing')
    elif verbose:
        parameters_info.append(('south_used', env.south_used))
    if 'virtenv' not in env or not env.virtenv:
        errors.append('virtenv configuration missing')
    elif verbose:
        parameters_info.append(('virtenv', env.virtenv))
    if 'virtenv_options' not in env or not env.virtenv_options:
        errors.append('"virtenv_options" configuration missing, you must have at least one option')
    elif verbose:
        parameters_info.append(('virtenv_options', env.virtenv_options))
    if 'requirements_file' not in env or not env.requirements_file:
        env.requirements_file = join(env.code_root, 'requirements.txt')
    if verbose:
        parameters_info.append(('requirements_file', env.requirements_file))
    if 'ask_confirmation' not in env:
        errors.append('"ask_confirmation" configuration missing')
    elif verbose:
        parameters_info.append(('ask_confirmation', env.ask_confirmation))
    if 'gunicorn_bind' not in env or not env.gunicorn_bind:
        errors.append('"gunicorn_bind" configuration missing')
    elif verbose:
        parameters_info.append(('gunicorn_bind', env.gunicorn_bind))
    if 'gunicorn_logfile' not in env or not env.gunicorn_logfile:
        errors.append('"gunicorn_logfile" configuration missing')
    elif verbose:
        parameters_info.append(('gunicorn_logfile', env.gunicorn_logfile))
    if 'rungunicorn_script' not in env or not env.rungunicorn_script:
        errors.append('"rungunicorn_script" configuration missing')
    elif verbose:
        parameters_info.append(('rungunicorn_script', env.rungunicorn_script))
    if 'gunicorn_workers' not in env or not env.gunicorn_workers:
        errors.append('"gunicorn_workers" configuration missing, you must have at least one worker')
    elif verbose:
        parameters_info.append(('gunicorn_workers', env.gunicorn_workers))
    if 'gunicorn_worker_class' not in env or not env.gunicorn_worker_class:
        errors.append('"gunicorn_worker_class" configuration missing')
    elif verbose:
        parameters_info.append(('gunicorn_worker_class', env.gunicorn_worker_class))
    if 'gunicorn_loglevel' not in env or not env.gunicorn_loglevel:
        errors.append('"gunicorn_loglevel" configuration missing')
    elif verbose:
        parameters_info.append(('gunicorn_loglevel', env.gunicorn_loglevel))
    if 'nginx_server_name' not in env or not env.nginx_server_name:
        errors.append('"nginx_server_name" configuration missing')
    elif verbose:
        parameters_info.append(('nginx_server_name', env.nginx_server_name))
    if 'nginx_conf_file' not in env or not env.nginx_conf_file:
        errors.append('"nginx_conf_file" configuration missing')
    elif verbose:
        parameters_info.append(('nginx_conf_file', env.nginx_conf_file))
    if 'nginx_client_max_body_size' not in env or not env.nginx_client_max_body_size:
        env.nginx_client_max_body_size = 10
    elif not isinstance(env.nginx_client_max_body_size, int):
        errors.append('"nginx_client_max_body_size" must be an integer value')
    if verbose:
        parameters_info.append(('nginx_client_max_body_size', env.nginx_client_max_body_size))
    if 'nginx_htdocs' not in env or not env.nginx_htdocs:
        errors.append('"nginx_htdocs" configuration missing')
    elif verbose:
        parameters_info.append(('nginx_htdocs', env.nginx_htdocs))

    if 'nginx_https' not in env:
        env.nginx_https = False
    elif not isinstance(env.nginx_https, bool):
        errors.append('"nginx_https" must be a boolean value')
    elif verbose:
        parameters_info.append(('nginx_https', env.nginx_https))

    if 'supervisor_program_name' not in env or not env.supervisor_program_name:
        env.supervisor_program_name = env.project
    if verbose:
        parameters_info.append(('supervisor_program_name', env.supervisor_program_name))
    if 'supervisorctl' not in env or not env.supervisorctl:
        errors.append('"supervisorctl" configuration missing')
    elif verbose:
        parameters_info.append(('supervisorctl', env.supervisorctl))
    if 'supervisor_autostart' not in env or not env.supervisor_autostart:
        errors.append('"supervisor_autostart" configuration missing')
    elif verbose:
        parameters_info.append(('supervisor_autostart', env.supervisor_autostart))
    if 'supervisor_autorestart' not in env or not env.supervisor_autorestart:
        errors.append('"supervisor_autorestart" configuration missing')
    elif verbose:
        parameters_info.append(('supervisor_autorestart', env.supervisor_autorestart))
    if 'supervisor_redirect_stderr' not in env or not env.supervisor_redirect_stderr:
        errors.append('"supervisor_redirect_stderr" configuration missing')
    elif verbose:
        parameters_info.append(('supervisor_redirect_stderr', env.supervisor_redirect_stderr))
    if 'supervisor_stdout_logfile' not in env or not env.supervisor_stdout_logfile:
        errors.append('"supervisor_stdout_logfile" configuration missing')
    elif verbose:
        parameters_info.append(('supervisor_stdout_logfile', env.supervisor_stdout_logfile))
    if 'supervisord_appconf_file' not in env or not env.supervisord_appconf_file:
        errors.append('"supervisord_appconf_file" configuration missing')
    elif verbose:
        parameters_info.append(('supervisord_appconf_file', env.supervisord_appconf_file))

    if errors:
        if len(errors) == 29:
            ''' all configuration missing '''
            puts('Configuration missing! Please read README.rst first or go ahead at your own risk.')
        else:
            puts('Configuration test revealed %i errors:' % len(errors))
            puts('%s\n\n* %s\n' % ('-' * 37, '\n* '.join(errors)))
            puts('-' * 40)
            puts('Please fix them or go ahead at your own risk.')
        return False
    elif verbose:
        for parameter in parameters_info:
            parameter_formatting = "'%s'" if isinstance(parameter[1], str) else "%s"
            parameter_value = parameter_formatting % parameter[1]
            puts('%s %s' % (parameter[0].ljust(27), green(parameter_value)))
    puts('Configuration tests passed!')
    return True



def _create_django_user():
    with settings(hide('running', 'stdout', 'stderr', 'warnings'), warn_only=True):
        res = sudo('useradd -d %(django_user_home)s -m -r %(django_user)s' % env)
    if 'already exists' in res:
        puts('User \'%(django_user)s\' already exists, will not be changed.' % env)
        return
    #  set password
    sudo('passwd %(django_user)s' % env)


def _verify_sudo():
    ''' we just check if the user is sudoers '''
    sudo('cd .')


def _install_nginx():
    sudo("/etc/init.d/nginx start")


def _install_dependencies():
    ''' Ensure those Debian/Ubuntu packages are installed '''
    sudo("sed -i 's/http:\/\/.*ubuntu\.com/http:\/\/mirrors\.aliyun\.com/g' /etc/apt/sources.list")
    sudo("apt-get update")
    sudo("apt-get install -y software-properties-common")
    sudo("add-apt-repository ppa:deadsnakes/ppa")
    sudo("add-apt-repository \"deb http://apt.postgresql.org/pub/repos/apt/ xenial-pgdg main\"")
    sudo("wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -")
    sudo("apt-get update")
    packages = [
        "python-software-properties",
        "python3.6",
        "python3.6-dev",
        "libncurses5-dev",
        "build-essential",
        "python-pip",
        "supervisor",
        "postgresql-10",
        "redis-server",
        "postgresql-server-dev-10",
        "nginx",
        "autopostgresqlbackup",
        "bsdtar",
        "libffi-dev",
        "libcurl4-openssl-dev",
        "libssl-dev",
    ]
    sudo("apt-get -y install %s" % " ".join(packages))
    if "additional_packages" in env and env.additional_packages:
        sudo("apt-get -y install %s" % " ".join(env.additional_packages))
    _install_nginx()
    sudo("pip install --upgrade pip")


def _install_virtualenv():
    sudo('pip install virtualenv;pip install virtualenvwrapper;pip install autoenv')


def _setup_directories():
    sudo('mkdir -p %(projects_path)s' % env)
    # sudo('mkdir -p %(django_user_home)s/logs/nginx' % env)  # Not used
    # prepare gunicorn_logfile
    sudo('mkdir -p %s' % dirname(env.gunicorn_logfile))
    sudo('chown %s %s' % (env.django_user, dirname(env.gunicorn_logfile)))
    sudo('chmod -R 775 %s' % dirname(env.gunicorn_logfile))
    sudo('touch %s' % env.gunicorn_logfile)
    sudo('chown %s %s' % (env.django_user, env.gunicorn_logfile))
    # prepare supervisor_stdout_logfile
    sudo('mkdir -p %s' % dirname(env.supervisor_stdout_logfile))
    sudo('chown %s %s' % (env.django_user, dirname(env.supervisor_stdout_logfile)))
    sudo('chmod -R 775 %s' % dirname(env.supervisor_stdout_logfile))
    sudo('touch %s' % env.supervisor_stdout_logfile)
    sudo('chown %s %s' % (env.django_user, env.supervisor_stdout_logfile))

    sudo('mkdir -p %s' % dirname(env.nginx_conf_file))
    sudo('mkdir -p %s' % dirname(env.pip_conf_file))
    sudo('mkdir -p %s' % dirname(env.supervisord_appconf_file))
    sudo('mkdir -p %s' % dirname(env.supervisord_workerconf_file))
    sudo('mkdir -p %s' % dirname(env.rungunicorn_script))
    sudo('mkdir -p %(virtenv)s' % env)
    sudo('mkdir -p %(nginx_htdocs)s' % env)
    sudo('echo "<html><body>nothing here</body></html> " > %(nginx_htdocs)s/index.html' % env)


def _upload_pip_conf():
    context = copy(env)
    template = '%s/conf/%s' % (fabric_utils_path,  'pip.conf')
    upload_template(template, env.pip_conf_file,
                    context=context, backup=False, use_sudo=True)
    run('mkdir -p ~/.pip')
    run('ln -sf %s ~/.pip/%s' % (env.pip_conf_file, 'pip.conf'))

def _upload_db_init_script():
    context = copy(env)
    template = '%s/scripts/%s' % (fabric_utils_path,  'db_init.sh')
    upload_template(template, '/tmp/db_init.sh',
                    context=context, backup=False, use_sudo=True)
    sudo('sh /tmp/db_init.sh')


@task
# Sysctl security
def sysctl():
	puts(green("[*]") + " Modifying /etc/sysctl.conf")
	sudo("echo net.ipv4.ip_forward = 0 > /etc/sysctl.conf")
	sudo("echo net.ipv4.conf.all.send_redirects = 0 >> /etc/sysctl.conf")
	sudo("echo net.ipv4.conf.default.send_redirects = 0 >> /etc/sysctl.conf")
	sudo("echo net.ipv4.tcp_max_syn_backlog = 1280 >> /etc/sysctl.conf")
	sudo("echo net.ipv4.icmp_echo_ignore_broadcasts = 1 >> /etc/sysctl.conf")
	sudo("echo net.ipv4.conf.all.accept_source_route = 0 >> /etc/sysctl.conf")
	sudo("echo net.ipv4.conf.all.accept_redirects = 0 >> /etc/sysctl.conf")
	sudo("echo net.ipv4.conf.all.secure_redirects = 0 >> /etc/sysctl.conf")
	sudo("echo net.ipv4.conf.all.log_martians = 1 >> /etc/sysctl.conf")
	sudo("echo net.ipv4.conf.default.accept_source_route = 0 >> /etc/sysctl.conf")
	sudo("echo net.ipv4.conf.default.accept_redirects = 0 >> /etc/sysctl.conf")
	sudo("echo net.ipv4.conf.default.secure_redirects = 0 >> /etc/sysctl.conf")
	sudo("echo net.ipv4.icmp_echo_ignore_broadcasts = 1 >> /etc/sysctl.conf")
	sudo("echo net.ipv4.icmp_ignore_bogus_error_responses = 1 >> /etc/sysctl.conf")
	sudo("echo net.ipv4.tcp_syncookies = 1 >> /etc/sysctl.conf")
	sudo("echo net.ipv4.conf.default.rp_filter = 1 >> /etc/sysctl.conf")
	sudo("echo net.ipv4.tcp_timestamps = 0 >> /etc/sysctl.conf")

@task
def tune_system():
    sudo('echo "10152 65535" > /proc/sys/net/ipv4/ip_local_port_range')
    sudo('sysctl -w fs.file-max=128000')
    sudo('sysctl -w net.core.somaxconn=250000')
    sudo('sysctl -w net.ipv4.tcp_max_syn_backlog=2500')
    sudo('sysctl -w net.core.netdev_max_backlog=2500')
    sudo('ulimit -n 10240')
    sudo('sysctl -w fs.file-max=128000')
    sudo("echo net.core.somaxconn=250000 >> /etc/sysctl.conf")
    sudo("echo net.ipv4.tcp_max_syn_backlog=2500 >> /etc/sysctl.conf")
    sudo("echo net.core.netdev_max_backlog=2500 >> /etc/sysctl.conf")
    sudo("echo fs.file-max=128000 >> /etc/sysctl.conf")
    sudo("echo net.ipv4.ip_local_port_range=10152 65535 >> /etc/sysctl.conf")
    sudo("echo * soft nofile 10240 >> /etc/security/limits.conf")
    sudo("echo * hard nofile 10240 >> /etc/security/limits.conf")


