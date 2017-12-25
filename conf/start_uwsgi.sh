#!/bin/bash
trap : 15
workon lqtripitaka
uwsgi ../uwsgi.ini &

#workon lqtripitaka ; nohup uwsgi ../uwsgi.ini &
