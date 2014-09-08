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
from openstackclient.tests import utils


BASE_URL = 'https://api.example.com:1234/vX'

LIST_RESP = [
    {'id': '1', 'name': 'alpha'},
    {'id': '2', 'name': 'beta'},
]

LIST_BODY = {
    'p1': 'xxx',
    'p2': 'yyy',
}

SHOW_RESP = {
    'id': '3',
    'name': 'delta',
}


class TestBaseAPI(utils.TestCase):

    def setUp(self):
        super(TestBaseAPI, self).setUp()
        sess = session.Session()
        self.api = api.BaseAPI(session=sess, endpoint=BASE_URL)
        self.requests_mock = self.useFixture(fixture.Fixture())

    def test_create_post(self):
        self.requests_mock.register_uri(
            'POST',
            BASE_URL + '/qaz',
            json=SHOW_RESP,
            status_code=202,
        )
        ret = self.api.create('qaz')
        self.assertEqual(SHOW_RESP, ret)

    def test_create_put(self):
        self.requests_mock.register_uri(
            'PUT',
            BASE_URL + '/qaz',
            json=SHOW_RESP,
            status_code=202,
        )
        ret = self.api.create('qaz', method='PUT')
        self.assertEqual(SHOW_RESP, ret)

    def test_delete(self):
        self.requests_mock.register_uri(
            'DELETE',
            BASE_URL + '/qaz',
            status_code=204,
        )
        ret = self.api.delete('qaz')
        self.assertEqual(204, ret.status_code)

    def test_find_bulk_none(self):
        self.requests_mock.register_uri(
            'GET',
            BASE_URL + '/qaz',
            json=LIST_RESP,
            status_code=200,
        )
        ret = self.api.find_bulk('qaz')
        self.assertEqual(LIST_RESP, ret)

    def test_find_bulk_one(self):
        self.requests_mock.register_uri(
            'GET',
            BASE_URL + '/qaz',
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
            BASE_URL + '/qaz',
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
            BASE_URL + '/qaz',
            json={'qaz': LIST_RESP},
            status_code=200,
        )
        ret = self.api.find_bulk('qaz', id='1')
        self.assertEqual([LIST_RESP[0]], ret)

    def test_list_no_body(self):
        self.requests_mock.register_uri(
            'GET',
            BASE_URL + '/qaz',
            json=LIST_RESP,
            status_code=200,
        )
        ret = self.api.list('qaz')
        self.assertEqual(LIST_RESP, ret)

    def test_list_body(self):
        self.requests_mock.register_uri(
            'POST',
            BASE_URL + '/qaz',
            json=LIST_RESP,
            status_code=200,
        )
        ret = self.api.list('qaz', body=LIST_BODY)
        self.assertEqual(LIST_RESP, ret)
