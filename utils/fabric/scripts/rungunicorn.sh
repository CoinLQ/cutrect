#!/bin/bash
set -e
# go in your project root
cd %(django_project_root)s
# set PYTHONPATH to cwd

# echo "10152 65535" > /proc/sys/net/ipv4/ip_local_port_range
# sysctl -w fs.file-max=128000
# sysctl -w net.ipv4.tcp_keepalive_time=300
# sysctl -w net.core.somaxconn=250000
# sysctl -w net.ipv4.tcp_max_syn_backlog=2500
# sysctl -w net.core.netdev_max_backlog=2500
# ulimit -n 10240

export PYTHONPATH=`pwd`
export DJANGO_SETTINGS_MODULE=%(project)s.settings
export AWS_ACCESS_KEY=1
export AWS_SECRET_KEY=2
export EMAIL_PW=3
# activate the virtualenv
source %(virtenv)s/bin/activate
# start gunicorn with all options earlier declared in fabfile.py
exec  %(virtenv)s/bin/gunicorn %(project)s.wsgi:application -w %(gunicorn_workers)s \
    --user=%(django_user)s --group=%(django_user_group)s \
    --bind=%(gunicorn_bind)s --log-level=%(gunicorn_loglevel)s \
    --log-file=%(gunicorn_logfile)s 2>>%(gunicorn_logfile)s



