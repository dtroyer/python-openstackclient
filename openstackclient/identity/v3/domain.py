#   Copyright 2012-2013 OpenStack Foundation
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

"""Identity v3 Domain action implementations"""

import six
import sys

from keystoneauth1 import exceptions as ks_exc
from osc_lib.i18n import _
from osc_lib import utils

from openstackclient.common import command


class CreateDomain(command.ShowOne):
    """Create new domain"""

    def get_parser(self, prog_name):
        parser = super(CreateDomain, self).get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='<domain-name>',
            help='New domain name',
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help='New domain description',
        )
        enable_group = parser.add_mutually_exclusive_group()
        enable_group.add_argument(
            '--enable',
            action='store_true',
            help='Enable domain (default)',
        )
        enable_group.add_argument(
            '--disable',
            action='store_true',
            help='Disable domain',
        )
        parser.add_argument(
            '--or-show',
            action='store_true',
            help=_('Return existing domain'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        enabled = True
        if parsed_args.disable:
            enabled = False

        try:
            domain = identity_client.domains.create(
                name=parsed_args.name,
                description=parsed_args.description,
                enabled=enabled,
            )
        except ks_exc.Conflict as e:
            if parsed_args.or_show:
                domain = utils.find_resource(identity_client.domains,
                                             parsed_args.name)
                self.log.info('Returning existing domain %s', domain.name)
            else:
                raise e

        domain._info.pop('links')
        return zip(*sorted(six.iteritems(domain._info)))


class DeleteDomain(command.Command):
    """Delete domain"""

    def get_parser(self, prog_name):
        parser = super(DeleteDomain, self).get_parser(prog_name)
        parser.add_argument(
            'domain',
            metavar='<domain>',
            help='Domain to delete (name or ID)',
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        domain = utils.find_resource(identity_client.domains,
                                     parsed_args.domain)
        identity_client.domains.delete(domain.id)


class ListDomain(command.Lister):
    """List domains"""

    def take_action(self, parsed_args):
        columns = ('ID', 'Name', 'Enabled', 'Description')
        data = self.app.client_manager.identity.domains.list()
        return (columns,
                (utils.get_item_properties(
                    s, columns,
                    formatters={},
                ) for s in data))


class SetDomain(command.Command):
    """Set domain properties"""

    def get_parser(self, prog_name):
        parser = super(SetDomain, self).get_parser(prog_name)
        parser.add_argument(
            'domain',
            metavar='<domain>',
            help='Domain to modify (name or ID)',
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            help='New domain name',
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help='New domain description',
        )
        enable_group = parser.add_mutually_exclusive_group()
        enable_group.add_argument(
            '--enable',
            action='store_true',
            help='Enable domain',
        )
        enable_group.add_argument(
            '--disable',
            action='store_true',
            help='Disable domain',
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        domain = utils.find_resource(identity_client.domains,
                                     parsed_args.domain)
        kwargs = {}
        if parsed_args.name:
            kwargs['name'] = parsed_args.name
        if parsed_args.description:
            kwargs['description'] = parsed_args.description

        if parsed_args.enable:
            kwargs['enabled'] = True
        if parsed_args.disable:
            kwargs['enabled'] = False

        if not kwargs:
            sys.stdout.write("Domain not updated, no arguments present")
            return
        identity_client.domains.update(domain.id, **kwargs)


class ShowDomain(command.ShowOne):
    """Display domain details"""

    def get_parser(self, prog_name):
        parser = super(ShowDomain, self).get_parser(prog_name)
        parser.add_argument(
            'domain',
            metavar='<domain>',
            help='Domain to display (name or ID)',
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        domain = utils.find_resource(identity_client.domains,
                                     parsed_args.domain)

        domain._info.pop('links')
        return zip(*sorted(six.iteritems(domain._info)))
