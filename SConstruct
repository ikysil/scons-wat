import os
env = Environment()
#Add option to install to individual projects
db_site = os.path.join(os.path.expanduser('~'),'.scons','site_scons','site_tools','watcom')
env.Install(db_site, ['__init__.py', 'watcom.py'])
env.Alias('install', db_site)
