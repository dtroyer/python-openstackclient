# Copyright 2012 OpenStack LLC.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#
# vim: tabstop=4 shiftwidth=4 softtabstop=4

"""
Server action implementations
"""

import logging
import os

from cliff import lister

from novaclient import client
from novaclient.v1_1 import servers

from openstackclient.common import command
from openstackclient.common import utils


def _find_server(cs, server):
    """Get a server by name or ID."""
    return utils.find_resource(cs.servers, server)


def _print_server(cs, server):
    # By default when searching via name we will do a
    # findall(name=blah) and due a REST /details which is not the same
    # as a .get() and doesn't get the information about flavors and
    # images. This fix it as we redo the call with the id which does a
    # .get() to get all informations.
    if not 'flavor' in server._info:
        server = _find_server(cs, server.id)

    networks = server.networks
    info = server._info.copy()
    for network_label, address_list in networks.items():
        info['%s network' % network_label] = ', '.join(address_list)

    flavor = info.get('flavor', {})
    flavor_id = flavor.get('id', '')
    info['flavor'] = _find_flavor(cs, flavor_id).name

    image = info.get('image', {})
    image_id = image.get('id', '')
    info['image'] = _find_image(cs, image_id).name

    info.pop('links', None)
    info.pop('addresses', None)

    utils.print_dict(info)


# FIXME(dhellmann): Create "client factory" plugins for each API type?
def get_authenticated_client(options, service_type):
    """Return a Nova client instance after authenticating it.

    :param options: argparse Namespace with option values for connecting
    :param service_type: string name of the service type
    """
    nova_client = client.Client(
        options.os_compute_api_version,
        options.os_username,
        options.os_password,
        options.os_tenant_name,
        options.os_auth_url,
        options.insecure,
        region_name=options.os_region_name,
        # FIXME(dhellmann): get endpoint_type from option?
        endpoint_type='publicURL',
        # FIXME(dhellmann): add extension discovery
        extensions=[],
        service_type=service_type,
        # FIXME(dhellmann): what is service_name?
        service_name='',
        )
    nova_client.authenticate()
    return nova_client


def _format_servers_list_networks(server):
    output = []
    for (network, addresses) in server.networks.items():
        if len(addresses) == 0:
            continue
        addresses_csv = ', '.join(addresses)
        group = "%s=%s" % (network, addresses_csv)
        output.append(group)
    return '; '.join(output)


def get_server_properties(server, fields, formatters={}):
    """Return a tuple containing the server properties.

    :param server: a single Server resource
    :param fields: tuple of strings with the desired field names
    :param formatters: dictionary mapping field names to callables
       to format the values
    """
    row = []
    mixed_case_fields = ['serverId']

    for field in fields:
        if field in formatters:
            row.append(formatters[field](server))
        else:
            if field in mixed_case_fields:
                field_name = field.replace(' ', '_')
            else:
                field_name = field.lower().replace(' ', '_')
            data = getattr(server, field_name, '')
            row.append(data)
    return tuple(row)


class List_Server(command.OpenStackCommand, lister.Lister):
    "List server command."

    api = 'compute'
    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(List_Server, self).get_parser(prog_name)
        parser.add_argument(
            '--reservation-id',
            help='only return instances that match the reservation',
            )
        parser.add_argument(
            '--ip',
            help='regular expression to match IP address',
            )
        parser.add_argument(
            '--ip6',
            help='regular expression to match IPv6 address',
            )
        parser.add_argument(
            '--name',
            help='regular expression to match name',
            )
        parser.add_argument(
            '--instance-name',
            help='regular expression to match instance name',
            )
        parser.add_argument(
            '--status',
            help='search by server status',
            # FIXME(dhellmann): Add choices?
            )
        parser.add_argument(
            '--flavor',
            help='search by flavor ID',
            )
        parser.add_argument(
            '--image',
            help='search by image ID',
            )
        parser.add_argument(
            '--host',
            metavar='HOSTNAME',
            help='search by hostname',
            )
        parser.add_argument(
            '--all-tenants',
            action='store_true',
            default=False,
            help='display information from all tenants (admin only)',
            )
        return parser

    def get_data(self, parsed_args):
        nova_client = get_authenticated_client(self.app.options, self.api)
        all_tenants = bool(int(os.environ.get("ALL_TENANTS", 0)))
        search_opts = {
            'all_tenants': all_tenants,
            'reservation_id': parsed_args.reservation_id,
            'ip': parsed_args.ip,
            'ip6': parsed_args.ip6,
            'name': parsed_args.name,
            'image': parsed_args.image,
            'flavor': parsed_args.flavor,
            'status': parsed_args.status,
            'host': parsed_args.host,
            'instance_name': parsed_args.instance_name,
            }
        self.log.debug('search options: %s', search_opts)
        # FIXME(dhellmann): Consider adding other columns
        columns = ('ID', 'Name', 'Status', 'Networks')
        data = nova_client.servers.list(search_opts=search_opts)
        return (columns,
                (get_server_properties(
                    s, columns,
                    formatters={'Networks': _format_servers_list_networks},
                    ) for s in data),
                )


class Show_Server(command.OpenStackCommand):
    "Show server command."

    api = 'compute'
    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Show_Server, self).get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help='Name or ID of server to display')
        return parser

    def run(self, parsed_args):
        self.log.info('v2.Show_Server.run(%s)' % parsed_args)
        #s = _find_server(cs, args.server)
        #_print_server(cs, s)
