import os
import sys
import site

base_path       = '/home/ec2-user/summarybot'
packages        = '%s/venv/lib/python3.5/dist-packages' % base_path
packages64      = '%s/venv/lib64/python3.5/dist-packages' % base_path
execution       = '%s/app' % base_path
venv_start      = '%s/venv/bin/activate_this.py' % base_path

# Add virtualenv site packages
site.addsitedir(packages)
site.addsitedir(packages64)

# Path of execution
sys.path.append(execution)

# Fired up virtualenv before include application
exec(open(venv_start).read(), dict(__file__=venv_start))

# import app as application
import api