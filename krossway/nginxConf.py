import subprocess

import crossplane
from pathlib import Path
import copy
import logging
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
empty_location_directive_template = {'directive': 'location',
                                     'args': [],
                                     'block': []
                                     }

bypass_location_directive_template = {'directive': 'location',
                                      'args': [],
                                      'block': [
                                          {'directive': 'proxy_pass',
                                           'args': ['http://hackazon_server']
                                           }
                                      ]
                                      }

passive_location_directive_template = {'directive': 'location',
                                       'args': [],
                                       'block': [
                                           {'directive': 'proxy_intercept_errors', 'args': ['on']},
                                           {'directive': 'error_page', 'args': ['400', '=', '@hackazon_backend']},
                                           {'directive': 'error_page', 'args': ['403', '=', '@hackazon_backend']},
                                           {'directive': 'error_page', 'args': ['429', '=', '@hackazon_backend']},
                                           {'directive': 'error_page', 'args': ['500', '=', '@hackazon_backend']},
                                           {'directive': 'proxy_pass', 'args': ['https://sj4tt7tht4.execute-api.us-east-1.amazonaws.com/v1$request_uri']}
                                       ]
                                       }

active_location_directive_template = {'directive': 'location',
                                      'args': [],
                                      'block': [
                                          {'directive': 'proxy_pass',
                                           'args': ['https://sj4tt7tht4.execute-api.us-east-1.amazonaws.com/v1$request_uri']
                                           }
                                      ]
                                      }

# DUMMY_URI = '/krossway/dummy'
log = logging.getLogger(__name__)


class NginxConf():

    def __init__(self):
        pass
        # log.info(f'self: {self} ')

    def init_app(self, app):
        self.service_name = app.config.get('SERVICE_NAME')
        self.nginx_conf_file_path = app.config.get('NGINX_MAIN_CONF_PATH')
        self.service_conf_path = app.config.get('SERVICE_CONF_PATH')
        self.service_availble_conf_path = app.config.get('SERVICE_AVAILABLE_CONF_PATH')

        # log = app.logger

        app.logger.info(f'self: {self} ')

    def parse_and_find_end_point(self, name, action=None, create_none_existing=False):
        payload = crossplane.parse(self.nginx_conf_file_path)

        if payload.get('error'):
            log.error(f"Parsed config error: {payload.get('error')}")

            return 400, payload.get('error')

        config = payload.get('config', None)

        if config:
            if not config[0].get('errors'):
                server_parsed = self._find_file_conf(self.service_conf_path, config)

                if server_parsed:
                    server_directive = self._find_server_directive(name, server_parsed)

                    new_directive = self._find_location_directive_in_blocks(name, server_directive.get('block'), action, create_none_existing)
                    if new_directive:
                        self._generate_new_config_payload(config)

    def _find_file_conf(self, filename: Path, configs: list):
        log.info(f'looking for {filename} in the config blocks')
        for conf in configs:
            if filename.samefile(conf.get('file')):
                log.error(f'found {filename} conf block')
                return conf.get('parsed')

    def _find_server_directive(self, name, directives: list):
        log.info(f'looking for server directive')

        for directive in directives:
            # log.error(f"directives: {pprint.pprint(directive)} ")

            if directive.get('directive') == 'server':
                log.info(f'found server directive')
                return directive
        return None

    def _find_location_directive_in_blocks(self, name, directives: list, action, create_none_existing):
        log.debug(f'looking for {name} in the parsed config blocks')
        new_directive = None
        target_directive_index = -1

        if directives:
            for directive in directives:
                if directive.get('directive') == 'location':
                    if name in directive.get('args'):
                        log.debug(f'found matching location {name}')
                        # log.error(f'matched directive {directive}')
                        log.debug(f'action: {action}')

                        target_directive_index = directives.index(directive)
                        new_directive = self._generate_directive(directive, name, action)
                        # log.error(f'new directive {new_directive}')

            #if we didn't find any matching location and create new flag is set
            if target_directive_index == -1 and create_none_existing:
                log.info(f'didnt find matching directive creating new one')

                new_directive = self._generate_directive(empty_location_directive_template, name, action)
                directives.append(new_directive)


            # Update the original config with the new directive
            if target_directive_index != -1:
                directives[target_directive_index] = new_directive

        return new_directive



    def passive_end_point(self, directive, name):
        new_directive = copy.deepcopy(passive_location_directive_template)
        args_list: list = directive.get('args').copy()
        #for directive with options before the endpoint it will not work
        new_directive['args'] = list(set(args_list) | {name})
        return new_directive

    def active_end_point(self, directive, name):
        new_directive = copy.deepcopy(active_location_directive_template)
        args_list: list = directive.get('args').copy()
        #for directive with options before the endpoint it will not work
        new_directive['args'] = list(set(args_list) | {name})
        return new_directive

    def bypass_end_point(self, directive, name):
        new_directive = copy.deepcopy(bypass_location_directive_template)
        args_list: list = directive.get('args').copy()
        #for directive with options before the endpoint it will not work
        new_directive['args'] = list(set(args_list) | {name})
        return new_directive

    def _generate_directive(self, original_directive, name, action):
        if action == 'passive':
            return self.passive_end_point(original_directive, name)

        elif action == 'active':
            return self.active_end_point(original_directive, name)

        elif action == 'bypass':
            return self.bypass_end_point(original_directive, name)

        else:
            log.error(f'bad action {action}')
            return None


    def _generate_new_config_payload(self, configs):

        service_file_directive = self._find_file_conf(self.service_conf_path, configs)
        # log.error(f'service_file_directive config {service_file_directive}')
        try:
            post_build = crossplane.build(service_file_directive, tabs=True)
            self._dump_config_to_nginx_conf_file(post_build, self.service_availble_conf_path)
            self._reload_nginx()
        except Exception as ex:
            log.error(f'Config build failed')
            log.exception(f'{ex}')
            return False

        log.debug(f'Service Config after build:\n{post_build}')

    def _dump_config_to_nginx_conf_file(self, conf_str, output_file: Path):

        with output_file.open(mode='w+') as fio:
            log.info(f'writing new config to {output_file}')

            fio.write(conf_str)

    def _reload_nginx(self):
        output = subprocess.check_output(f'sudo nginx -s reload', shell=True)
        log.info(f'reload nginx output {output}')

    def __repr__(self):
        return f'service_name: {self.service_name} ' \
               f'nginx_conf_file_path: {self.nginx_conf_file_path} ' \
               f'service_conf_path: {self.service_conf_path} '