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

"""Base API Library Tests"""

from requests_mock.contrib import fixture

from keystoneclient import session
from openstackclient.api import api
from openstackclient.common import exceptions
from openstackclient.tests import utils


RESP_ITEM_1 = {
    'id': '1',
    'name': 'alpha',
    'status': 'UP',
}
RESP_ITEM_2 = {
    'id': '2',
    'name': 'beta',
    'status': 'DOWN',
}
RESP_ITEM_3 = {
    'id': '3',
    'name': 'delta',
    'status': 'UP',
}

LIST_RESP = [RESP_ITEM_1, RESP_ITEM_2]

LIST_BODY = {
    'p1': 'xxx',
    'p2': 'yyy',
}


class TestSession(utils.TestCase):

    BASE_URL = 'https://api.example.com:1234/vX'

    def setUp(self):
        super(TestSession, self).setUp()
        self.sess = session.Session()
        self.requests_mock = self.useFixture(fixture.Fixture())


class TestKeystoneSession(TestSession):

    def setUp(self):
        super(TestKeystoneSession, self).setUp()
        self.api = api.KeystoneSession(
            session=self.sess,
            endpoint=self.BASE_URL,
        )

    def test_session_request(self):
        self.requests_mock.register_uri(
            'GET',
            self.BASE_URL + '/qaz',
            json=RESP_ITEM_1,
            status_code=200,
        )
        ret = self.api._request('GET', '/qaz')
        self.assertEqual(RESP_ITEM_1, ret.json())


class TestBaseAPI(TestSession):

    def setUp(self):
        super(TestBaseAPI, self).setUp()
        self.api = api.BaseAPI(
            session=self.sess,
            endpoint=self.BASE_URL,
        )

    def test_create_post(self):
        self.requests_mock.register_uri(
            'POST',
            self.BASE_URL + '/qaz',
            json=RESP_ITEM_1,
            status_code=202,
        )
        ret = self.api.create('qaz')
        self.assertEqual(RESP_ITEM_1, ret)

    def test_create_put(self):
        self.requests_mock.register_uri(
            'PUT',
            self.BASE_URL + '/qaz',
            json=RESP_ITEM_1,
            status_code=202,
        )
        ret = self.api.create('qaz', method='PUT')
        self.assertEqual(RESP_ITEM_1, ret)

    def test_delete(self):
        self.requests_mock.register_uri(
            'DELETE',
            self.BASE_URL + '/qaz',
            status_code=204,
        )
        ret = self.api.delete('qaz')
        self.assertEqual(204, ret.status_code)

    # find tests

    def test_find_attr_by_id(self):

        # All first requests (by name) will fail in this test
        self.requests_mock.register_uri(
            'GET',
            self.BASE_URL + '/qaz?name=1',
            json={'qaz': []},
            status_code=200,
        )
        self.requests_mock.register_uri(
            'GET',
            self.BASE_URL + '/qaz?id=1',
            json={'qaz': [RESP_ITEM_1]},
            status_code=200,
        )
        ret = self.api.find_attr('qaz', '1')
        self.assertEqual(RESP_ITEM_1, ret)

        # value not found
        self.requests_mock.register_uri(
            'GET',
            self.BASE_URL + '/qaz?name=0',
            json={'qaz': []},
            status_code=200,
        )
        self.requests_mock.register_uri(
            'GET',
            self.BASE_URL + '/qaz?id=0',
            json={'qaz': []},
            status_code=200,
        )
        self.assertRaises(
            exceptions.CommandError,
            self.api.find_attr,
            'qaz',
            '0',
        )

        # Attribute other than 'name'
        self.requests_mock.register_uri(
            'GET',
            self.BASE_URL + '/qaz?status=UP',
            json={'qaz': [RESP_ITEM_1]},
            status_code=200,
        )
        ret = self.api.find_attr('qaz', 'UP', attr='status')
        self.assertEqual(RESP_ITEM_1, ret)
        ret = self.api.find_attr('qaz', value='UP', attr='status')
        self.assertEqual(RESP_ITEM_1, ret)

    def test_find_attr_by_name(self):
        self.requests_mock.register_uri(
            'GET',
            self.BASE_URL + '/qaz?name=alpha',
            json={'qaz': [RESP_ITEM_1]},
            status_code=200,
        )
        ret = self.api.find_attr('qaz', 'alpha')
        self.assertEqual(RESP_ITEM_1, ret)

        # value not found
        self.requests_mock.register_uri(
            'GET',
            self.BASE_URL + '/qaz?name=0',
            json={'qaz': []},
            status_code=200,
        )
        self.requests_mock.register_uri(
            'GET',
            self.BASE_URL + '/qaz?id=0',
            json={'qaz': []},
            status_code=200,
        )
        self.assertRaises(
            exceptions.CommandError,
            self.api.find_attr,
            'qaz',
            '0',
        )

        # Attribute other than 'name'
        self.requests_mock.register_uri(
            'GET',
            self.BASE_URL + '/qaz?status=UP',
            json={'qaz': [RESP_ITEM_1]},
            status_code=200,
        )
        ret = self.api.find_attr('qaz', 'UP', attr='status')
        self.assertEqual(RESP_ITEM_1, ret)
        ret = self.api.find_attr('qaz', value='UP', attr='status')
        self.assertEqual(RESP_ITEM_1, ret)

    def test_find_attr_path_resource(self):

        # Test resource different than path
        self.requests_mock.register_uri(
            'GET',
            self.BASE_URL + '/wsx?name=1',
            json={'qaz': []},
            status_code=200,
        )
        self.requests_mock.register_uri(
            'GET',
            self.BASE_URL + '/wsx?id=1',
            json={'qaz': [RESP_ITEM_1]},
            status_code=200,
        )
        ret = self.api.find_attr('wsx', '1', resource='qaz')
        self.assertEqual(RESP_ITEM_1, ret)

    def test_find_bulk_none(self):
        self.requests_mock.register_uri(
            'GET',
            self.BASE_URL + '/qaz',
            json=LIST_RESP,
            status_code=200,
        )
        ret = self.api.find_bulk('qaz')
        self.assertEqual(LIST_RESP, ret)

    def test_find_bulk_one(self):
        self.requests_mock.register_uri(
            'GET',
            self.BASE_URL + '/qaz',
            json=LIST_RESP,
            status_code=200,
        )
        ret = self.api.find_bulk('qaz', id='1')
        self.assertEqual([LIST_RESP[0]], ret)

        ret = self.api.find_bulk('qaz', id='0')
        self.assertEqual([], ret)

        ret = self.api.find_bulk('qaz', name='beta')
        self.assertEqual([LIST_RESP[1]], ret)

        ret = self.api.find_bulk('qaz', error='bogus')
        self.assertEqual([], ret)

    def test_find_bulk_two(self):
        self.requests_mock.register_uri(
            'GET',
            self.BASE_URL + '/qaz',
            json=LIST_RESP,
            status_code=200,
        )
        ret = self.api.find_bulk('qaz', id='1', name='alpha')
        self.assertEqual([LIST_RESP[0]], ret)

        ret = self.api.find_bulk('qaz', id='1', name='beta')
        self.assertEqual([], ret)

        ret = self.api.find_bulk('qaz', id='1', error='beta')
        self.assertEqual([], ret)

    def test_find_bulk_dict(self):
        self.requests_mock.register_uri(
            'GET',
            self.BASE_URL + '/qaz',
            json={'qaz': LIST_RESP},
            status_code=200,
        )
        ret = self.api.find_bulk('qaz', id='1')
        self.assertEqual([LIST_RESP[0]], ret)

    # list tests

    def test_list_no_body(self):
        self.requests_mock.register_uri(
            'GET',
            self.BASE_URL + '/qaz',
            json=LIST_RESP,
            status_code=200,
        )
        ret = self.api.list('qaz')
        self.assertEqual(LIST_RESP, ret)

    def test_list_body(self):
        self.requests_mock.register_uri(
            'POST',
            self.BASE_URL + '/qaz',
            json=LIST_RESP,
            status_code=200,
        )
        ret = self.api.list('qaz', body=LIST_BODY)
        self.assertEqual(LIST_RESP, ret)

    def test_list_detailed(self):
        self.requests_mock.register_uri(
            'GET',
            self.BASE_URL + '/qaz/details',
            json=LIST_RESP,
            status_code=200,
        )
        ret = self.api.list('qaz', detailed=True)
        self.assertEqual(LIST_RESP, ret)

    def test_list_filtered(self):
        self.requests_mock.register_uri(
            'GET',
            self.BASE_URL + '/qaz?attr=value',
            json=LIST_RESP,
            status_code=200,
        )
        ret = self.api.list('qaz', attr='value')
        self.assertEqual(LIST_RESP, ret)

    def test_list_wrapped(self):
        self.requests_mock.register_uri(
            'GET',
            self.BASE_URL + '/qaz?attr=value',
            json={'responses': LIST_RESP},
            status_code=200,
        )
        ret = self.api.list('qaz', attr='value')
        self.assertEqual({'responses': LIST_RESP}, ret)
