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
from six.moves.urllib import parse as urlparse

from keystoneclient.v2_0 import client as identity_client_v2_0
from openstackclient.common import api_discovery
from openstackclient.common import utils


LOG = logging.getLogger(__name__)

DEFAULT_IDENTITY_API_VERSION = '3'
API_VERSION_OPTION = 'os_identity_api_version'
API_NAME = 'identity'
API_VERSIONS = {
    '2.0': 'openstackclient.identity.client.IdentityClientv2_0',
    '3': 'keystoneclient.v3.client.Client',
}


def make_client(instance):
    """Returns an identity service client."""

    LOG.debug('identity version discovery')
    ver = IdentityVersion(
        session=instance._restapi,
        clients=API_VERSIONS.keys(),
        requested_version=instance._api_version[API_NAME],
        auth_url=instance._auth_url,
        strict=False,
    )
    if not ver.server_version.id and not ver.client_version.id:
        # We're at the top level exception-handler-wise, be nice and exit
        raise SystemExit("ERROR: Identity API version negotiation failed")
    LOG.debug("Identity server versions: %s" % ver.server_version.id)
    LOG.debug("Identity client versions: %s" % ver.client_version.id)
    for link in ver.server_version.links:
        if link['rel'] == 'self':
            instance._auth_url = link['href']
    LOG.debug("using client %s (%s) for server %s: %s" % (
        ver.client_version.id,
        API_VERSIONS[ver.client_version.id],
        ver.server_version.id,
        instance._auth_url,
    ))
    # Save the selected client version
    instance._api_version[API_NAME] = ver.client_version.id

    identity_client = utils.get_client_class(
        API_NAME,
        ver.client_version.id,
        API_VERSIONS)
    if instance._url:
        LOG.debug(
            'instantiating identity client: %s token flow',
            identity_client,
        )
        client = identity_client(
            endpoint=instance._url,
            token=instance._token)
    else:
        LOG.debug(
            'instantiating identity client: %s password flow',
            identity_client,
        )
        client = identity_client(
            username=instance._username,
            password=instance._password,
            user_domain_id=instance._user_domain_id,
            user_domain_name=instance._user_domain_name,
            project_domain_id=instance._project_domain_id,
            project_domain_name=instance._project_domain_name,
            domain_id=instance._domain_id,
            domain_name=instance._domain_name,
            tenant_name=instance._project_name,
            tenant_id=instance._project_id,
            auth_url=instance._auth_url,
            region_name=instance._region_name,
            cacert=instance._cacert,
            insecure=instance._insecure,
        )
        instance.auth_ref = client.auth_ref
    return client


class IdentityClientv2_0(identity_client_v2_0.Client):
    """Tweak the earlier client class to deal with some changes"""
    def __getattr__(self, name):
        # Map v3 'projects' back to v2 'tenants'
        if name == "projects":
            return self.tenants
        else:
            raise AttributeError(name)


class IdentityVersion(api_discovery.BaseVersion):
    """Handle Identity^H^H^H^H^HKeystone anomalies"""

    def query_server(self):
        # Hack off '/v2.0' to do proper discovery with old auth URLs
        u = urlparse.urlparse(self.auth_url)
        if u.path.endswith('/'):
            # Dump any trailing seperator
            path = u.path[:-1]
        else:
            path = u.path
        if (not self.strict):
            # Hack out the old v2_0
            if (path.endswith('v2.0')):
                # Strip off the last path component
                path = '/'.join(path.split('/')[:-1])

        self.auth_url = "%s://%s%s" % (u.scheme, u.netloc, path)
        versions = super(IdentityVersion, self).query_server()

        # Adjust the returned dict to match the rest of the world
        if 'values' in versions:
            versions = versions['values']
        return versions
