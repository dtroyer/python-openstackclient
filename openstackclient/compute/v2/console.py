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

"""Compute v2 Console action implementations"""

import six
import sys

from osc_lib.cli import parseractions
from osc_lib.command import command
from osc_lib.i18n import _
from osc_lib import utils


class ShowConsoleLog(command.Command):
    """Show server's console output"""

    def get_parser(self, prog_name):
        parser = super(ShowConsoleLog, self).get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help=_("Server to show console log (name or ID)")
        )
        parser.add_argument(
            '--lines',
            metavar='<num-lines>',
            type=int,
            default=None,
            action=parseractions.NonNegativeAction,
            help=_("Number of lines to display from the end of the log "
                   "(default=all)")
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute

        server = utils.find_resource(
            compute_client.servers,
            parsed_args.server,
        )
        length = parsed_args.lines
        if length:
            # NOTE(dtroyer): get_console_output() appears to shortchange the
            #                output by one line
            length += 1

        data = server.get_console_output(length=length)
        sys.stdout.write(data)


class ShowConsoleURL(command.ShowOne):
    """Show server's remote console URL"""

    def get_parser(self, prog_name):
        parser = super(ShowConsoleURL, self).get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help=_("Server to show URL (name or ID)")
        )
        type_group = parser.add_mutually_exclusive_group()
        type_group.add_argument(
            '--novnc',
            dest='url_type',
            action='store_const',
            const='novnc',
            default='novnc',
            help=_("Show noVNC console URL (default)")
        )
        type_group.add_argument(
            '--xvpvnc',
            dest='url_type',
            action='store_const',
            const='xvpvnc',
            help=_("Show xpvnc console URL")
        )
        type_group.add_argument(
            '--spice',
            dest='url_type',
            action='store_const',
            const='spice',
            help=_("Show SPICE console URL")
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        server = utils.find_resource(
            compute_client.servers,
            parsed_args.server,
        )

        if parsed_args.url_type in ['novnc', 'xvpvnc']:
            data = server.get_vnc_console(parsed_args.url_type)
        if parsed_args.url_type in ['spice']:
            data = server.get_spice_console(parsed_args.url_type)

        if not data:
            return ({}, {})

        info = {}
        info.update(data['console'])
        return zip(*sorted(six.iteritems(info)))
