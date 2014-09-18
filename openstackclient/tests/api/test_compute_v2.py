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

"""Compute v2 API Library Tests"""

from requests_mock.contrib import fixture

from keystoneclient import session
from openstackclient.api import compute_v2 as compute
from openstackclient.tests import utils


FAKE_PROJECT = 'xyzpdq'
FAKE_URL = 'http://gopher.com/v2/' + FAKE_PROJECT


class TestComputeAPIv2(utils.TestCase):

    def setUp(self):
        super(TestComputeAPIv2, self).setUp()
        sess = session.Session()
        self.api = compute.APIv2(session=sess, endpoint=FAKE_URL)
        self.requests_mock = self.useFixture(fixture.Fixture())


class TestFlavor(TestComputeAPIv2):

    FAKE_FLAVOR_RESP = {'id': '1', 'name': 'flavor1'}
    LIST_FLAVOR_RESP = [
        {'id': '1', 'name': 'flavor1'},
        {'id': '2', 'name': 'flavor2'},
    ]

    def test_flavor_create_no_options(self):
        # TODO(dtroyer): need to do checking on body passed in
        self.requests_mock.register_uri(
            'POST',
            FAKE_URL + '/flavors',
            json={'flavor': self.FAKE_FLAVOR_RESP},
            status_code=200,
        )
        ret = self.api.flavor_create('qaz')
        self.assertEqual(self.FAKE_FLAVOR_RESP, ret)

    def test_flavor_list_no_options(self):
        self.requests_mock.register_uri(
            'GET',
            FAKE_URL + '/flavors/detail',
            json={'flavors': self.LIST_FLAVOR_RESP},
            status_code=200,
        )
        ret = self.api.flavor_list()
        self.assertEqual(self.LIST_FLAVOR_RESP, ret)

    def test_flavor_show(self):
        self.requests_mock.register_uri(
            'GET',
            FAKE_URL + '/flavors/1',
            json=self.FAKE_FLAVOR_RESP,
            status_code=200,
        )
        self.requests_mock.register_uri(
            'GET',
            FAKE_URL + '/flavors/flavor1',
            json=self.FAKE_FLAVOR_RESP,
            status_code=200,
        )
        ret = self.api.flavor_show(flavor='1')
        self.assertEqual(self.FAKE_FLAVOR_RESP, ret)

        ret = self.api.flavor_show(flavor='flavor1')
        self.assertEqual(self.FAKE_FLAVOR_RESP, ret)


class TestKey(TestComputeAPIv2):

    FAKE_KEY_1 = {
        "public_key": "ssh-rsa AAAA...ZZZZ waldo@whereami.org\n",
        "name": "waldo",
        "fingerprint": "a5:da:0c:52:e8:52:42:a3:4f:b8:22:62:7b:e4:e8:89",
    }
    FAKE_KEY_2 = {
        "public_key": "ssh-rsa AAAA...ZZZZ carmen@intheworld.org\n",
        "name": "carmen",
        "fingerprint": "a5:da:0c:52:e8:52:42:a3:4f:b8:22:62:7b:e4:e8:89",
    }
    LIST_KEY_RESP = [
        {'keypair': FAKE_KEY_1},
        {'keypair': FAKE_KEY_2},
    ]

    def test_key_list_no_options(self):
        self.requests_mock.register_uri(
            'GET',
            FAKE_URL + '/os-keypairs',
            json={'keypairs': self.LIST_KEY_RESP},
            status_code=200,
        )
        ret = self.api.key_list()
        self.assertEqual([self.FAKE_KEY_1, self.FAKE_KEY_2], ret)
