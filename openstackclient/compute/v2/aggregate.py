#   Copyright 2012 OpenStack Foundation
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

"""Compute v2 Aggregate action implementations"""

import six

from osc_lib.cli import parseractions
from osc_lib.i18n import _

from openstackclient.common import command
from openstackclient.common import utils


class AddAggregateHost(command.ShowOne):
    """Add host to aggregate"""

    def get_parser(self, prog_name):
        parser = super(AddAggregateHost, self).get_parser(prog_name)
        parser.add_argument(
            'aggregate',
            metavar='<aggregate>',
            help=_("Aggregate (name or ID)")
        )
        parser.add_argument(
            'host',
            metavar='<host>',
            help=_("Host to add to <aggregate>")
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute

        aggregate = utils.find_resource(
            compute_client.aggregates,
            parsed_args.aggregate,
        )
        data = compute_client.aggregates.add_host(aggregate, parsed_args.host)

        info = {}
        info.update(data._info)
        return zip(*sorted(six.iteritems(info)))


class CreateAggregate(command.ShowOne):
    """Create a new aggregate"""

    def get_parser(self, prog_name):
        parser = super(CreateAggregate, self).get_parser(prog_name)
        parser.add_argument(
            "name",
            metavar="<name>",
            help=_("New aggregate name")
        )
        parser.add_argument(
            "--zone",
            metavar="<availability-zone>",
            help=_("Availability zone name")
        )
        parser.add_argument(
            "--property",
            metavar="<key=value>",
            action=parseractions.KeyValueAction,
            help=_("Property to add to this aggregate "
                   "(repeat option to set multiple properties)")
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute

        info = {}
        data = compute_client.aggregates.create(
            parsed_args.name,
            parsed_args.zone,
        )
        info.update(data._info)

        if parsed_args.property:
            info.update(compute_client.aggregates.set_metadata(
                data,
                parsed_args.property,
            )._info)

        return zip(*sorted(six.iteritems(info)))


class DeleteAggregate(command.Command):
    """Delete an existing aggregate"""

    def get_parser(self, prog_name):
        parser = super(DeleteAggregate, self).get_parser(prog_name)
        parser.add_argument(
            'aggregate',
            metavar='<aggregate>',
            help=_("Aggregate to delete (name or ID)")
        )
        return parser

    def take_action(self, parsed_args):

        compute_client = self.app.client_manager.compute
        data = utils.find_resource(
            compute_client.aggregates,
            parsed_args.aggregate,
        )
        compute_client.aggregates.delete(data.id)


class ListAggregate(command.Lister):
    """List all aggregates"""

    def get_parser(self, prog_name):
        parser = super(ListAggregate, self).get_parser(prog_name)
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help=_("List additional fields in output")
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute

        data = compute_client.aggregates.list()

        if parsed_args.long:
            # Remove availability_zone from metadata because Nova doesn't
            for d in data:
                if 'availability_zone' in d.metadata:
                    d.metadata.pop('availability_zone')
            # This is the easiest way to change column headers
            column_headers = (
                "ID",
                "Name",
                "Availability Zone",
                "Properties",
            )
            columns = (
                "ID",
                "Name",
                "Availability Zone",
                "Metadata",
            )
        else:
            column_headers = columns = (
                "ID",
                "Name",
                "Availability Zone",
            )

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))


class RemoveAggregateHost(command.ShowOne):
    """Remove host from aggregate"""

    def get_parser(self, prog_name):
        parser = super(RemoveAggregateHost, self).get_parser(prog_name)
        parser.add_argument(
            'aggregate',
            metavar='<aggregate>',
            help=_("Aggregate (name or ID)")
        )
        parser.add_argument(
            'host',
            metavar='<host>',
            help=_("Host to remove from <aggregate>")
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute

        aggregate = utils.find_resource(
            compute_client.aggregates,
            parsed_args.aggregate,
        )
        data = compute_client.aggregates.remove_host(
            aggregate,
            parsed_args.host,
        )

        info = {}
        info.update(data._info)
        return zip(*sorted(six.iteritems(info)))


class SetAggregate(command.Command):
    """Set aggregate properties"""

    def get_parser(self, prog_name):
        parser = super(SetAggregate, self).get_parser(prog_name)
        parser.add_argument(
            'aggregate',
            metavar='<aggregate>',
            help=_("Aggregate to modify (name or ID)")
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_("Set aggregate name")
        )
        parser.add_argument(
            "--zone",
            metavar="<availability-zone>",
            help=_("Set availability zone name")
        )
        parser.add_argument(
            "--property",
            metavar="<key=value>",
            action=parseractions.KeyValueAction,
            help=_("Property to set on <aggregate> "
                   "(repeat option to set multiple properties)")
        )
        return parser

    def take_action(self, parsed_args):

        compute_client = self.app.client_manager.compute
        aggregate = utils.find_resource(
            compute_client.aggregates,
            parsed_args.aggregate,
        )

        kwargs = {}
        if parsed_args.name:
            kwargs['name'] = parsed_args.name
        if parsed_args.zone:
            kwargs['availability_zone'] = parsed_args.zone
        if kwargs:
            compute_client.aggregates.update(
                aggregate,
                kwargs
            )

        if parsed_args.property:
            compute_client.aggregates.set_metadata(
                aggregate,
                parsed_args.property
            )


class ShowAggregate(command.ShowOne):
    """Display aggregate details"""

    def get_parser(self, prog_name):
        parser = super(ShowAggregate, self).get_parser(prog_name)
        parser.add_argument(
            'aggregate',
            metavar='<aggregate>',
            help=_("Aggregate to display (name or ID)")
        )
        return parser

    def take_action(self, parsed_args):

        compute_client = self.app.client_manager.compute
        data = utils.find_resource(
            compute_client.aggregates,
            parsed_args.aggregate,
        )
        # Remove availability_zone from metadata because Nova doesn't
        if 'availability_zone' in data.metadata:
            data.metadata.pop('availability_zone')

        # Special mapping for columns to make the output easier to read:
        # 'metadata' --> 'properties'
        data._info.update(
            {
                'properties': utils.format_dict(data._info.pop('metadata')),
            },
        )

        info = {}
        info.update(data._info)
        return zip(*sorted(six.iteritems(info)))


class UnsetAggregate(command.Command):
    """Unset aggregate properties"""

    def get_parser(self, prog_name):
        parser = super(UnsetAggregate, self).get_parser(prog_name)
        parser.add_argument(
            "aggregate",
            metavar="<aggregate>",
            help=_("Aggregate to modify (name or ID)")
        )
        parser.add_argument(
            "--property",
            metavar="<key>",
            action='append',
            required=True,
            help=_("Property to remove from aggregate "
                   "(repeat option to remove multiple properties)")
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        aggregate = utils.find_resource(
            compute_client.aggregates,
            parsed_args.aggregate)

        unset_property = {key: None for key in parsed_args.property}
        compute_client.aggregates.set_metadata(aggregate,
                                               unset_property)
