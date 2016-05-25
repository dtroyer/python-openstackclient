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

"""Subnet action implementations"""

import copy

from osc_lib.cli import parseractions
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib.i18n import _
from osc_lib import utils

from openstackclient.identity import common as identity_common


def _format_allocation_pools(data):
    pool_formatted = ['%s-%s' % (pool.get('start', ''), pool.get('end', ''))
                      for pool in data]
    return ','.join(pool_formatted)


def _format_host_routes(data):
    # Map the host route keys to match --host-route option.
    return utils.format_list_of_dicts(convert_entries_to_gateway(data))


_formatters = {
    'allocation_pools': _format_allocation_pools,
    'dns_nameservers': utils.format_list,
    'host_routes': _format_host_routes,
}


def _get_common_parse_arguments(parser):
    parser.add_argument(
        '--allocation-pool',
        metavar='start=<ip-address>,end=<ip-address>',
        dest='allocation_pools',
        action=parseractions.MultiKeyValueAction,
        required_keys=['start', 'end'],
        help=_("Allocation pool IP addresses for this subnet "
               "e.g.: start=192.168.199.2,end=192.168.199.254 "
               "(repeat option to add multiple IP addresses)")
    )
    parser.add_argument(
        '--dns-nameserver',
        metavar='<dns-nameserver>',
        action='append',
        dest='dns_nameservers',
        help=_("DNS server for this subnet "
               "(repeat option to set multiple DNS servers)")
    )
    parser.add_argument(
        '--host-route',
        metavar='destination=<subnet>,gateway=<ip-address>',
        dest='host_routes',
        action=parseractions.MultiKeyValueAction,
        required_keys=['destination', 'gateway'],
        help=_("Additional route for this subnet "
               "e.g.: destination=10.10.0.0/16,gateway=192.168.71.254 "
               "destination: destination subnet (in CIDR notation) "
               "gateway: nexthop IP address "
               "(repeat option to add multiple routes)")
    )


def _get_columns(item):
    columns = list(item.keys())
    if 'tenant_id' in columns:
        columns.remove('tenant_id')
        columns.append('project_id')
    return tuple(sorted(columns))


def convert_entries_to_nexthop(entries):
    # Change 'gateway' entry to 'nexthop'
    changed_entries = copy.deepcopy(entries)
    for entry in changed_entries:
        if 'gateway' in entry:
            entry['nexthop'] = entry['gateway']
            del entry['gateway']

    return changed_entries


def convert_entries_to_gateway(entries):
    # Change 'nexthop' entry to 'gateway'
    changed_entries = copy.deepcopy(entries)
    for entry in changed_entries:
        if 'nexthop' in entry:
            entry['gateway'] = entry['nexthop']
            del entry['nexthop']

    return changed_entries


def _get_attrs(client_manager, parsed_args, is_create=True):
    attrs = {}
    if 'name' in parsed_args and parsed_args.name is not None:
        attrs['name'] = str(parsed_args.name)

    if is_create:
        if 'project' in parsed_args and parsed_args.project is not None:
            identity_client = client_manager.identity
            project_id = identity_common.find_project(
                identity_client,
                parsed_args.project,
                parsed_args.project_domain,
            ).id
            attrs['tenant_id'] = project_id
        client = client_manager.network
        attrs['network_id'] = client.find_network(parsed_args.network,
                                                  ignore_missing=False).id
        if parsed_args.subnet_pool is not None:
            subnet_pool = client.find_subnet_pool(parsed_args.subnet_pool,
                                                  ignore_missing=False)
            attrs['subnetpool_id'] = subnet_pool.id
        if parsed_args.use_default_subnet_pool:
            attrs['use_default_subnetpool'] = True
        if parsed_args.prefix_length is not None:
            attrs['prefixlen'] = parsed_args.prefix_length
        if parsed_args.subnet_range is not None:
            attrs['cidr'] = parsed_args.subnet_range
        if parsed_args.ip_version is not None:
            attrs['ip_version'] = parsed_args.ip_version
        if parsed_args.ipv6_ra_mode is not None:
            attrs['ipv6_ra_mode'] = parsed_args.ipv6_ra_mode
        if parsed_args.ipv6_address_mode is not None:
            attrs['ipv6_address_mode'] = parsed_args.ipv6_address_mode

    if 'gateway' in parsed_args and parsed_args.gateway is not None:
        gateway = parsed_args.gateway.lower()

        if not is_create and gateway == 'auto':
            msg = _("Auto option is not available for Subnet Set. "
                    "Valid options are <ip-address> or none")
            raise exceptions.CommandError(msg)
        elif gateway != 'auto':
            if gateway == 'none':
                attrs['gateway_ip'] = None
            else:
                attrs['gateway_ip'] = gateway
    if ('allocation_pools' in parsed_args and
       parsed_args.allocation_pools is not None):
        attrs['allocation_pools'] = parsed_args.allocation_pools
    if parsed_args.dhcp:
        attrs['enable_dhcp'] = True
    elif parsed_args.no_dhcp:
        attrs['enable_dhcp'] = False
    if ('dns_nameservers' in parsed_args and
       parsed_args.dns_nameservers is not None):
        attrs['dns_nameservers'] = parsed_args.dns_nameservers
    if 'host_routes' in parsed_args and parsed_args.host_routes is not None:
        # Change 'gateway' entry to 'nexthop' to match the API
        attrs['host_routes'] = convert_entries_to_nexthop(
            parsed_args.host_routes)
    return attrs


class CreateSubnet(command.ShowOne):
    """Create a subnet"""

    def get_parser(self, prog_name):
        parser = super(CreateSubnet, self).get_parser(prog_name)
        parser.add_argument(
            'name',
            help=_("New subnet name")
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_("Owner's project (name or ID)")
        )
        identity_common.add_project_domain_option_to_parser(parser)
        subnet_pool_group = parser.add_mutually_exclusive_group()
        subnet_pool_group.add_argument(
            '--subnet-pool',
            metavar='<subnet-pool>',
            help=_("Subnet pool from which this subnet will obtain a CIDR "
                   "(Name or ID)")
        )
        subnet_pool_group.add_argument(
            '--use-default-subnet-pool',
            action='store_true',
            help=_("Use default subnet pool for --ip-version")
        )
        parser.add_argument(
            '--prefix-length',
            metavar='<prefix-length>',
            help=_("Prefix length for subnet allocation from subnet pool")
        )
        parser.add_argument(
            '--subnet-range',
            metavar='<subnet-range>',
            help=_("Subnet range in CIDR notation "
                   "(required if --subnet-pool is not specified, "
                   "optional otherwise)")
        )
        dhcp_enable_group = parser.add_mutually_exclusive_group()
        dhcp_enable_group.add_argument(
            '--dhcp',
            action='store_true',
            default=True,
            help=_("Enable DHCP (default)")
        )
        dhcp_enable_group.add_argument(
            '--no-dhcp',
            action='store_true',
            help=_("Disable DHCP")
        )
        parser.add_argument(
            '--gateway',
            metavar='<gateway>',
            default='auto',
            help=_("Specify a gateway for the subnet.  The three options are: "
                   "<ip-address>: Specific IP address to use as the gateway, "
                   "'auto': Gateway address should automatically be chosen "
                   "from within the subnet itself, 'none': This subnet will "
                   "not use a gateway, e.g.: --gateway 192.168.9.1, "
                   "--gateway auto, --gateway none (default is 'auto')")
        )
        parser.add_argument(
            '--ip-version',
            type=int,
            default=4,
            choices=[4, 6],
            help=_("IP version (default is 4).  Note that when subnet pool is "
                   "specified, IP version is determined from the subnet pool "
                   "and this option is ignored")
        )
        parser.add_argument(
            '--ipv6-ra-mode',
            choices=['dhcpv6-stateful', 'dhcpv6-stateless', 'slaac'],
            help=_("IPv6 RA (Router Advertisement) mode, "
                   "valid modes: [dhcpv6-stateful, dhcpv6-stateless, slaac]")
        )
        parser.add_argument(
            '--ipv6-address-mode',
            choices=['dhcpv6-stateful', 'dhcpv6-stateless', 'slaac'],
            help=_("IPv6 address mode, "
                   "valid modes: [dhcpv6-stateful, dhcpv6-stateless, slaac]")
        )
        parser.add_argument(
            '--network',
            required=True,
            metavar='<network>',
            help=_("Network this subnet belongs to (name or ID)")
        )
        _get_common_parse_arguments(parser)
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        attrs = _get_attrs(self.app.client_manager, parsed_args)
        obj = client.create_subnet(**attrs)
        columns = _get_columns(obj)
        data = utils.get_item_properties(obj, columns, formatters=_formatters)
        return (columns, data)


class DeleteSubnet(command.Command):
    """Delete subnet"""

    def get_parser(self, prog_name):
        parser = super(DeleteSubnet, self).get_parser(prog_name)
        parser.add_argument(
            'subnet',
            metavar="<subnet>",
            help=_("Subnet to delete (name or ID)")
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        client.delete_subnet(
            client.find_subnet(parsed_args.subnet))


class ListSubnet(command.Lister):
    """List subnets"""

    def get_parser(self, prog_name):
        parser = super(ListSubnet, self).get_parser(prog_name)
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help=_("List additional fields in output")
        )
        parser.add_argument(
            '--ip-version',
            type=int,
            choices=[4, 6],
            metavar='<ip-version>',
            dest='ip_version',
            help=_("List only subnets of given IP version in output"
                   "Allowed values for IP version are 4 and 6."),
        )
        return parser

    def take_action(self, parsed_args):
        filters = {}
        if parsed_args.ip_version:
            filters['ip_version'] = parsed_args.ip_version
        data = self.app.client_manager.network.subnets(**filters)

        headers = ('ID', 'Name', 'Network', 'Subnet')
        columns = ('id', 'name', 'network_id', 'cidr')
        if parsed_args.long:
            headers += ('Project', 'DHCP', 'Name Servers',
                        'Allocation Pools', 'Host Routes', 'IP Version',
                        'Gateway')
            columns += ('tenant_id', 'enable_dhcp', 'dns_nameservers',
                        'allocation_pools', 'host_routes', 'ip_version',
                        'gateway_ip')

        return (headers,
                (utils.get_item_properties(
                    s, columns,
                    formatters=_formatters,
                ) for s in data))


class SetSubnet(command.Command):
    """Set subnet properties"""

    def get_parser(self, prog_name):
        parser = super(SetSubnet, self).get_parser(prog_name)
        parser.add_argument(
            'subnet',
            metavar="<subnet>",
            help=_("Subnet to modify (name or ID)")
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_("Updated name of the subnet")
        )
        dhcp_enable_group = parser.add_mutually_exclusive_group()
        dhcp_enable_group.add_argument(
            '--dhcp',
            action='store_true',
            default=None,
            help=_("Enable DHCP")
        )
        dhcp_enable_group.add_argument(
            '--no-dhcp',
            action='store_true',
            help=_("Disable DHCP")
        )
        parser.add_argument(
            '--gateway',
            metavar='<gateway>',
            help=_("Specify a gateway for the subnet. The options are: "
                   "<ip-address>: Specific IP address to use as the gateway, "
                   "'none': This subnet will not use a gateway, "
                   "e.g.: --gateway 192.168.9.1, --gateway none")
        )
        _get_common_parse_arguments(parser)
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        obj = client.find_subnet(parsed_args.subnet, ignore_missing=False)
        attrs = _get_attrs(self.app.client_manager, parsed_args,
                           is_create=False)
        if not attrs:
            msg = "Nothing specified to be set"
            raise exceptions.CommandError(msg)
        if 'dns_nameservers' in attrs:
            attrs['dns_nameservers'] += obj.dns_nameservers
        if 'host_routes' in attrs:
            attrs['host_routes'] += obj.host_routes
        if 'allocation_pools' in attrs:
            attrs['allocation_pools'] += obj.allocation_pools
        client.update_subnet(obj, **attrs)
        return


class ShowSubnet(command.ShowOne):
    """Display subnet details"""

    def get_parser(self, prog_name):
        parser = super(ShowSubnet, self).get_parser(prog_name)
        parser.add_argument(
            'subnet',
            metavar="<subnet>",
            help=_("Subnet to display (name or ID)")
        )
        return parser

    def take_action(self, parsed_args):
        obj = self.app.client_manager.network.find_subnet(parsed_args.subnet,
                                                          ignore_missing=False)
        columns = _get_columns(obj)
        data = utils.get_item_properties(obj, columns, formatters=_formatters)
        return (columns, data)
