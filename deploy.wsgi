import os
import sys
import site

base_path       = '/srv/summarybot'
packages        = '%s/venv/lib/python3.5/dist-packages' % base_path
packages64      = '%s/venv/lib64/python3.5/dist-packages' % base_path
venv_start      = '%s/venv/bin/activate_this.py' % base_path

# Add virtualenv site packages
site.addsitedir(packages)
site.addsitedir(packages64)

# Path of execution
sys.path.append(base_path)

# Fired up virtualenv before include application
exec(open(venv_start).read(), dict(__file__=venv_start))

# import app as application
from api import api as application