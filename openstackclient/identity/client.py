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

import logging

from keystoneclient.v2_0 import client as identity_client_v2_0
from openstackclient.common import utils


LOG = logging.getLogger(__name__)

API_NAME = 'identity'
API_VERSIONS = {
    '2.0': 'openstackclient.identity.client.IdentityClientv2_0',
    '3': 'keystoneclient.v3.client.Client',
}


def make_client(instance):
    """Returns an identity service client."""
    if instance._url:
        LOG.debug('instantiating identity client: token flow')
        identity_client = utils.get_client_class(
            API_NAME,
            instance._api_version[API_NAME],
            API_VERSIONS)
        client = identity_client(
            endpoint=instance._url,
            token=instance._token)
    else:
        LOG.debug('instantiating identity client: password flow')
        server_versions = api_utils.get_server_versions(
            API_NAME,
            instance._auth_url,
        )

        client_versions = api_utils.get_client_versions(
            API_NAME,
            API_VERSIONS,
            instance._api_version[API_NAME],
        )

        (s_version, c_version) = api_utils.match_versions(
            server_versions,
            client_versions,
        )
        if not s_version and not c_version:
            # We're at the top level exception-handler-wise, be nice and exit
            LOG.debug("Identity server versions: %s" % server_versions)
            LOG.debug("Identity client versions: %s" % client_versions)
            raise SystemExit("ERROR: Identity API version negotiation failed")

        for link in s_version.links:
            if link['rel'] == 'self':
                instance._auth_url = link['href']
        print "using client %s (%s) for server %s: %s" % (
            c_version.id,
            c_version.class_name,
            s_version.id,
            instance._auth_url,
        )

        # Save the selected client version
        instance._api_version[API_NAME] = c_version.id

        identity_client = utils.get_client_class(
            API_NAME,
            instance._api_version[API_NAME],
            API_VERSIONS)
        client = identity_client(
            username=instance._username,
            password=instance._password,
            tenant_name=instance._project_name,
            tenant_id=instance._project_id,
            auth_url=instance._auth_url,
            region_name=instance._region_name)
    return client


class IdentityClientv2_0(identity_client_v2_0.Client):
    """Tweak the earlier client class to deal with some changes"""
    def __getattr__(self, name):
        # Map v3 'projects' back to v2 'tenants'
        if name == "projects":
            return self.tenants
        else:
            raise AttributeError, name
