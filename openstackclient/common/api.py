#   Copyright 2013 Nebula Inc.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#

"""API Action Implementation"""

import logging

from cliff import lister

from openstackclient.common import api_utils
from openstackclient.common import utils
from openstackclient.compute import client as compute_client
from openstackclient.identity import client as identity_client
from openstackclient.image import client as image_client
from openstackclient.volume import client as volume_client


# api list [--compute|--identity|--image|--volume|--current] [--supported]
# Returns a list of the API versions reported by the servers
# --supported Returns a list of the API versions supported by the OSC client

class ListAPI(lister.Lister):
    """List API versions supported by servers"""

    log = logging.getLogger(__name__ + '.ListAPI')

    def get_parser(self, prog_name):
        parser = super(ListAPI, self).get_parser(prog_name)
        api_group = parser.add_mutually_exclusive_group()
        api_group.add_argument(
            "--compute",
            dest="do_compute",
            action="store_true",
            default=False,
            help="Show available Compute APIs",
        )
        api_group.add_argument(
            "--identity",
            dest="do_identity",
            action="store_true",
            default=False,
            help="Show available Identity APIs",
        )
        api_group.add_argument(
            "--image",
            dest="do_image",
            action="store_true",
            default=False,
            help="Show available Image APIs",
        )
        api_group.add_argument(
            "--volume",
            dest="do_volume",
            action="store_true",
            default=False,
            help="Show available Volume APIs",
        )
        api_group.add_argument(
            "--current",
            action="store_true",
            default=False,
            help="Show current client API selections",
        )
        parser.add_argument(
            "--supported",
            action="store_true",
            default=False,
            help="Show APIs supported by OpenStackClient",
        )
        return parser

    def take_action(self, parsed_args):

        def _format_links(data):
            """Return a formatted links URL (self only)"""
            output = ""
            for s in data.links:
                if s['rel'] == 'self':
                    output += s['href'] + ", "
            return output[:-2]

        self.log.debug('take_action(%s)' % parsed_args)

        data = []
        if parsed_args.current:
            columns = [
                "Name",
                "Id",
            ]
            column_headers = [
                "Name",
                "Version",
            ]
            for api in self.app.api_version.keys():
                data.append(api_utils.ApiVersion(
                    name=api,
                    id=self.app.api_version[api],
                ))
        else:
            do_all = not parsed_args.do_compute \
                and not parsed_args.do_identity \
                and not parsed_args.do_image \
                and not parsed_args.do_volume

            if parsed_args.supported:
                columns = [
                    "Name",
                    "Id",
                ]
                column_headers = [
                    "Name",
                    "Version",
                ]
            else:
                columns = [
                    "Name",
                    "Id",
                    "Status",
                    "Links",
                    "Updated",
                ]
                column_headers = [
                    "Name",
                    "Version",
                    "Status",
                    "Links",
                    "Updated",
                ]
            if do_all or parsed_args.do_compute:
                if parsed_args.supported:
                    data += api_utils.get_client_versions(
                        'compute', compute_client.API_VERSIONS)
                else:
                    data += api_utils.get_server_versions(
                        'compute', "http://10.130.50.20:8774")
            if do_all or parsed_args.do_identity:
                if parsed_args.supported:
                    data += api_utils.get_client_versions(
                        'identity', identity_client.API_VERSIONS)
                else:
                    data += api_utils.get_server_versions(
                        'identity', self.app.options.os_auth_url)
            if do_all or parsed_args.do_image:
                if parsed_args.supported:
                    data += api_utils.get_client_versions(
                        'image', image_client.API_VERSIONS)
                else:
                    data += api_utils.get_server_versions(
                        'image', "http://10.130.50.20:9292")
            if do_all or parsed_args.do_volume:
                if parsed_args.supported:
                    data += api_utils.get_client_versions(
                        'volume', volume_client.API_VERSIONS)
                else:
                    data += api_utils.get_server_versions(
                        'volume', "http://10.130.50.20:8776")

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                    formatters={'Links': _format_links},
                ) for s in data))


class MatchAPI(lister.Lister):
    """Match API versionbetween client and server"""

    log = logging.getLogger(__name__ + '.MatchAPI')

    def get_parser(self, prog_name):
        parser = super(MatchAPI, self).get_parser(prog_name)
        parser.add_argument(
            "api",
            metavar="<api-name>",
            help="Match requested API version to available",
        )
        return parser

    def take_action(self, parsed_args):
        api_utils.negotiate_api_version(
            parsed_args.api,
            identity_client,
            self.app.options.os_auth_url,
            self.app.api_version[parsed_args.api],
        )
        return ({}, {})
