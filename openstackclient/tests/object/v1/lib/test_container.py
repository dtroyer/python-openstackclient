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

from openstackclient.object.v1.lib import container as lib_container
from openstackclient.tests.common import test_restapi as restapi
from openstackclient.tests.object.v1 import fakes as object_fakes


fake_account = 'q12we34r'
fake_auth = '11223344556677889900'
fake_url = 'http://gopher.com/v1/' + fake_account

fake_container = 'rainbarrel'


class FakeClient(object):
    def __init__(self, endpoint=None, **kwargs):
        self.endpoint = fake_url
        self.token = fake_auth


class TestContainer(object_fakes.TestObjectv1):

    def setUp(self):
        super(TestContainer, self).setUp()
        self.app.restapi = mock.MagicMock()


class TestContainerList(TestContainer):

    def test_container_list_no_options(self):
        resp = [{'name': 'is-name'}]
        self.app.restapi.list.return_value = resp

        data = lib_container.list_containers(
            self.app.restapi,
            fake_url,
        )

        # Check expected values
        self.app.restapi.list.assert_called_with(
            fake_url,
            params={
                'format': 'json',
            }
        )
        self.assertEqual(data, resp)

    def test_container_list_marker(self):
        resp = [{'name': 'is-name'}]
        self.app.restapi.list.return_value = resp

        data = lib_container.list_containers(
            self.app.restapi,
            fake_url,
            marker='next',
        )

        # Check expected values
        self.app.restapi.list.assert_called_with(
            fake_url,
            params={
                'format': 'json',
                'marker': 'next',
            }
        )
        self.assertEqual(data, resp)

    def test_container_list_limit(self):
        resp = [{'name': 'is-name'}]
        self.app.restapi.list.return_value = resp

        data = lib_container.list_containers(
            self.app.restapi,
            fake_url,
            limit=5,
        )

        # Check expected values
        self.app.restapi.list.assert_called_with(
            fake_url,
            params={
                'format': 'json',
                'limit': 5,
            }
        )
        self.assertEqual(data, resp)

    def test_container_list_end_marker(self):
        resp = [{'name': 'is-name'}]
        self.app.restapi.list.return_value = resp

        data = lib_container.list_containers(
            self.app.restapi,
            fake_url,
            end_marker='last',
        )

        # Check expected values
        self.app.restapi.list.assert_called_with(
            fake_url,
            params={
                'format': 'json',
                'end_marker': 'last',
            }
        )
        self.assertEqual(data, resp)

    def test_container_list_prefix(self):
        resp = [{'name': 'is-name'}]
        self.app.restapi.list.return_value = resp

        data = lib_container.list_containers(
            self.app.restapi,
            fake_url,
            prefix='foo/',
        )

        # Check expected values
        self.app.restapi.list.assert_called_with(
            fake_url,
            params={
                'format': 'json',
                'prefix': 'foo/',
            }
        )
        self.assertEqual(data, resp)

    def test_container_list_full_listing(self):

        def side_effect(*args, **kwargs):
            rv = self.app.restapi.list.return_value
            self.app.restapi.list.return_value = []
            self.app.restapi.list.side_effect = None
            return rv

        resp = [{'name': 'is-name'}]
        self.app.restapi.list.return_value = resp
        self.app.restapi.list.side_effect = side_effect

        data = lib_container.list_containers(
            self.app.restapi,
            fake_url,
            full_listing=True,
        )

        # Check expected values
        self.app.restapi.list.assert_called_with(
            fake_url,
            params={
                'format': 'json',
                'marker': 'is-name',
            }
        )
        self.assertEqual(data, resp)


class TestContainerShow(TestContainer):

    def test_container_show_no_options(self):
        resp = {
            'x-container-object-count': 1,
            'x-container-bytes-used': 577,
        }
        self.app.restapi.head.return_value = \
            restapi.FakeResponse(headers=resp)

        data = lib_container.show_container(
            self.app.restapi,
            fake_url,
            'is-name',
        )

        # Check expected values
        self.app.restapi.head.assert_called_with(
            fake_url + '/is-name',
        )

        data_expected = {
            'account': fake_account,
            'container': 'is-name',
            'object_count': 1,
            'bytes_used': 577,
            'read_acl': None,
            'write_acl': None,
            'sync_to': None,
            'sync_key': None,
        }
        self.assertEqual(data, data_expected)
