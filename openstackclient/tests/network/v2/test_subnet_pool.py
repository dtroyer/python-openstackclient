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

import argparse
import copy
import mock

from osc_lib import exceptions

from openstackclient.common import utils
from openstackclient.network.v2 import subnet_pool
from openstackclient.tests import fakes
from openstackclient.tests.identity.v3 import fakes as identity_fakes_v3
from openstackclient.tests.network.v2 import fakes as network_fakes
from openstackclient.tests import utils as tests_utils


class TestSubnetPool(network_fakes.TestNetworkV2):

    def setUp(self):
        super(TestSubnetPool, self).setUp()

        # Get a shortcut to the network client
        self.network = self.app.client_manager.network


class TestCreateSubnetPool(TestSubnetPool):

    # The new subnet pool to create.
    _subnet_pool = network_fakes.FakeSubnetPool.create_one_subnet_pool()

    _address_scope = network_fakes.FakeAddressScope.create_one_address_scope()

    columns = (
        'address_scope_id',
        'default_prefixlen',
        'default_quota',
        'id',
        'ip_version',
        'is_default',
        'max_prefixlen',
        'min_prefixlen',
        'name',
        'prefixes',
        'project_id',
        'shared',
    )
    data = (
        _subnet_pool.address_scope_id,
        _subnet_pool.default_prefixlen,
        _subnet_pool.default_quota,
        _subnet_pool.id,
        _subnet_pool.ip_version,
        _subnet_pool.is_default,
        _subnet_pool.max_prefixlen,
        _subnet_pool.min_prefixlen,
        _subnet_pool.name,
        utils.format_list(_subnet_pool.prefixes),
        _subnet_pool.project_id,
        _subnet_pool.shared,
    )

    def setUp(self):
        super(TestCreateSubnetPool, self).setUp()

        self.network.create_subnet_pool = mock.Mock(
            return_value=self._subnet_pool)

        # Get the command object to test
        self.cmd = subnet_pool.CreateSubnetPool(self.app, self.namespace)

        self.network.find_address_scope = mock.Mock(
            return_value=self._address_scope)

        # Set identity client. And get a shortcut to Identity client.
        identity_client = identity_fakes_v3.FakeIdentityv3Client(
            endpoint=fakes.AUTH_URL,
            token=fakes.AUTH_TOKEN,
        )
        self.app.client_manager.identity = identity_client
        self.identity = self.app.client_manager.identity

        # Get a shortcut to the ProjectManager Mock
        self.projects_mock = self.identity.projects
        self.projects_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes_v3.PROJECT),
            loaded=True,
        )

        # Get a shortcut to the DomainManager Mock
        self.domains_mock = self.identity.domains
        self.domains_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes_v3.DOMAIN),
            loaded=True,
        )

    def test_create_no_options(self):
        arglist = []
        verifylist = []

        self.assertRaises(tests_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_create_no_pool_prefix(self):
        """Make sure --pool-prefix is a required argument"""
        arglist = [
            self._subnet_pool.name,
        ]
        verifylist = [
            ('name', self._subnet_pool.name),
        ]
        self.assertRaises(tests_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_create_default_options(self):
        arglist = [
            '--pool-prefix', '10.0.10.0/24',
            self._subnet_pool.name,
        ]
        verifylist = [
            ('prefixes', ['10.0.10.0/24']),
            ('name', self._subnet_pool.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = (self.cmd.take_action(parsed_args))

        self.network.create_subnet_pool.assert_called_once_with(**{
            'prefixes': ['10.0.10.0/24'],
            'name': self._subnet_pool.name,
        })
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_create_prefixlen_options(self):
        arglist = [
            '--default-prefix-length', self._subnet_pool.default_prefixlen,
            '--max-prefix-length', self._subnet_pool.max_prefixlen,
            '--min-prefix-length', self._subnet_pool.min_prefixlen,
            '--pool-prefix', '10.0.10.0/24',
            self._subnet_pool.name,
        ]
        verifylist = [
            ('default_prefix_length',
                int(self._subnet_pool.default_prefixlen)),
            ('max_prefix_length', int(self._subnet_pool.max_prefixlen)),
            ('min_prefix_length', int(self._subnet_pool.min_prefixlen)),
            ('name', self._subnet_pool.name),
            ('prefixes', ['10.0.10.0/24']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = (self.cmd.take_action(parsed_args))

        self.network.create_subnet_pool.assert_called_once_with(**{
            'default_prefixlen': int(self._subnet_pool.default_prefixlen),
            'max_prefixlen': int(self._subnet_pool.max_prefixlen),
            'min_prefixlen': int(self._subnet_pool.min_prefixlen),
            'prefixes': ['10.0.10.0/24'],
            'name': self._subnet_pool.name,
        })
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_create_len_negative(self):
        arglist = [
            self._subnet_pool.name,
            '--min-prefix-length', '-16',
        ]
        verifylist = [
            ('subnet_pool', self._subnet_pool.name),
            ('min_prefix_length', '-16'),
        ]

        self.assertRaises(argparse.ArgumentTypeError, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_create_project_domain(self):
        arglist = [
            '--pool-prefix', '10.0.10.0/24',
            "--project", identity_fakes_v3.project_name,
            "--project-domain", identity_fakes_v3.domain_name,
            self._subnet_pool.name,
        ]
        verifylist = [
            ('prefixes', ['10.0.10.0/24']),
            ('project', identity_fakes_v3.project_name),
            ('project_domain', identity_fakes_v3.domain_name),
            ('name', self._subnet_pool.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = (self.cmd.take_action(parsed_args))

        self.network.create_subnet_pool.assert_called_once_with(**{
            'prefixes': ['10.0.10.0/24'],
            'tenant_id': identity_fakes_v3.project_id,
            'name': self._subnet_pool.name,
        })
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_create_address_scope_option(self):
        arglist = [
            '--pool-prefix', '10.0.10.0/24',
            '--address-scope', self._address_scope.id,
            self._subnet_pool.name,
        ]
        verifylist = [
            ('prefixes', ['10.0.10.0/24']),
            ('address_scope', self._address_scope.id),
            ('name', self._subnet_pool.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = (self.cmd.take_action(parsed_args))

        self.network.create_subnet_pool.assert_called_once_with(**{
            'prefixes': ['10.0.10.0/24'],
            'address_scope_id': self._address_scope.id,
            'name': self._subnet_pool.name,
        })
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_create_default_and_shared_options(self):
        arglist = [
            '--pool-prefix', '10.0.10.0/24',
            '--default',
            '--share',
            self._subnet_pool.name,
        ]
        verifylist = [
            ('prefixes', ['10.0.10.0/24']),
            ('default', True),
            ('share', True),
            ('name', self._subnet_pool.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = (self.cmd.take_action(parsed_args))

        self.network.create_subnet_pool.assert_called_once_with(**{
            'is_default': True,
            'name': self._subnet_pool.name,
            'prefixes': ['10.0.10.0/24'],
            'shared': True,
        })
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)


class TestDeleteSubnetPool(TestSubnetPool):

    # The subnet pool to delete.
    _subnet_pool = network_fakes.FakeSubnetPool.create_one_subnet_pool()

    def setUp(self):
        super(TestDeleteSubnetPool, self).setUp()

        self.network.delete_subnet_pool = mock.Mock(return_value=None)

        self.network.find_subnet_pool = mock.Mock(
            return_value=self._subnet_pool
        )

        # Get the command object to test
        self.cmd = subnet_pool.DeleteSubnetPool(self.app, self.namespace)

    def test_delete(self):
        arglist = [
            self._subnet_pool.name,
        ]
        verifylist = [
            ('subnet_pool', self._subnet_pool.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.network.delete_subnet_pool.assert_called_once_with(
            self._subnet_pool)
        self.assertIsNone(result)


class TestListSubnetPool(TestSubnetPool):
    # The subnet pools going to be listed up.
    _subnet_pools = network_fakes.FakeSubnetPool.create_subnet_pools(count=3)

    columns = (
        'ID',
        'Name',
        'Prefixes',
    )
    columns_long = columns + (
        'Default Prefix Length',
        'Address Scope',
        'Default Subnet Pool',
        'Shared',
    )

    data = []
    for pool in _subnet_pools:
        data.append((
            pool.id,
            pool.name,
            utils.format_list(pool.prefixes),
        ))

    data_long = []
    for pool in _subnet_pools:
        data_long.append((
            pool.id,
            pool.name,
            utils.format_list(pool.prefixes),
            pool.default_prefixlen,
            pool.address_scope_id,
            pool.is_default,
            pool.shared,
        ))

    def setUp(self):
        super(TestListSubnetPool, self).setUp()

        # Get the command object to test
        self.cmd = subnet_pool.ListSubnetPool(self.app, self.namespace)

        self.network.subnet_pools = mock.Mock(return_value=self._subnet_pools)

    def test_subnet_pool_list_no_option(self):
        arglist = []
        verifylist = [
            ('long', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network.subnet_pools.assert_called_once_with()
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_subnet_pool_list_long(self):
        arglist = [
            '--long',
        ]
        verifylist = [
            ('long', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network.subnet_pools.assert_called_once_with()
        self.assertEqual(self.columns_long, columns)
        self.assertEqual(self.data_long, list(data))


class TestSetSubnetPool(TestSubnetPool):

    # The subnet_pool to set.
    _subnet_pool = network_fakes.FakeSubnetPool.create_one_subnet_pool()

    _address_scope = network_fakes.FakeAddressScope.create_one_address_scope()

    def setUp(self):
        super(TestSetSubnetPool, self).setUp()

        self.network.update_subnet_pool = mock.Mock(return_value=None)

        self.network.find_subnet_pool = mock.Mock(
            return_value=self._subnet_pool)

        self.network.find_address_scope = mock.Mock(
            return_value=self._address_scope)

        # Get the command object to test
        self.cmd = subnet_pool.SetSubnetPool(self.app, self.namespace)

    def test_set_this(self):
        arglist = [
            '--name', 'noob',
            '--default-prefix-length', '8',
            '--min-prefix-length', '8',
            self._subnet_pool.name,
        ]
        verifylist = [
            ('name', 'noob'),
            ('default_prefix_length', 8),
            ('min_prefix_length', 8),
            ('subnet_pool', self._subnet_pool.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        attrs = {
            'name': 'noob',
            'default_prefixlen': 8,
            'min_prefixlen': 8,
        }
        self.network.update_subnet_pool.assert_called_once_with(
            self._subnet_pool, **attrs)
        self.assertIsNone(result)

    def test_set_that(self):
        arglist = [
            '--pool-prefix', '10.0.1.0/24',
            '--pool-prefix', '10.0.2.0/24',
            '--max-prefix-length', '16',
            self._subnet_pool.name,
        ]
        verifylist = [
            ('prefixes', ['10.0.1.0/24', '10.0.2.0/24']),
            ('max_prefix_length', 16),
            ('subnet_pool', self._subnet_pool.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        prefixes = ['10.0.1.0/24', '10.0.2.0/24']
        prefixes.extend(self._subnet_pool.prefixes)
        attrs = {
            'prefixes': prefixes,
            'max_prefixlen': 16,
        }
        self.network.update_subnet_pool.assert_called_once_with(
            self._subnet_pool, **attrs)
        self.assertIsNone(result)

    def test_set_nothing(self):
        arglist = [self._subnet_pool.name, ]
        verifylist = [('subnet_pool', self._subnet_pool.name), ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(exceptions.CommandError, self.cmd.take_action,
                          parsed_args)

    def test_set_len_negative(self):
        arglist = [
            '--max-prefix-length', '-16',
            self._subnet_pool.name,
        ]
        verifylist = [
            ('max_prefix_length', '-16'),
            ('subnet_pool', self._subnet_pool.name),
        ]

        self.assertRaises(argparse.ArgumentTypeError, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_set_address_scope(self):
        arglist = [
            '--address-scope', self._address_scope.id,
            self._subnet_pool.name,
        ]
        verifylist = [
            ('address_scope', self._address_scope.id),
            ('subnet_pool', self._subnet_pool.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        attrs = {
            'address_scope_id': self._address_scope.id,
        }
        self.network.update_subnet_pool.assert_called_once_with(
            self._subnet_pool, **attrs)
        self.assertIsNone(result)

    def test_set_no_address_scope(self):
        arglist = [
            '--no-address-scope',
            self._subnet_pool.name,
        ]
        verifylist = [
            ('no_address_scope', True),
            ('subnet_pool', self._subnet_pool.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        attrs = {
            'address_scope_id': None,
        }
        self.network.update_subnet_pool.assert_called_once_with(
            self._subnet_pool, **attrs)
        self.assertIsNone(result)

    def test_set_no_address_scope_conflict(self):
        arglist = [
            '--address-scope', self._address_scope.id,
            '--no-address-scope',
            self._subnet_pool.name,
        ]
        verifylist = [
            ('address_scope', self._address_scope.id),
            ('no_address_scope', True),
            ('subnet_pool', self._subnet_pool.name),
        ]

        # Exclusive arguments will conflict here.
        self.assertRaises(tests_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_set_default(self):
        arglist = [
            '--default',
            self._subnet_pool.name,
        ]
        verifylist = [
            ('default', True),
            ('subnet_pool', self._subnet_pool.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        attrs = {
            'is_default': True
        }
        self.network.update_subnet_pool.assert_called_once_with(
            self._subnet_pool, **attrs)
        self.assertIsNone(result)

    def test_set_no_default(self):
        arglist = [
            '--no-default',
            self._subnet_pool.name,
        ]
        verifylist = [
            ('no_default', True),
            ('subnet_pool', self._subnet_pool.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        attrs = {
            'is_default': False,
        }
        self.network.update_subnet_pool.assert_called_once_with(
            self._subnet_pool, **attrs)
        self.assertIsNone(result)

    def test_set_no_default_conflict(self):
        arglist = [
            '--default',
            '--no-default',
            self._subnet_pool.name,
        ]
        verifylist = [
            ('default', True),
            ('no_default', True),
            ('subnet_pool', self._subnet_pool.name),
        ]

        # Exclusive arguments will conflict here.
        self.assertRaises(tests_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)


class TestShowSubnetPool(TestSubnetPool):

    # The subnet_pool to set.
    _subnet_pool = network_fakes.FakeSubnetPool.create_one_subnet_pool()

    columns = (
        'address_scope_id',
        'default_prefixlen',
        'default_quota',
        'id',
        'ip_version',
        'is_default',
        'max_prefixlen',
        'min_prefixlen',
        'name',
        'prefixes',
        'project_id',
        'shared',
    )

    data = (
        _subnet_pool.address_scope_id,
        _subnet_pool.default_prefixlen,
        _subnet_pool.default_quota,
        _subnet_pool.id,
        _subnet_pool.ip_version,
        _subnet_pool.is_default,
        _subnet_pool.max_prefixlen,
        _subnet_pool.min_prefixlen,
        _subnet_pool.name,
        utils.format_list(_subnet_pool.prefixes),
        _subnet_pool.tenant_id,
        _subnet_pool.shared,
    )

    def setUp(self):
        super(TestShowSubnetPool, self).setUp()

        self.network.find_subnet_pool = mock.Mock(
            return_value=self._subnet_pool
        )

        # Get the command object to test
        self.cmd = subnet_pool.ShowSubnetPool(self.app, self.namespace)

    def test_show_no_options(self):
        arglist = []
        verifylist = []

        self.assertRaises(tests_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_show_all_options(self):
        arglist = [
            self._subnet_pool.name,
        ]
        verifylist = [
            ('subnet_pool', self._subnet_pool.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network.find_subnet_pool.assert_called_once_with(
            self._subnet_pool.name,
            ignore_missing=False
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)
