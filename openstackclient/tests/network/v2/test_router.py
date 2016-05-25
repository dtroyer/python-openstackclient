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

import mock

from osc_lib import exceptions

from openstackclient.common import utils as osc_utils
from openstackclient.network.v2 import router
from openstackclient.tests.network.v2 import fakes as network_fakes
from openstackclient.tests import utils as tests_utils


class TestRouter(network_fakes.TestNetworkV2):

    def setUp(self):
        super(TestRouter, self).setUp()

        # Get a shortcut to the network client
        self.network = self.app.client_manager.network


class TestAddPortToRouter(TestRouter):
    '''Add port to Router '''

    _port = network_fakes.FakePort.create_one_port()
    _router = network_fakes.FakeRouter.create_one_router(
        attrs={'port': _port.id})

    def setUp(self):
        super(TestAddPortToRouter, self).setUp()
        self.network.router_add_interface = mock.Mock()
        self.cmd = router.AddPortToRouter(self.app, self.namespace)
        self.network.find_router = mock.Mock(return_value=self._router)
        self.network.find_port = mock.Mock(return_value=self._port)

    def test_add_port_no_option(self):
        arglist = []
        verifylist = []

        self.assertRaises(tests_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_add_port_required_options(self):
        arglist = [
            self._router.id,
            self._router.port,
        ]
        verifylist = [
            ('router', self._router.id),
            ('port', self._router.port),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.network.router_add_interface.assert_called_with(self._router, **{
            'port_id': self._router.port,
        })
        self.assertIsNone(result)


class TestAddSubnetToRouter(TestRouter):
    '''Add subnet to Router '''

    _subnet = network_fakes.FakeSubnet.create_one_subnet()
    _router = network_fakes.FakeRouter.create_one_router(
        attrs={'subnet': _subnet.id})

    def setUp(self):
        super(TestAddSubnetToRouter, self).setUp()
        self.network.router_add_interface = mock.Mock()
        self.cmd = router.AddSubnetToRouter(self.app, self.namespace)
        self.network.find_router = mock.Mock(return_value=self._router)
        self.network.find_subnet = mock.Mock(return_value=self._subnet)

    def test_add_subnet_no_option(self):
        arglist = []
        verifylist = []

        self.assertRaises(tests_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_add_subnet_required_options(self):
        arglist = [
            self._router.id,
            self._router.subnet,
        ]
        verifylist = [
            ('router', self._router.id),
            ('subnet', self._router.subnet),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.network.router_add_interface.assert_called_with(
            self._router, **{'subnet_id': self._router.subnet})

        self.assertIsNone(result)


class TestCreateRouter(TestRouter):

    # The new router created.
    new_router = network_fakes.FakeRouter.create_one_router()

    columns = (
        'admin_state_up',
        'availability_zone_hints',
        'availability_zones',
        'distributed',
        'external_gateway_info',
        'ha',
        'id',
        'name',
        'project_id',
        'routes',
        'status',
    )
    data = (
        router._format_admin_state(new_router.admin_state_up),
        osc_utils.format_list(new_router.availability_zone_hints),
        osc_utils.format_list(new_router.availability_zones),
        new_router.distributed,
        router._format_external_gateway_info(new_router.external_gateway_info),
        new_router.ha,
        new_router.id,
        new_router.name,
        new_router.tenant_id,
        router._format_routes(new_router.routes),
        new_router.status,
    )

    def setUp(self):
        super(TestCreateRouter, self).setUp()

        self.network.create_router = mock.Mock(return_value=self.new_router)

        # Get the command object to test
        self.cmd = router.CreateRouter(self.app, self.namespace)

    def test_create_no_options(self):
        arglist = []
        verifylist = []

        self.assertRaises(tests_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_create_default_options(self):
        arglist = [
            self.new_router.name,
        ]
        verifylist = [
            ('name', self.new_router.name),
            ('enable', True),
            ('distributed', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = (self.cmd.take_action(parsed_args))

        self.network.create_router.assert_called_once_with(**{
            'admin_state_up': True,
            'name': self.new_router.name,
        })
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_create_with_AZ_hints(self):
        arglist = [
            self.new_router.name,
            '--availability-zone-hint', 'fake-az',
            '--availability-zone-hint', 'fake-az2',
        ]
        verifylist = [
            ('name', self.new_router.name),
            ('availability_zone_hints', ['fake-az', 'fake-az2']),
            ('enable', True),
            ('distributed', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = (self.cmd.take_action(parsed_args))
        self.network.create_router.assert_called_once_with(**{
            'admin_state_up': True,
            'name': self.new_router.name,
            'availability_zone_hints': ['fake-az', 'fake-az2'],
        })

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)


class TestDeleteRouter(TestRouter):

    # The router to delete.
    _router = network_fakes.FakeRouter.create_one_router()

    def setUp(self):
        super(TestDeleteRouter, self).setUp()

        self.network.delete_router = mock.Mock(return_value=None)

        self.network.find_router = mock.Mock(return_value=self._router)

        # Get the command object to test
        self.cmd = router.DeleteRouter(self.app, self.namespace)

    def test_delete(self):
        arglist = [
            self._router.name,
        ]
        verifylist = [
            ('router', [self._router.name]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.network.delete_router.assert_called_once_with(self._router)
        self.assertIsNone(result)


class TestListRouter(TestRouter):

    # The routers going to be listed up.
    routers = network_fakes.FakeRouter.create_routers(count=3)

    columns = (
        'ID',
        'Name',
        'Status',
        'State',
        'Distributed',
        'HA',
        'Project',
    )
    columns_long = columns + (
        'Routes',
        'External gateway info',
        'Availability zones'
    )

    data = []
    for r in routers:
        data.append((
            r.id,
            r.name,
            r.status,
            router._format_admin_state(r.admin_state_up),
            r.distributed,
            r.ha,
            r.tenant_id,
        ))
    data_long = []
    for i in range(0, len(routers)):
        r = routers[i]
        data_long.append(
            data[i] + (
                router._format_routes(r.routes),
                router._format_external_gateway_info(r.external_gateway_info),
                osc_utils.format_list(r.availability_zones),
            )
        )

    def setUp(self):
        super(TestListRouter, self).setUp()

        # Get the command object to test
        self.cmd = router.ListRouter(self.app, self.namespace)

        self.network.routers = mock.Mock(return_value=self.routers)

    def test_router_list_no_options(self):
        arglist = []
        verifylist = [
            ('long', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.network.routers.assert_called_once_with()
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_router_list_long(self):
        arglist = [
            '--long',
        ]
        verifylist = [
            ('long', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.network.routers.assert_called_once_with()
        self.assertEqual(self.columns_long, columns)
        self.assertEqual(self.data_long, list(data))


class TestRemovePortFromRouter(TestRouter):
    '''Remove port from a Router '''

    _port = network_fakes.FakePort.create_one_port()
    _router = network_fakes.FakeRouter.create_one_router(
        attrs={'port': _port.id})

    def setUp(self):
        super(TestRemovePortFromRouter, self).setUp()
        self.network.router_remove_interface = mock.Mock()
        self.cmd = router.RemovePortFromRouter(self.app, self.namespace)
        self.network.find_router = mock.Mock(return_value=self._router)
        self.network.find_port = mock.Mock(return_value=self._port)

    def test_remove_port_no_option(self):
        arglist = []
        verifylist = []

        self.assertRaises(tests_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_remove_port_required_options(self):
        arglist = [
            self._router.id,
            self._router.port,
        ]
        verifylist = [
            ('router', self._router.id),
            ('port', self._router.port),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.network.router_remove_interface.assert_called_with(
            self._router, **{'port_id': self._router.port})
        self.assertIsNone(result)


class TestRemoveSubnetFromRouter(TestRouter):
    '''Remove subnet from Router '''

    _subnet = network_fakes.FakeSubnet.create_one_subnet()
    _router = network_fakes.FakeRouter.create_one_router(
        attrs={'subnet': _subnet.id})

    def setUp(self):
        super(TestRemoveSubnetFromRouter, self).setUp()
        self.network.router_remove_interface = mock.Mock()
        self.cmd = router.RemoveSubnetFromRouter(self.app, self.namespace)
        self.network.find_router = mock.Mock(return_value=self._router)
        self.network.find_subnet = mock.Mock(return_value=self._subnet)

    def test_remove_subnet_no_option(self):
        arglist = []
        verifylist = []

        self.assertRaises(tests_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_remove_subnet_required_options(self):
        arglist = [
            self._router.id,
            self._router.subnet,
        ]
        verifylist = [
            ('subnet', self._router.subnet),
            ('router', self._router.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.network.router_remove_interface.assert_called_with(
            self._router, **{'subnet_id': self._router.subnet})
        self.assertIsNone(result)


class TestSetRouter(TestRouter):

    # The router to set.
    _default_route = {'destination': '10.20.20.0/24', 'nexthop': '10.20.30.1'}
    _router = network_fakes.FakeRouter.create_one_router(
        attrs={'routes': [_default_route]}
    )

    def setUp(self):
        super(TestSetRouter, self).setUp()

        self.network.update_router = mock.Mock(return_value=None)

        self.network.find_router = mock.Mock(return_value=self._router)

        # Get the command object to test
        self.cmd = router.SetRouter(self.app, self.namespace)

    def test_set_this(self):
        arglist = [
            self._router.name,
            '--enable',
            '--distributed',
            '--name', 'noob',
        ]
        verifylist = [
            ('router', self._router.name),
            ('enable', True),
            ('distributed', True),
            ('name', 'noob'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        attrs = {
            'admin_state_up': True,
            'distributed': True,
            'name': 'noob',
        }
        self.network.update_router.assert_called_once_with(
            self._router, **attrs)
        self.assertIsNone(result)

    def test_set_that(self):
        arglist = [
            self._router.name,
            '--disable',
            '--centralized',
        ]
        verifylist = [
            ('router', self._router.name),
            ('disable', True),
            ('centralized', True),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        attrs = {
            'admin_state_up': False,
            'distributed': False,
        }
        self.network.update_router.assert_called_once_with(
            self._router, **attrs)
        self.assertIsNone(result)

    def test_set_distributed_centralized(self):
        arglist = [
            self._router.name,
            '--distributed',
            '--centralized',
        ]
        verifylist = [
            ('router', self._router.name),
            ('distributed', True),
            ('distributed', False),
        ]

        self.assertRaises(tests_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_set_route(self):
        arglist = [
            self._router.name,
            '--route', 'destination=10.20.30.0/24,gateway=10.20.30.1',
        ]
        verifylist = [
            ('router', self._router.name),
            ('routes', [{'destination': '10.20.30.0/24',
                         'gateway': '10.20.30.1'}]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        attrs = {
            'routes': self._router.routes + [{'destination': '10.20.30.0/24',
                                             'nexthop': '10.20.30.1'}],
        }
        self.network.update_router.assert_called_once_with(
            self._router, **attrs)
        self.assertIsNone(result)

    def test_set_no_route(self):
        arglist = [
            self._router.name,
            '--no-route',
        ]
        verifylist = [
            ('router', self._router.name),
            ('no_route', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        attrs = {
            'routes': [],
        }
        self.network.update_router.assert_called_once_with(
            self._router, **attrs)
        self.assertIsNone(result)

    def test_set_route_no_route(self):
        arglist = [
            self._router.name,
            '--route', 'destination=10.20.30.0/24,gateway=10.20.30.1',
            '--no-route',
        ]
        verifylist = [
            ('router', self._router.name),
            ('routes', [{'destination': '10.20.30.0/24',
                         'gateway': '10.20.30.1'}]),
            ('no_route', True),
        ]

        self.assertRaises(tests_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_set_clear_routes(self):
        arglist = [
            self._router.name,
            '--clear-routes',
        ]
        verifylist = [
            ('router', self._router.name),
            ('clear_routes', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        attrs = {
            'routes': [],
        }
        self.network.update_router.assert_called_once_with(
            self._router, **attrs)
        self.assertIsNone(result)

    def test_set_route_clear_routes(self):
        arglist = [
            self._router.name,
            '--route', 'destination=10.20.30.0/24,gateway=10.20.30.1',
            '--clear-routes',
        ]
        verifylist = [
            ('router', self._router.name),
            ('routes', [{'destination': '10.20.30.0/24',
                         'gateway': '10.20.30.1'}]),
            ('clear_routes', True),
        ]

        self.assertRaises(tests_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_set_nothing(self):
        arglist = [self._router.name, ]
        verifylist = [('router', self._router.name), ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(exceptions.CommandError, self.cmd.take_action,
                          parsed_args)


class TestShowRouter(TestRouter):

    # The router to set.
    _router = network_fakes.FakeRouter.create_one_router()

    columns = (
        'admin_state_up',
        'availability_zone_hints',
        'availability_zones',
        'distributed',
        'external_gateway_info',
        'ha',
        'id',
        'name',
        'project_id',
        'routes',
        'status',
    )
    data = (
        router._format_admin_state(_router.admin_state_up),
        osc_utils.format_list(_router.availability_zone_hints),
        osc_utils.format_list(_router.availability_zones),
        _router.distributed,
        router._format_external_gateway_info(_router.external_gateway_info),
        _router.ha,
        _router.id,
        _router.name,
        _router.tenant_id,
        router._format_routes(_router.routes),
        _router.status,
    )

    def setUp(self):
        super(TestShowRouter, self).setUp()

        self.network.find_router = mock.Mock(return_value=self._router)

        # Get the command object to test
        self.cmd = router.ShowRouter(self.app, self.namespace)

    def test_show_no_options(self):
        arglist = []
        verifylist = []

        self.assertRaises(tests_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_show_all_options(self):
        arglist = [
            self._router.name,
        ]
        verifylist = [
            ('router', self._router.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network.find_router.assert_called_once_with(
            self._router.name, ignore_missing=False)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)
