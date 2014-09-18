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

"""Base API Version Library Tests"""


from openstackclient.api import api
from openstackclient.tests.api import test_api


class TestBaseAPIVersion(test_api.TestSession):

    FAKE_VERSION_1 = {
        'status': 'stable',
        'id': '1',
        'links': [
            {
                'rel': 'self',
                'href': 'https://x.example.com/v1',
            },
            {
                'href': 'http://docs.example.com/api/1.0/content/',
                'type': 'text/html',
                'rel': 'describedby',
            },
        ],

    }

    FAKE_NORMAL_VERSION_1 = {
        'status': 'stable',
        'id': '1',
        'version': (1, 0),
        'url': 'https://x.example.com/v1',
    }

    FAKE_VERSION_2 = {
        'status': 'stable',
        'id': '2.3',
        'links': [
            {
                'rel': 'self',
                'href': 'https://x.example.com/v2',
            },
            {
                'href': 'http://docs.example.com/api/2.0/content/',
                'type': 'text/html',
                'rel': 'describedby',
            },
        ],

    }

    FAKE_NORMAL_VERSION_2 = {
        'status': 'stable',
        'id': '2.3',
        'version': (2, 3),
        'url': 'https://x.example.com/v2',
    }

    def setUp(self):
        super(TestBaseAPIVersion, self).setUp()
        self.apiver = api.BaseAPIVersion(
            session=self.sess,
            endpoint=self.BASE_URL,
        )

    def test_query_server_root_one(self):
        self.requests_mock.register_uri(
            'GET',
            self.BASE_URL + '/',
            json={'version': self.FAKE_VERSION_1},
            status_code=200,
        )
        ret = self.apiver.query_server_root()
        self.assertEqual([self.FAKE_VERSION_1], ret)

    def test_query_server_root_many(self):
        self.requests_mock.register_uri(
            'GET',
            self.BASE_URL + '/',
            json={'versions': [self.FAKE_VERSION_1]},
            status_code=300,
        )
        ret = self.apiver.query_server_root()
        self.assertEqual([self.FAKE_VERSION_1], ret)

    # TODO(dtroyer): Add exception handler tests

    def test_server_version_one(self):
        self.requests_mock.register_uri(
            'GET',
            self.BASE_URL + '/',
            json={'versions': [self.FAKE_VERSION_1]},
            status_code=300,
        )
        ret = self.apiver.server_versions()
        self.assertEqual([self.FAKE_NORMAL_VERSION_1], ret)

    def test_server_version_all(self):
        self.requests_mock.register_uri(
            'GET',
            self.BASE_URL + '/',
            json={'versions': [self.FAKE_VERSION_1, self.FAKE_VERSION_2]},
            status_code=300,
        )
        ret = self.apiver.server_versions()
        self.assertEqual(
            [
                self.FAKE_NORMAL_VERSION_1,
                self.FAKE_NORMAL_VERSION_2,
            ],
            ret,
        )

    def test_normalize_version(self):
        ver = self.apiver.normalize_version(None)
        self.assertEqual('', ver)

        ver = self.apiver.normalize_version('')
        self.assertEqual('', ver)

        ver = self.apiver.normalize_version('1')
        self.assertEqual('1', ver)

        ver = self.apiver.normalize_version('2.1')
        self.assertEqual('2.1', ver)

        ver = self.apiver.normalize_version('3.2.1')
        self.assertEqual('3.2.1', ver)

        ver = self.apiver.normalize_version('v2.0')
        self.assertEqual('2.0', ver)

        ver = self.apiver.normalize_version('v2.0a32-b1')
        self.assertEqual('2.0321', ver)

        self.assertRaises(
            TypeError,
            self.apiver.normalize_version,
            4.1,
        )

    def test_make_tuple(self):
        ver = self.apiver.make_version_tuple(None)
        self.assertEqual((), ver)

        ver = self.apiver.make_version_tuple('')
        self.assertEqual((), ver)

        ver = self.apiver.make_version_tuple('1')
        self.assertEqual((1, 0), ver)

        ver = self.apiver.make_version_tuple('2.1')
        self.assertEqual((2, 1), ver)

        ver = self.apiver.make_version_tuple('3.2.1')
        self.assertEqual((3, 2), ver)

        ver = self.apiver.make_version_tuple('v2.0')
        self.assertEqual((2, 0), ver)

        ver = self.apiver.make_version_tuple('v2.0a32-b1')
        self.assertEqual((2, 321), ver)

        self.assertRaises(
            TypeError,
            self.apiver.make_version_tuple,
            4.1,
        )
