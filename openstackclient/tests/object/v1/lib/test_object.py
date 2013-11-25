#   Copyright 2013 Nebula Inc.
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

"""Test Object API library module"""

import mock

from openstackclient.object.v1.lib import object as lib_object
from openstackclient.tests.common import test_restapi as restapi
from openstackclient.tests.object.v1 import fakes as object_fakes


fake_account = 'q12we34r'
fake_auth = '11223344556677889900'
fake_url = 'http://gopher.com/v1/' + fake_account

fake_container = 'rainbarrel'
fake_object = 'raindrop'


class FakeClient(object):
    def __init__(self, endpoint=None, **kwargs):
        self.endpoint = fake_url
        self.token = fake_auth


class TestObject(object_fakes.TestObjectv1):

    def setUp(self):
        super(TestObject, self).setUp()
        self.app.restapi = mock.MagicMock()


class TestObjectListObjects(TestObject):

    def test_list_objects_no_options(self):
        resp = [{'name': 'is-name'}]
        self.app.restapi.list.return_value = resp

        data = lib_object.list_objects(
            self.app.restapi,
            fake_url,
            fake_container,
        )

        # Check expected values
        self.app.restapi.list.assert_called_with(
            fake_url + '/' + fake_container,
            params={
                'format': 'json',
            }
        )
        self.assertEqual(data, resp)

    def test_list_objects_marker(self):
        resp = [{'name': 'is-name'}]
        self.app.restapi.list.return_value = resp

        data = lib_object.list_objects(
            self.app.restapi,
            fake_url,
            fake_container,
            marker='next',
        )

        # Check expected values
        self.app.restapi.list.assert_called_with(
            fake_url + '/' + fake_container,
            params={
                'format': 'json',
                'marker': 'next',
            }
        )
        self.assertEqual(data, resp)

    def test_list_objects_limit(self):
        resp = [{'name': 'is-name'}]
        self.app.restapi.list.return_value = resp

        data = lib_object.list_objects(
            self.app.restapi,
            fake_url,
            fake_container,
            limit=5,
        )

        # Check expected values
        self.app.restapi.list.assert_called_with(
            fake_url + '/' + fake_container,
            params={
                'format': 'json',
                'limit': 5,
            }
        )
        self.assertEqual(data, resp)

    def test_list_objects_end_marker(self):
        resp = [{'name': 'is-name'}]
        self.app.restapi.list.return_value = resp

        data = lib_object.list_objects(
            self.app.restapi,
            fake_url,
            fake_container,
            end_marker='last',
        )

        # Check expected values
        self.app.restapi.list.assert_called_with(
            fake_url + '/' + fake_container,
            params={
                'format': 'json',
                'end_marker': 'last',
            }
        )
        self.assertEqual(data, resp)

    def test_list_objects_delimiter(self):
        resp = [{'name': 'is-name'}]
        self.app.restapi.list.return_value = resp

        data = lib_object.list_objects(
            self.app.restapi,
            fake_url,
            fake_container,
            delimiter='|',
        )

        # Check expected values
        # NOTE(dtroyer): requests handles the URL encoding and we're
        #                mocking that so use the otherwise-not-legal
        #                pipe '|' char in the response.
        self.app.restapi.list.assert_called_with(
            fake_url + '/' + fake_container,
            params={
                'format': 'json',
                'delimiter': '|',
            }
        )
        self.assertEqual(data, resp)

    def test_list_objects_prefix(self):
        resp = [{'name': 'is-name'}]
        self.app.restapi.list.return_value = resp

        data = lib_object.list_objects(
            self.app.restapi,
            fake_url,
            fake_container,
            prefix='foo/',
        )

        # Check expected values
        self.app.restapi.list.assert_called_with(
            fake_url + '/' + fake_container,
            params={
                'format': 'json',
                'prefix': 'foo/',
            }
        )
        self.assertEqual(data, resp)

    def test_list_objects_path(self):
        resp = [{'name': 'is-name'}]
        self.app.restapi.list.return_value = resp

        data = lib_object.list_objects(
            self.app.restapi,
            fake_url,
            fake_container,
            path='next',
        )

        # Check expected values
        self.app.restapi.list.assert_called_with(
            fake_url + '/' + fake_container,
            params={
                'format': 'json',
                'path': 'next',
            }
        )
        self.assertEqual(data, resp)

    def test_list_objects_full_listing(self):

        def side_effect(*args, **kwargs):
            rv = self.app.restapi.list.return_value
            self.app.restapi.list.return_value = []
            self.app.restapi.list.side_effect = None
            return rv

        resp = [{'name': 'is-name'}]
        self.app.restapi.list.return_value = resp
        self.app.restapi.list.side_effect = side_effect

        data = lib_object.list_objects(
            self.app.restapi,
            fake_url,
            fake_container,
            full_listing=True,
        )

        # Check expected values
        self.app.restapi.list.assert_called_with(
            fake_url + '/' + fake_container,
            params={
                'format': 'json',
                'marker': 'is-name',
            }
        )
        self.assertEqual(data, resp)


class TestObjectShowObjects(TestObject):

    def test_object_show_no_options(self):
        resp = {
            'content-type': 'text/alpha',
        }
        self.app.restapi.head.return_value = \
            restapi.FakeResponse(headers=resp)

        data = lib_object.show_object(
            self.app.restapi,
            fake_url,
            fake_container,
            fake_object,
        )

        # Check expected values
        self.app.restapi.head.assert_called_with(
            fake_url + '/%s/%s' % (fake_container, fake_object),
        )

        data_expected = {
            'account': fake_account,
            'container': fake_container,
            'object': fake_object,
            'content-type': 'text/alpha',
        }
        self.assertEqual(data, data_expected)

    def test_object_show_all_options(self):
        resp = {
            'content-type': 'text/alpha',
            'content-length': 577,
            'last-modified': '20130101',
            'etag': 'qaz',
            'x-object-manifest': None,
            'x-object-meta-wife': 'Wilma',
            'x-tra-header': 'yabba-dabba-do',
        }
        self.app.restapi.head.return_value = \
            restapi.FakeResponse(headers=resp)

        data = lib_object.show_object(
            self.app.restapi,
            fake_url,
            fake_container,
            fake_object,
        )

        # Check expected values
        self.app.restapi.head.assert_called_with(
            fake_url + '/%s/%s' % (fake_container, fake_object),
        )

        data_expected = {
            'account': fake_account,
            'container': fake_container,
            'object': fake_object,
            'content-type': 'text/alpha',
            'content-length': 577,
            'last-modified': '20130101',
            'etag': 'qaz',
            'x-object-manifest': None,
            'Wife': 'Wilma',
            'X-Tra-Header': 'yabba-dabba-do',
        }
        self.assertEqual(data, data_expected)
