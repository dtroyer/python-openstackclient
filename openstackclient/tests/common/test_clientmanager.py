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

import mock

from openstackclient.common import api_discovery
from openstackclient.common import clientmanager
from openstackclient.tests import utils


AUTH_TOKEN = "foobar"
AUTH_URL = "http://0.0.0.0"


class Container(object):
    attr = clientmanager.ClientCache(lambda x: object())

    def __init__(self):
        pass


class TestClientManager(utils.TestCase):
    def setUp(self):
        super(TestClientManager, self).setUp()

        api_version = {"identity": "2.0"}

        vers = (
            api_discovery.ApiVersion(id='2.0', name='xx', status='stable'),
            api_discovery.ApiVersion(id='2.0', name='xx', status='stable'),
        )
        id_mock = mock.patch(
            'openstackclient.common.clientmanager.identity_client.IdentityVersion',  # noqa
            return_value=vers,
        )

        with id_mock:
            self.client_manager = clientmanager.ClientManager(
                token=AUTH_TOKEN,
                url=AUTH_URL,
                auth_url=AUTH_URL,
                api_version=api_version,
            )

    def test_singleton(self):
        # NOTE(dtroyer): Verify that the ClientCache descriptor only invokes
        # the factory one time and always returns the same value after that.
        c = Container()
        self.assertEqual(c.attr, c.attr)

#     def test_make_client_identity_default(self):
#         self.assertEqual(
#             self.client_manager.identity.auth_token,
#             AUTH_TOKEN,
#         )
#         self.assertEqual(
#             self.client_manager.identity.management_url,
#             AUTH_URL,
#         )
