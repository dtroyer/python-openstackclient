#   Copyright 2014 Nebula Inc.
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

"""Test api_discovery module"""

import json
import mock
import requests

from openstackclient.common import api_discovery
from openstackclient.tests import utils

fake_user_agent = 'test_rapi'

FAPI_v2 = {
    "status": "stable",
    "updated": "2013-03-06T00:00:00Z",
    "media-types": [
        {
            "base": "application/json",
            "type": "application/vnd.openstack.identity-v2.0+json"
        },
        {
            "base": "application/xml",
            "type": "application/vnd.openstack.identity-v2.0+xml"
        }
    ],
    "id": "v2.0",
    "links": [
        {
            "href": "http://10.130.50.11:5000/v2.0/",
            "rel": "self"
        },
        {
            "href": "http://docs.openstack.org/api/openstack-identity-service/2.0/content/",  # noqa
            "type": "text/html",
            "rel": "describedby"
        },
        {
            "href": "http://docs.openstack.org/api/openstack-identity-service/2.0/identity-dev-guide-2.0.pdf",  # noqa
            "type": "application/pdf",
            "rel": "describedby"
        }
    ]
}

# default DevStack install
FAPI_v3 = {
    "status": "stable",
    "updated": "2013-03-06T00:00:00Z",
    "media-types": [
        {
            "base": "application/json",
            "type": "application/vnd.openstack.identity-v3+json"
        },
        {
            "base": "application/xml",
            "type": "application/vnd.openstack.identity-v3+xml"
        }
    ],
    "id": "v3.0",
    "links": [
        {
            "href": "http://10.130.50.11:35357/v3/",
            "rel": "self"
        }
    ]
}

FAPI_All = {
    "versions": [
        FAPI_v2,
        FAPI_v3,
    ]
}

fake_identity_version_single = {
    'versions': {
        'values': [
            {
                "status": "stable",
                "updated": "2013-03-06T00:00:00Z",
                "media-types": [
                    {
                        "base": "application/json",
                        "type": "application/vnd.openstack.identity-v3+json"
                    },
                    {
                        "base": "application/xml",
                        "type": "application/vnd.openstack.identity-v3+xml"
                    }
                ],
                "id": "v3.0",
                "links": [
                    {
                        "href": "http://10.130.50.11:5000/v3/",
                        "rel": "self"
                    }
                ]
            }
        ]
    }
}

FAKE_API_VERSIONS = {
    '2.0': 'fake.identity.client.ClientV2',
    '2.1': 'fake.identity.client.ClientV2_1',
    '3': 'fake.identity.client.ClientV3',
}


class FakeResponse(requests.Response):
    def __init__(self, headers={}, status_code=None, data=None, encoding=None):
        super(FakeResponse, self).__init__()

        self.status_code = status_code

        self.headers.update(headers)
        self._content = json.dumps(data)


class TestRESTApi(utils.TestCase):

    def setUp(self):
        super(TestRESTApi, self).setUp()

    def get_versions(self, smock, url):
        vlist = api_discovery.BaseVersion(
            session=smock,
            clients=FAKE_API_VERSIONS.keys(),
            auth_url=url,
            strict=True,
        )

        smock.get.assert_called_with(url)
        self.assertNotEqual(vlist.client_version.id, "")

    def test_request_strict(self):
        resp = FakeResponse(
            status_code=200,
            data=FAPI_All,
        )
        session_mock = mock.MagicMock(
            get=mock.MagicMock(return_value=resp),
        )

        self.get_versions(
            session_mock,
            "http://keystone:5000",
        )
        self.get_versions(
            session_mock,
            "http://keystone:5000/v2.0",
        )
        self.get_versions(
            session_mock,
            "http://keystone:5000/v3",
        )
