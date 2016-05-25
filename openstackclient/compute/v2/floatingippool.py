#   Copyright 2013 OpenStack Foundation
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

"""Floating IP Pool action implementations"""

from osc_lib.command import command
from osc_lib import utils


class ListFloatingIPPool(command.Lister):
    """List pools of floating IP addresses"""

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute

        columns = ('Name',)

        data = compute_client.floating_ip_pools.list()

        return (columns,
                (utils.get_item_properties(
                    s, columns,
                    formatters={},
                ) for s in data))
