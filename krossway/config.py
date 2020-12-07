# /src/config.py

import os
from pathlib import Path

class LocalEnv(object):
    """
    Development environment configuration
    """
    DEBUG = True
    TESTING = False
    SERVICE_NAME = 'hackzon'
    SERVICE_NAME_CONF = 'hackzon.conf'
    NGINX_CONF = 'nginx.conf'
    NGINX_MAIN_CONF_PATH = Path(r'C:\Users\elil\Documents\nginx', NGINX_CONF)
    SERVICE_CONF_PATH = Path(r'C:\Users\elil\Documents\nginx', SERVICE_NAME_CONF)

class AWSEnv(object):
    """
    Production environment configurations
    """
    DEBUG = True
    TESTING = False
    SERVICE_NAME = 'hackzon'
    SERVICE_NAME_CONF = 'hackzon'
    NGINX_CONF = 'nginx.conf'
    NGINX_MAIN_CONF_PATH = Path('/etc/nginx', NGINX_CONF)
    SERVICE_CONF_PATH = Path('/etc/nginx/sites-enabled', SERVICE_NAME_CONF)

app_config = {
    'development': LocalEnv,
    'aws': AWSEnv,
}