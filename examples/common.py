#!/usr/bin/env python
# common.py - Common bits for API examples

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""
API Examples

This is a collection of common functions used by the example scripts.
It may also be run directly as a script to do basic testing of itself.

common.object_parser() provides the common set of command-line arguments
used in the library CLIs for setting up authentication.  This should make
playing with the example scripts against a running OpenStack simpler.

"""

import logging
import os
import sys
import traceback

CONSOLE_MESSAGE_FORMAT = '%(levelname)s: %(name)s %(message)s'
DEFAULT_VERBOSE_LEVEL = 1
USER_AGENT = 'sdk-examples'

PARSER_DESCRIPTION = 'A demonstration framework'

DEFAULT_IDENTITY_API_VERSION = '2.0'

_logger = logging.getLogger(__name__)

# --debug sets this True
dump_stack_trace = False


# Generally useful stuff often found in a utils module

def env(*vars, **kwargs):
    """Search for the first defined of possibly many env vars

    Returns the first environment variable defined in vars, or
    returns the default defined in kwargs.

    """
    for v in vars:
        value = os.environ.get(v, None)
        if value:
            return value
    return kwargs.get('default', '')


def import_class(import_str):
    """Returns a class from a string including module and class

    :param import_str: a string representation of the class name
    :rtype: the requested class
    """
    mod_str, _sep, class_str = import_str.rpartition('.')
    __import__(mod_str)
    return getattr(sys.modules[mod_str], class_str)


# Common Example functions

def base_parser(parser):
    """Set up some of the common CLI options

    These are the basic options that match the library CLIs so
    command-line/environment setups for those also work with these
    demonstration programs.

    """

    # Global arguments
#     parser.add_argument(
#         '--os-auth-url',
#         metavar='<auth-url>',
#         default=env('OS_AUTH_URL'),
#         help='Authentication URL (Env: OS_AUTH_URL)',
#     )
#     parser.add_argument(
#         '--os-project-name',
#         metavar='<auth-project-name>',
#         default=env('OS_PROJECT_NAME', default=env('OS_TENANT_NAME')),
#         help='Project name of the requested project-level'
#              'authorization scope (Env: OS_PROJECT_NAME)',
#     )
#     parser.add_argument(
#         '--os-username',
#         metavar='<auth-username>',
#         default=env('OS_USERNAME'),
#         help='Authentication username (Env: OS_USERNAME)',
#     )
#     parser.add_argument(
#         '--os-password',
#         metavar='<auth-password>',
#         default=env('OS_PASSWORD'),
#         help='Authentication password (Env: OS_PASSWORD)',
#     )
    parser.add_argument(
        '--os-cacert',
        metavar='<ca-bundle-file>',
        default=env('OS_CACERT'),
        help='CA certificate bundle file (Env: OS_CACERT)',
    )
    verify_group = parser.add_mutually_exclusive_group()
    verify_group.add_argument(
        '--verify',
        action='store_true',
        help='Verify server certificate (default)',
    )
    verify_group.add_argument(
        '--insecure',
        action='store_true',
        help='Disable server certificate verification',
    )
    parser.add_argument(
        '--os-identity-api-version',
        metavar='<identity-api-version>',
        default=env(
            'OS_IDENTITY_API_VERSION',
            default=DEFAULT_IDENTITY_API_VERSION),
        help='Force Identity API version (Env: OS_IDENTITY_API_VERSION)',
    )
#     parser.add_argument(
#         '--os-token',
#         metavar='<token>',
#         default=env('OS_TOKEN'),
#         help='Defaults to env[OS_TOKEN]',
#     )
    parser.add_argument(
        '--os-url',
        metavar='<url>',
        default=env('OS_URL'),
        help='Defaults to env[OS_URL]',
    )
    parser.add_argument(
        '-v', '--verbose',
        action='count',
        dest='verbose_level',
        default=1,
        help='Increase verbosity of output. Can be repeated.',
    )
    parser.add_argument(
        '--debug',
        default=False,
        action='store_true',
        help='show tracebacks on errors',
    )
    parser.add_argument(
        'rest',
        nargs='*',
        help='the rest of the args',
    )
    return parser


def configure_logging(opts):
    """Typical app logging setup

    Based on OSC/cliff

    """

    global dump_stack_trace

    root_logger = logging.getLogger('')

    # Requests logs some stuff at INFO that we don't want
    # unless we have DEBUG
    requests_log = logging.getLogger("requests")
    requests_log.setLevel(logging.ERROR)

    # Other modules we don't want DEBUG output for so
    # don't reset them below
    iso8601_log = logging.getLogger("iso8601")
    iso8601_log.setLevel(logging.ERROR)

    # Always send higher-level messages to the console via stderr
    console = logging.StreamHandler(sys.stderr)
    formatter = logging.Formatter(CONSOLE_MESSAGE_FORMAT)
    console.setFormatter(formatter)
    root_logger.addHandler(console)

    # Set logging to the requested level
    dump_stack_trace = False
    if opts.verbose_level == 0:
        # --quiet
        root_logger.setLevel(logging.ERROR)
    elif opts.verbose_level == 1:
        # This is the default case, no --debug, --verbose or --quiet
        root_logger.setLevel(logging.WARNING)
    elif opts.verbose_level == 2:
        # One --verbose
        root_logger.setLevel(logging.INFO)
    elif opts.verbose_level >= 3:
        # Two or more --verbose
        root_logger.setLevel(logging.DEBUG)
        requests_log.setLevel(logging.DEBUG)

    if opts.debug:
        # --debug forces traceback
        dump_stack_trace = True
        root_logger.setLevel(logging.DEBUG)
        requests_log.setLevel(logging.DEBUG)

    return


# Top-level functions

def run(opts):
    """Default run command"""

    # Do some basic testing here
    sys.stdout.write("Default run command\n")
    sys.stdout.write("Verbose level: %s\n" % opts.verbose_level)
    sys.stdout.write("Debug: %s\n" % opts.debug)
    sys.stdout.write("dump_stack_trace: %s\n" % dump_stack_trace)


def setup():
    """Parse command line and configure logging"""
    opts = base_parser().parse_args()
    configure_logging(opts)
    return opts


def main(opts, run):
    try:
        return run(opts)
    except Exception as e:
        if dump_stack_trace:
            _logger.error(traceback.format_exc(e))
        else:
            _logger.error('Exception raised: ' + str(e))
        return 1


if __name__ == "__main__":
    opts = setup()
    sys.exit(main(opts, run))
