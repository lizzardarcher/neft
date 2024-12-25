# # -*- encoding: utf-8 -*-

command = '/opt/neft/env/bin/gunicorn'
pythonpath = '/opt/dicom_converter'
bind = '0.0.0.0'
workers = 5
timeout = 600
accesslog = '-'
loglevel = 'info'
capture_output = True
enable_stdio_inheritance = True
reload = True