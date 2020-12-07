import crossplane
from flask import g
# import logging
import pprint

# log = logging.getLogger(__name__)
"""
    Response Object
    {
        "status": String, // "ok" or "failed" if "errors" is not empty
        "errors": Array,  // aggregation of "errors" from Config objects
        "config": Array   // Array of Config objects
    }
    
    Config Object
    {
        "file": String,   // the full path of the config file
        "status": String, // "ok" or "failed" if errors is not empty array
        "errors": Array,  // Array of Error objects
        "parsed": Array   // Array of Directive objects
    }
    
    Directive Object
    {
        "directive": String, // the name of the directive
        "line": Number,      // integer line number the directive started on
        "args": Array,       // Array of String arguments
        "includes": Array,   // Array of integers (included iff this is an include directive)
        "block": Array       // Array of Directive Objects (included iff this is a block)
    }
"""


class NginxConf():

    def __init__(self):
        pass
        # log.info(f'self: {self} ')

    def init_app(self, app):
        self.service_name = app.config.get('SERVICE_NAME')
        self.nginx_conf_file_path = app.config.get('NGINX_MAIN_CONF_PATH')
        self.service_conf_path = app.config.get('SERVICE_CONF_PATH')

        self.log = app.logger

        app.logger.info(f'self: {self} ')

    def parse_and_find_end_point(self, name):
        service_end_point_payload = crossplane.parse(self.nginx_conf_file_path)
        if service_end_point_payload.get('error'):
            return 400, "bad parsing"

        self.log.info(f'{pprint.pprint(service_end_point_payload)}')






    def passive_end_point(self, name):
        service_end_point = crossplane.parse(self.service_conf_path)
        pass

    def active_end_point(self, name):
        pass

    def bypass_end_point(self, name):
        pass

    def __repr__(self):
        return f'service_name: {self.service_name} ' \
               f'nginx_conf_file_path: {self.nginx_conf_file_path} ' \
               f'service_conf_path: {self.service_conf_path} '