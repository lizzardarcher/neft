# # -*- encoding: utf-8 -*-
from glob import glob

command = '/opt/neft/venv/bin/gunicorn'
pythonpath = '/opt/neft'
bind = '0.0.0.0'
workers = 9
timeout = 600
accesslog = '-'
loglevel = 'info'
capture_output = True
enable_stdio_inheritance = True
reload = True
reload_extra_files = glob('/opt/neft/templates/**/*.html', recursive=True) + glob('/opt/neft/static/**/*.css', recursive=True)