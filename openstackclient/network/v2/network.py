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

"""Network action implementations"""

import logging
import six

from cliff import command
from cliff import lister
from cliff import show

from openstackclient.common import exceptions
from openstackclient.common import utils
from openstackclient.network import common


def network_filter(net):
    """Filter network objects"""

    if 'subnets' in net:
        net['subnets'] = utils.format_list(net['subnets'])
    if 'admin_state_up' in net:
        net['state'] = 'UP' if net['admin_state_up'] else 'DOWN'
        net.pop('admin_state_up')
    if 'router:external' in net:
        net['router_type'] = 'External' if net['router:external'] \
            else 'Internal'
        net.pop('router:external')
    if 'tenant_id' in net:
        net['project_id'] = net.pop('tenant_id')
    return net


class CreateNetwork(show.ShowOne):
    """Create a network"""

    log = logging.getLogger(__name__ + '.CreateNetwork')

    def get_parser(self, prog_name):
        parser = super(CreateNetwork, self).get_parser(prog_name)
        parser.add_argument(
            'name', metavar='<network_name>',
            help='Name of network to create')
        admin_group = parser.add_mutually_exclusive_group()
        admin_group.add_argument(
            '--enable',
            dest='admin_state',
            default=True,
            action='store_true',
            help='Set administrative state up')
        admin_group.add_argument(
            '--disable',
            dest='admin_state',
            action='store_false',
            help='Set administrative state down')
        share_group = parser.add_mutually_exclusive_group()
        share_group.add_argument(
            '--share',
            dest='shared', action='store_true',
            default=None,
            help='Share the network across tenants')
        share_group.add_argument(
            '--no-share',
            dest='shared', action='store_false',
            help='Do not share the network across tenants')
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        client = self.app.client_manager.network
        body = self.get_body(parsed_args)
        create_method = getattr(client, "create_network")
        data = create_method(body)['network']
        if data:
            data = network_filter(data)
        else:
            data = {'': ''}
        return zip(*sorted(six.iteritems(data)))

    def get_body(self, parsed_args):
        body = {'name': str(parsed_args.name),
                'admin_state_up': parsed_args.admin_state}
        if parsed_args.shared is not None:
            body['shared'] = parsed_args.shared
        return {'network': body}


class DeleteNetwork(command.Command):
    """Delete a network"""

    log = logging.getLogger(__name__ + '.DeleteNetwork')

    def get_parser(self, prog_name):
        parser = super(DeleteNetwork, self).get_parser(prog_name)
        parser.add_argument(
            'identifier',
            metavar="<network>",
            help=("Name or identifier of network to delete")
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        client = self.app.client_manager.network
        _id = common.find(client, 'network', 'networks',
                          parsed_args.identifier)
        delete_method = getattr(client, "delete_network")
        delete_method(_id)
        return


class ListNetwork(lister.Lister):
    """List networks"""

    log = logging.getLogger(__name__ + '.ListNetwork')

    def get_parser(self, prog_name):
        parser = super(ListNetwork, self).get_parser(prog_name)
        parser.add_argument(
            '--external',
            action='store_true',
            default=False,
            help='List external networks',
        )
        parser.add_argument(
            '--dhcp',
            help='ID of the DHCP agent')
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help='Long listing',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        client = self.app.client_manager.network
        if parsed_args.dhcp:
            list_method = getattr(client, 'list_networks_on_dhcp_agent')
            resources = 'networks_on_dhcp_agent'
            report_filter = {'dhcp_agent': parsed_args.dhcp}
            data = list_method(**report_filter)[resources]
            columns = ('ID',)
        else:
            report_filter = {}
            if parsed_args.external:
                report_filter = {'router:external': True}
            data = client.api.network_list(**report_filter)
            columns = ('ID', 'Name', 'Subnets')
        column_headers = columns

        if parsed_args.long and not parsed_args.dhcp:
            columns = (
                'ID',
                'Name',
                'Status',
                'project_id',
                'state',
                'Shared',
                'Subnets',
                'provider:network_type',
                'router_type',
            )
            column_headers = (
                'ID',
                'Name',
                'Status',
                'Project',
                'State',
                'Shared',
                'Subnets',
                'Network Type',
                'Router Type',
            )

        for d in data:
            d = network_filter(d)

        return (column_headers,
                (utils.get_dict_properties(
                    s, columns,
                    formatters={'subnets': utils.format_list},
                ) for s in data))


class SetNetwork(command.Command):
    """Set network properties"""

    log = logging.getLogger(__name__ + '.SetNetwork')

    def get_parser(self, prog_name):
        parser = super(SetNetwork, self).get_parser(prog_name)
        parser.add_argument(
            'identifier',
            metavar="<network>",
            help=("Name or identifier of network to set")
        )
        admin_group = parser.add_mutually_exclusive_group()
        admin_group.add_argument(
            '--enable',
            dest='admin_state',
            default=None,
            action='store_true',
            help='Set administrative state up')
        admin_group.add_argument(
            '--disable',
            dest='admin_state',
            action='store_false',
            help='Set administrative state down')
        parser.add_argument(
            '--name',
            metavar='<network_name>',
            help='New name for the network')
        share_group = parser.add_mutually_exclusive_group()
        share_group.add_argument(
            '--share',
            dest='shared', action='store_true',
            default=None,
            help='Share the network across tenants')
        share_group.add_argument(
            '--no-share',
            dest='shared', action='store_false',
            help='Do not share the network across tenants')
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        client = self.app.client_manager.network
        _id = common.find(client, 'network', 'networks',
                          parsed_args.identifier)
        body = {}
        if parsed_args.name is not None:
            body['name'] = str(parsed_args.name)
        if parsed_args.admin_state is not None:
            body['admin_state_up'] = parsed_args.admin_state
        if parsed_args.shared is not None:
            body['shared'] = parsed_args.shared
        if body == {}:
            msg = "Nothing specified to be set"
            raise exceptions.CommandError(msg)
        update_method = getattr(client, "update_network")
        update_method(_id, {'network': body})
        return


class ShowNetwork(show.ShowOne):
    """Show network details"""

    log = logging.getLogger(__name__ + '.ShowNetwork')

    def get_parser(self, prog_name):
        parser = super(ShowNetwork, self).get_parser(prog_name)
        parser.add_argument(
            'identifier',
            metavar="<network>",
            help=("Name or identifier of network to show")
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        client = self.app.client_manager.network
        net = client.api.find_attr(
            'networks',
            parsed_args.identifier,
        ) #['networks']
        data = network_filter(net)
        print "data: %s" % net
        return zip(*sorted(six.iteritems(data)))
