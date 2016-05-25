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

"""Volume v2 snapshot action implementations"""

import copy

import six

from osc_lib.i18n import _

from openstackclient.common import command
from openstackclient.common import parseractions
from openstackclient.common import utils


class CreateSnapshot(command.ShowOne):
    """Create new snapshot"""

    def get_parser(self, prog_name):
        parser = super(CreateSnapshot, self).get_parser(prog_name)
        parser.add_argument(
            "volume",
            metavar="<volume>",
            help=_("Volume to snapshot (name or ID)")
        )
        parser.add_argument(
            "--name",
            metavar="<name>",
            help=("Name of the snapshot")
        )
        parser.add_argument(
            "--description",
            metavar="<description>",
            help=_("Description of the snapshot")
        )
        parser.add_argument(
            "--force",
            dest="force",
            action="store_true",
            default=False,
            help=_("Create a snapshot attached to an instance. "
                   "Default is False")
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        volume_id = utils.find_resource(
            volume_client.volumes, parsed_args.volume).id
        snapshot = volume_client.volume_snapshots.create(
            volume_id,
            force=parsed_args.force,
            name=parsed_args.name,
            description=parsed_args.description
        )
        snapshot._info.update(
            {'properties': utils.format_dict(snapshot._info.pop('metadata'))}
        )
        return zip(*sorted(six.iteritems(snapshot._info)))


class DeleteSnapshot(command.Command):
    """Delete volume snapshot(s)"""

    def get_parser(self, prog_name):
        parser = super(DeleteSnapshot, self).get_parser(prog_name)
        parser.add_argument(
            "snapshots",
            metavar="<snapshot>",
            nargs="+",
            help=_("Snapshot(s) to delete (name or ID)")
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        for snapshot in parsed_args.snapshots:
            snapshot_id = utils.find_resource(
                volume_client.volume_snapshots, snapshot).id
            volume_client.volume_snapshots.delete(snapshot_id)


class ListSnapshot(command.Lister):
    """List snapshots"""

    def get_parser(self, prog_name):
        parser = super(ListSnapshot, self).get_parser(prog_name)
        parser.add_argument(
            '--all-projects',
            action='store_true',
            default=False,
            help=_('Include all projects (admin only)'),
        )
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help=_('List additional fields in output'),
        )
        return parser

    def take_action(self, parsed_args):

        def _format_volume_id(volume_id):
            """Return a volume name if available

            :param volume_id: a volume ID
            :rtype: either the volume ID or name
            """

            volume = volume_id
            if volume_id in volume_cache.keys():
                volume = volume_cache[volume_id].name
            return volume

        if parsed_args.long:
            columns = ['ID', 'Name', 'Description', 'Status',
                       'Size', 'Created At', 'Volume ID', 'Metadata']
            column_headers = copy.deepcopy(columns)
            column_headers[6] = 'Volume'
            column_headers[7] = 'Properties'
        else:
            columns = ['ID', 'Name', 'Description', 'Status', 'Size']
            column_headers = copy.deepcopy(columns)

        # Cache the volume list
        volume_cache = {}
        try:
            for s in self.app.client_manager.volume.volumes.list():
                volume_cache[s.id] = s
        except Exception:
            # Just forget it if there's any trouble
            pass

        search_opts = {
            'all_tenants': parsed_args.all_projects,
        }

        data = self.app.client_manager.volume.volume_snapshots.list(
            search_opts=search_opts)
        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                    formatters={'Metadata': utils.format_dict,
                                'Volume ID': _format_volume_id},
                ) for s in data))


class SetSnapshot(command.Command):
    """Set snapshot properties"""

    def get_parser(self, prog_name):
        parser = super(SetSnapshot, self).get_parser(prog_name)
        parser.add_argument(
            'snapshot',
            metavar='<snapshot>',
            help=_('Snapshot to modify (name or ID)')
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('New snapshot name')
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('New snapshot description')
        )
        parser.add_argument(
            '--property',
            metavar='<key=value>',
            action=parseractions.KeyValueAction,
            help=_('Property to add/change for this snapshot '
                   '(repeat option to set multiple properties)'),
        )
        parser.add_argument(
            '--state',
            metavar='<state>',
            choices=['available', 'error', 'creating', 'deleting',
                     'error-deleting'],
            help=_('New snapshot state. Valid values are available, '
                   'error, creating, deleting, and error-deleting.'),
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        snapshot = utils.find_resource(volume_client.volume_snapshots,
                                       parsed_args.snapshot)

        kwargs = {}
        if parsed_args.name:
            kwargs['name'] = parsed_args.name
        if parsed_args.description:
            kwargs['description'] = parsed_args.description

        if (not kwargs and not parsed_args.property and not
                parsed_args.state):
            self.app.log.error(_("No changes requested\n"))
            return

        if parsed_args.property:
            volume_client.volume_snapshots.set_metadata(snapshot.id,
                                                        parsed_args.property)
        if parsed_args.state:
            volume_client.volume_snapshots.reset_state(snapshot.id,
                                                       parsed_args.state)
        volume_client.volume_snapshots.update(snapshot.id, **kwargs)


class ShowSnapshot(command.ShowOne):
    """Display snapshot details"""

    def get_parser(self, prog_name):
        parser = super(ShowSnapshot, self).get_parser(prog_name)
        parser.add_argument(
            "snapshot",
            metavar="<snapshot>",
            help=_("Snapshot to display (name or ID)")
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        snapshot = utils.find_resource(
            volume_client.volume_snapshots, parsed_args.snapshot)
        snapshot._info.update(
            {'properties': utils.format_dict(snapshot._info.pop('metadata'))}
        )
        return zip(*sorted(six.iteritems(snapshot._info)))


class UnsetSnapshot(command.Command):
    """Unset snapshot properties"""

    def get_parser(self, prog_name):
        parser = super(UnsetSnapshot, self).get_parser(prog_name)
        parser.add_argument(
            'snapshot',
            metavar='<snapshot>',
            help=_('Snapshot to modify (name or ID)'),
        )
        parser.add_argument(
            '--property',
            metavar='<key>',
            action='append',
            default=[],
            help=_('Property to remove from snapshot '
                   '(repeat option to remove multiple properties)'),
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        snapshot = utils.find_resource(
            volume_client.volume_snapshots, parsed_args.snapshot)

        if parsed_args.property:
            volume_client.volume_snapshots.delete_metadata(
                snapshot.id,
                parsed_args.property,
            )
        else:
            self.app.log.error(_("No changes requested\n"))
