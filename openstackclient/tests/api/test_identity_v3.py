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

"""Identity v3 API Library Tests"""

from requests_mock.contrib import fixture

from keystoneclient import session
from openstackclient.api import identity_v3
from openstackclient.tests import utils


FAKE_PROJECT = 'xyzpdq'
FAKE_URL = 'http://gopher.com/v2/' + FAKE_PROJECT


class TestIdentityAPIv3(utils.TestCase):

    def setUp(self):
        super(TestIdentityAPIv3, self).setUp()
        sess = session.Session()
        self.api = identity_v3.APIv3(session=sess, endpoint=FAKE_URL)
        self.requests_mock = self.useFixture(fixture.Fixture())


class TestProject(TestIdentityAPIv3):

    LIST_TENANT_RESP = [
        {'id': '1', 'name': 'p1', 'description': 'none', 'enabled': True},
        {'id': '2', 'name': 'p2', 'description': 'none', 'enabled': False},
        {'id': '3', 'name': 'p3', 'description': 'none', 'enabled': True},
    ]

    def test_project_list_no_options(self):
        self.requests_mock.register_uri(
            'GET',
            FAKE_URL + '/projects',
            json={'projects': self.LIST_TENANT_RESP},
            status_code=200,
        )
        ret = self.api.project_list()
        self.assertEqual(self.LIST_TENANT_RESP, ret)
