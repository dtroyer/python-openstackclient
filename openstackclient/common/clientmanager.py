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

"""Manage access to the clients, including authenticating when needed."""

import logging
import pkg_resources
import sys

from keystoneclient.auth.identity import v2 as v2_auth
from keystoneclient.auth.identity import v3 as v3_auth
from keystoneclient import session
from openstackclient.identity import client as identity_client


LOG = logging.getLogger(__name__)


class ClientCache(object):
    """Descriptor class for caching created client handles."""
    def __init__(self, factory):
        self.factory = factory
        self._handle = None

    def __get__(self, instance, owner):
        # Tell the ClientManager to login to keystone
        if self._handle is None:
            self._handle = self.factory(instance)
        return self._handle


class ClientManager(object):
    """Manages access to API clients, including authentication."""
    identity = ClientCache(identity_client.make_client)

    def __init__(self, cloud=None,
                 user_domain_id=None, user_domain_name=None,
                 project_domain_id=None, project_domain_name=None,
                 region_name=None, api_version=None, verify=True,
                 trust_id=None, timing=None):
        self.cloud = cloud
        self.service_token = getattr(cloud.config, 'service_token', None)
        self._url = getattr(cloud.config, 'service_url', None)  # deprecated
        self._auth_url = cloud.config['auth_url']       # _auth_url deprecated
        self._project_name = cloud.config['project_id']  # deprecated
        self._username = cloud.config['username']       # _username deprecated
        self._password = cloud.config['password']       # _password deprecated
        self._user_domain_id = user_domain_id
        self._user_domain_name = user_domain_name
        self._project_domain_id = project_domain_id
        self._project_domain_name = project_domain_name
        self._region_name = cloud.config['region_name']  # deprecated
        self._api_version = api_version
        self._trust_id = trust_id
        self._service_catalog = None
        self.timing = timing

        # verify is the Requests-compatible form
        self._verify = verify
        # also store in the form used by the legacy client libs
        self._cacert = None
        if verify is True or verify is False:
            self._insecure = not verify
        else:
            self._cacert = verify
            self._insecure = False

        ver_prefix = identity_client.AUTH_VERSIONS[
            self._api_version[identity_client.API_NAME]
        ]

        # Get logging from root logger
        root_logger = logging.getLogger('')
        LOG.setLevel(root_logger.getEffectiveLevel())

        # NOTE(dtroyer): These plugins are hard-coded for the first step
        #                in using the new Keystone auth plugins.

        if self.service_token:
            LOG.debug('Using token auth %s', ver_prefix)
            if ver_prefix == 'v2':
                self.auth = v2_auth.Token(
                    auth_url=self._url,
                    token=self.service_token,
                )
            else:
                self.auth = v3_auth.Token(
                    auth_url=self._url,
                    token=self.service_token,
                )
        else:
            LOG.debug('Using password auth %s', ver_prefix)
            if ver_prefix == 'v2':
                self.auth = v2_auth.Password(
                    auth_url=self.cloud.config['auth_url'],
                    username=self.cloud.config['username'],
                    password=self.cloud.config['password'],
                    tenant_name=self.cloud.config['project_id'],
                )
            else:
                self.auth = v3_auth.Password(
                    auth_url=self.cloud.config['auth_url'],
                    username=self.cloud.config['username'],
                    password=self.cloud.config['password'],
                    user_domain_id=user_domain_id,
                    user_domain_name=user_domain_name,
                    domain_name=self.cloud.config['domain'],
                    project_name=self.cloud.config['project_id'],
                    project_domain_id=project_domain_id,
                    project_domain_name=project_domain_name,
                )

        self.session = session.Session(
            auth=self.auth,
            verify=verify,
        )

        self.auth_ref = None
        if not self.service_token:
            # Trigger the auth call
            self.auth_ref = self.session.auth.get_auth_ref(self.session)
            # Populate other password flow attributes
            self.auth_token = self.session.auth.get_token(
                self.session,
            )
            self._service_catalog = self.auth_ref.service_catalog
        return

    def get_endpoint_for_service_type(self, service_type):
        """Return the endpoint URL for the service type."""
        # See if we are using password flow auth, i.e. we have a
        # service catalog to select endpoints from
        if self._service_catalog:
            endpoint = self._service_catalog.url_for(
                service_type=service_type)
        else:
            # Hope we were given the correct URL.
            endpoint = self.cloud.config['auth_url']
        return endpoint


def get_extension_modules(group):
    """Add extension clients"""
    mod_list = []
    for ep in pkg_resources.iter_entry_points(group):
        LOG.debug('found extension %r', ep.name)

        __import__(ep.module_name)
        module = sys.modules[ep.module_name]
        mod_list.append(module)
        init_func = getattr(module, 'Initialize', None)
        if init_func:
            init_func('x')

        setattr(
            ClientManager,
            module.API_NAME,
            ClientCache(
                getattr(sys.modules[ep.module_name], 'make_client', None)
            ),
        )
    return mod_list
