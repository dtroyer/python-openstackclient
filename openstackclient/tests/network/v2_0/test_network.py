#   Copyright 2013 OpenStack, LLC.
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

from openstackclient.network.v2_0 import network
from openstackclient.tests.network.v2_0 import common


class TestCreateNetwork(common.TestNetworkBase):
    def test_get_parser_nothing(self):
        given = "noo" + self.given_default_show_options()
        parsed = self.given_args(network.CreateNetwork, given)
        self.assertEqual('noo', parsed.name)
        self.assertEqual(True, parsed.admin_state)
        self.assertEqual(False, parsed.shared)
        self.assertEqual(None, parsed.tenant_id)
        self.then_default_show_options(parsed)

    def test_get_parser_all(self):
        allargs = "too --admin-state-down --shared --project sneed"
        allargs += self.given_all_show_options()
        parsed = self.given_args(network.CreateNetwork, allargs)
        self.assertEqual('too', parsed.name)
        self.assertEqual(False, parsed.admin_state)
        self.assertEqual(True, parsed.shared)
        self.assertEqual('sneed', parsed.tenant_id)
        self.then_all_show_options(parsed)


class TestDeleteNetwork(common.TestNetworkBase):
    def test_get_parser_nothing(self):
        parsed = self.given_args(network.DeleteNetwork, "noo")
        self.assertEqual('noo', parsed.id)


class TestListNetwork(common.TestNetworkBase):
    def test_get_parser_nothing(self):
        given = "" + self.given_default_list_options()
        parsed = self.given_args(network.ListNetwork, given)
        self.assertEqual(False, parsed.show_details)
        self.assertEqual(False, parsed.external)
        self.then_default_list_options(parsed)

    def test_get_parser_all(self):
        allargs = "--long --external" + self.given_all_list_options()
        parsed = self.given_args(network.ListNetwork, allargs)
        self.assertEqual(True, parsed.show_details)
        self.assertEqual(True, parsed.external)
        self.then_all_list_options(parsed)


class TestSetNetwork(common.TestNetworkBase):
    def test_get_parser_nothing(self):
        parsed = self.given_args(network.SetNetwork, "noo")
        self.assertEqual('noo', parsed.network)


class TestShowNetwork(common.TestNetworkBase):
    def test_get_parser_nothing(self):
        given = "noo" + self.given_default_show_options()
        parsed = self.given_args(network.ShowNetwork, given)
        self.assertEqual('noo', parsed.id)
        self.then_default_show_options(parsed)

    def test_get_parser_all(self):
        allargs = "too " + self.given_all_show_options()
        parsed = self.given_args(network.ShowNetwork, allargs)
        self.assertEqual('too', parsed.id)
        self.then_all_show_options(parsed)


class TestAddGatewayNetwork(common.TestNetworkBase):
    def test_get_parser_nothing(self):
        given = "netty getty"
        parsed = self.given_args(network.AddGatewayNetwork, given)
        self.assertEqual('netty', parsed.network_id)
        self.assertEqual('getty', parsed.net_gateway_id)
        self.assertEqual(None, parsed.segmentation_type)
        self.assertEqual(None, parsed.segmentation_id)

    def test_get_parser_all(self):
        allargs = "netty getty --segmentation-type 1 --segmentation-id 2"
        parsed = self.given_args(network.AddGatewayNetwork, allargs)
        self.assertEqual('netty', parsed.network_id)
        self.assertEqual('getty', parsed.net_gateway_id)
        self.assertEqual('1', parsed.segmentation_type)
        self.assertEqual('2', parsed.segmentation_id)


class TestRemoveGatewayNetwork(common.TestNetworkBase):
    def test_get_parser_nothing(self):
        given = "netty getty"
        parsed = self.given_args(network.RemoveGatewayNetwork, given)
        self.assertEqual('netty', parsed.network_id)
        self.assertEqual('getty', parsed.net_gateway_id)
        self.assertEqual(None, parsed.segmentation_type)
        self.assertEqual(None, parsed.segmentation_id)

    def test_get_parser_all(self):
        allargs = "netty getty --segmentation-type 1 --segmentation-id 2"
        parsed = self.given_args(network.RemoveGatewayNetwork, allargs)
        self.assertEqual('netty', parsed.network_id)
        self.assertEqual('getty', parsed.net_gateway_id)
        self.assertEqual('1', parsed.segmentation_type)
        self.assertEqual('2', parsed.segmentation_id)
