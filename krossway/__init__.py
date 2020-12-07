from flask import Flask
import click
import os
from krossway.config import app_config
from krossway.NginxConf import NginxConf
from pathlib import Path
URL_PREFIX = '/krossway'

nginxConf = NginxConf()


def create_app():
    env_name = os.getenv('FLASK_ENV', default='local')

    krossway_app = Flask(__name__)
    krossway_app.logger.debug('krossway app created')
    krossway_app.logger.debug(f'Env name: {env_name}')

    krossway_app.config.from_object(app_config[env_name])

    krossway_app.logger.error(f'Config: {krossway_app.config}')

    krossway_app.app_context().push()
    krossway_app.url_map.strict_slashes = False

    register_blueprints_for_app(krossway_app)

    # current_conf = krossway_app.config

    nginxConf.init_app(krossway_app)

    # nginxConf = NginxConf(service_name = current_conf.get('SERVICE_NAME'),
    #                       nginx_conf_file_path = current_conf.get('NGINX_MAIN_CONF_PATH'),
    #                       service_conf_path = current_conf.get('SERVICE_CONF_PATH'))

    return krossway_app





# read about Blueprints: http://flask.pocoo.org/docs/1.0/blueprints/
def register_blueprints_for_app(app):
    """
    register Flask blueprint

    :param app: Flask application object
    :return: none
    """

    from krossway.EndPoints import krossway_endpoint_handler

    # register the following blueprints with the given URL prefixes
    app.register_blueprint(krossway_endpoint_handler, url_prefix=f'{URL_PREFIX}')

