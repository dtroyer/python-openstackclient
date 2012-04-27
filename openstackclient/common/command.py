# Copyright 2011 OpenStack LLC.
# All Rights Reserved
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
OpenStack base command
"""

from cliff.command import Command


class OpenStackCommand(Command):
    """Base class for OpenStack commands
    """

    # Boolean indicating whether this command needs the user to
    # provide authentication information before it can be run. The
    # value is used by OpenStackShell.get_token_and_endpoint() to
    # decide if the user needs to provide those options before the
    # command is attempted. Most commands need auth, but we need
    # a way to let the `help` command run without it.
    REQUIRES_AUTH = True

    api = None

    def run(self, parsed_args):
        if not self.api:
            return
        else:
            return super(OpenStackCommand, self).run(parsed_args)
