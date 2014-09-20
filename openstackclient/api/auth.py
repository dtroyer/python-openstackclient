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

"""Authentication Library"""

import argparse
import logging

import common
from keystoneclient.auth import base
from keystoneclient import session as ksc_session
import stevedore


LOG = logging.getLogger('')

# Initialize the list of Authentication plugins early in order
# to get the command-line options
PLUGIN_LIST = stevedore.ExtensionManager(
    base.PLUGIN_NAMESPACE,
    invoke_on_load=False,
    propagate_map_exceptions=True,
)
# TODO(dtroyer): add some method to list the plugins for the
#                --os_auth_plugin option

# Get the command line options so the help action has them available
OPTIONS_LIST = {}
for plugin in PLUGIN_LIST:
    for o in plugin.plugin.get_options():
        os_name = o.dest.lower().replace('_', '-')
        os_env_name = 'OS_' + os_name.upper().replace('-', '_')
        OPTIONS_LIST.setdefault(
            os_name,
            {'env': os_env_name,
             'help': ''}
        )
        # TODO(mhu) simplistic approach, would be better to only add
        # help texts if they vary from one auth plugin to another
        # also the text rendering is ugly in the CLI ...
        OPTIONS_LIST[os_name]['help'] += 'With %s: %s\n' % (
            plugin.name,
            o.help,
        )


def build_auth_params(cmd_options, plugin_options):
    auth_params = {}
    for option in plugin_options:
        option_name = 'os_' + option.dest
        LOG.debug('fetching option %s' % option_name)
        auth_params[option.dest] = getattr(cmd_options, option_name, None)
    # grab tenant from project for v2.0 API compatibility
    if cmd_options.os_auth_plugin.startswith("v2"):
        auth_params['tenant_id'] = getattr(
            cmd_options,
            'os_project_id',
            None,
        )
        auth_params['tenant_name'] = getattr(
            cmd_options,
            'os_project_name',
            None,
        )
    return auth_params


def build_auth_plugins_option_parser(parser):
    """Auth plugins options builder

    Builds dynamically the list of options expected by each available
    authentication plugin.

    """
    available_plugins = [plugin.name for plugin in PLUGIN_LIST]
    parser.add_argument(
        '--os-auth-plugin',
        metavar='<OS_AUTH_PLUGIN>',
        default=common.env('OS_AUTH_PLUGIN', default=None),
        help='The authentication method to use. Default is v2password. '
             'The --os-identity-api-version argument must be consistent '
             'with the version of the method.\nAvailable methods are ' +
             ', '.join(available_plugins),
        choices=available_plugins
    )
    # make sur we catch old v2.0 env values
    envs = {
        'OS_PROJECT_NAME': common.env(
            'OS_PROJECT_NAME',
            default=common.env('OS_TENANT_NAME')
        ),
        'OS_PROJECT_ID': common.env(
            'OS_PROJECT_ID',
            default=common.env('OS_TENANT_ID')
        ),
    }
    for o in OPTIONS_LIST:
        # remove allusion to tenants from v2.0 API
        if 'tenant' not in o:
            parser.add_argument(
                '--os-' + o,
                metavar='<auth-%s>' % o,
                default=envs.get(OPTIONS_LIST[o]['env'],
                                 common.env(OPTIONS_LIST[o]['env'])),
                help='%s\n(Env: %s)' % (OPTIONS_LIST[o]['help'],
                                        OPTIONS_LIST[o]['env']),
            )
    # add tenant-related options for compatibility
    # this is deprecated...
    parser.add_argument(
        '--os-tenant-name',
        metavar='<auth-tenant-name>',
        dest='os_project_name',
        default=common.env('OS_TENANT_NAME'),
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        '--os-tenant-id',
        metavar='<auth-tenant-id>',
        dest='os_project_id',
        default=common.env('OS_TENANT_ID'),
        help=argparse.SUPPRESS,
    )
    return parser


def make_session(opts, **kwargs):
    """Create our base session using simple auth from ksc plugins

    The arguments required in opts varies depending on the auth plugin
    that is used.  This example assumes Identity v2 will be used
    and selects token auth if both os_url and os_token have been
    provided, otherwise it uses password.

    :param Namespace opts:
        A parser options Namespace containing the authentication
        options to be used
    :param dict kwargs:
        Additional options passed directly to Session constructor
    """

    # TODO(dtroyer): work out the versioning and how to do discovery
    #                pin to v2 auth for now
    ver_prefix = 'v2'

    # sort out auth_plugin here
    if opts.os_auth_plugin is None:
        if opts.os_url and opts.os_token:
            LOG.debug('Using token auth %s', ver_prefix)
            opts.os_auth_plugin = ver_prefix + 'token'
        else:
            LOG.debug('Using password auth %s', ver_prefix)
            opts.os_auth_plugin = ver_prefix + 'password'

    auth_plugin = base.get_plugin_class(opts.os_auth_plugin)
    auth_params = build_auth_params(opts, auth_plugin.get_options())
    auth = auth_plugin.load_from_options(**auth_params)

    session = ksc_session.Session(
        auth=auth,
        **kwargs
    )

    return session
