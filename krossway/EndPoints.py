from flask import Blueprint, request, current_app
from krossway import nginxConf
from pathlib import Path

import logging
import json

krossway_endpoint_handler = Blueprint('krossway_endpoint_handler', __name__)

log = logging.getLogger(__name__)

class EndPoints():


    def __init__(self):
        log.info(f'Init end points')

    @staticmethod
    @krossway_endpoint_handler.route('/endpoints', methods=['GET'])
    def list_endpoints():
        return "test list all end points"

    @staticmethod
    @krossway_endpoint_handler.route('/endpoints', methods=['PUT'])
    def update_custom_endpoint_state():
        resource_name = request.args.get('resource')
        action = request.args.get('action')

        if resource_name:
            target_location_conf = nginxConf.parse_and_find_end_point(resource_name, action, True)
        else:
            return f"Something bad happened"

        return f"Update {request.args.get('resource')} action {request.args.get('action')}"

    @staticmethod
    @krossway_endpoint_handler.route('/endpoints', methods=['POST'])
    def new_custom_endpoint_state():
        return f"New {request.args.get('resource')} endpoint, action {request.args.get('action')}"

    @staticmethod
    @krossway_endpoint_handler.route('/endpoints/root', methods=['PUT'])
    def update_root_endpoint_state():
        action = request.args.get('action')
        target_location_conf = nginxConf.parse_and_find_end_point(Path.home().root, action)

        return f"Update root action {request.args.get('action')}"
