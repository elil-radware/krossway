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
        payload = crossplane.parse(self.nginx_conf_file_path)
        if payload.get('error'):
            return 400, payload.get('error')

        config = payload.get('config', None)

        if config:
            if not config[0].get('errors'):
                server_parsed = self._find_file_conf(self.service_conf_path, config)

                self.log.info(f'server parsed: {pprint.pprint(server_parsed)}')
                if server_parsed:
                    self._find_location_directive_in_blocks(name, server_parsed)

        self.log.info(f'{pprint.pprint(payload)}')


    def _find_file_conf(self, filename, configs: list):
        self.log.error(f'looking for {filename} in the config blocks')
        for conf in configs:
            if conf.get('file') == filename:
                self.log.error(f'found {filename} conf block')
                return conf.get('parsed')


    def _find_location_directive_in_blocks(self, name, directives: list):
        self.log.info(f'looking for {name} in the parsed config blocks')
        for directive in directives:
            if directive.get('location'):
                if name in directive.get('args'):
                    self.log.info(f'in {pprint.pprint(directive)} found server')

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