#   Copyright 2012-2013 OpenStack, LLC.
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

"""Network action implementations"""

from neutronclient.neutron.v2_0 import network as neu2
from neutronclient.neutron.v2_0 import nvpnetworkgateway
from openstackclient.network import v2_0 as v2_0


class CreateNetwork(v2_0.CreateCommand):
    """Create a network"""

    clazz = neu2.CreateNetwork

    def get_parser(self, prog_name):
        parser = super(CreateNetwork, self).get_parser(prog_name)
        parser.add_argument(
            '--admin-state-down',
            dest='admin_state', action='store_false',
            default=True, help='Set Admin State Up to false')
        parser.add_argument(
            '--shared',
            action='store_true',
            default=False, help='Set the network as shared')
        parser.add_argument(
            'name', metavar='NAME',
            help='Name of network to create')
        return parser


class DeleteNetwork(v2_0.DeleteCommand):
    """Delete a network"""

    clazz = neu2.DeleteNetwork
    name = 'id'
    metavar = '<network>'
    help_text = 'Name or ID of network to delete'


class ListNetwork(v2_0.ListCommand):
    """List networks"""

    def get_parser(self, prog_name):
        parser = super(ListNetwork, self).get_parser(prog_name)
        parser.add_argument(
            '--external',
            action='store_true',
            default=False,
            help='List external networks',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        if parsed_args.external:
            neuter = neu2.ListExternalNetwork(self.app, self.app_args)
        else:
            neuter = neu2.ListNetwork(self.app, self.app_args)
        neuter.get_client = self.get_client
        parsed_args.request_format = 'json'
        parsed_args.fields = []
        parsed_args.page_size = None
        parsed_args.sort_key = []
        parsed_args.sort_dir = []
        return neuter.take_action(parsed_args)


class SetNetwork(v2_0.SetCommand):
    """Set network values"""

    clazz = neu2.UpdateNetwork
    name = 'network'
    metavar = '<network>'
    help_text = 'Name or ID of network to set'


class ShowNetwork(v2_0.ShowCommand):
    """Show a network"""

    clazz = neu2.ShowNetwork
    name = 'id'
    metavar = '<network>'
    help_text = 'Name or ID of network to show'


class AddGatewayNetwork(v2_0.AddCommand):
    """Add a gateway to a network"""

    clazz = nvpnetworkgateway.ConnectNetworkGateway
    container_name = "network_id"
    container_metavar = "<network_id>"
    container_help_text = "ID of the internal network"
    name = 'net_gateway_id'
    metavar = '<gateway_id>'
    help_text = 'ID of the gatway'

    def get_parser(self, prog_name):
        parser = super(AddGatewayNetwork, self).get_parser(prog_name)
        parser.add_argument(
            '--segmentation-type',
            help=('L2 segmentation strategy on the external side of '
                  'the gateway (e.g.: VLAN, FLAT)'))
        parser.add_argument(
            '--segmentation-id',
            help=('Identifier for the L2 segment on the external side '
                  'of the gateway'))
        return parser


class RemoveGatewayNetwork(v2_0.RemoveCommand):
    """Remove a gateway from a network"""

    clazz = nvpnetworkgateway.ConnectNetworkGateway
    container_name = "network_id"
    container_metavar = "<network_id>"
    container_help_text = "ID of the internal network"
    name = 'net_gateway_id'
    metavar = '<gateway_id>'
    help_text = 'ID of the gatway'

    def get_parser(self, prog_name):
        parser = super(RemoveGatewayNetwork, self).get_parser(prog_name)
        parser.add_argument(
            '--segmentation-type',
            help=('L2 segmentation strategy on the external side of '
                  'the gateway (e.g.: VLAN, FLAT)'))
        parser.add_argument(
            '--segmentation-id',
            help=('Identifier for the L2 segment on the external side '
                  'of the gateway'))
        return parser
