#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

# for exception...
import requests

from openstackclient.common import restapi as api_session


class BaseVersion(object):
    """Negotiate an API version with a server

    session
    strict
    Passes kwargs through to the session creation if no session
    is included.
    """

    api_name = "base"

    def __init__(
            self,
            session=None,
            clients=[],
            requested_version=None,
            auth_url=None,
            strict=True,
            **kwargs):

        if not session:
            self.session = api_session.Session(**kwargs)
        else:
            self.session = session
        self.auth_url = auth_url
        self.strict = strict

        server_versions = self.query_server_versions()

        client_versions = self.client_versions(
            api_versions=clients,
            requested_version=requested_version,
        )

        (self.server_version, self.client_version) = self.match_versions(
            server_versions,
            client_versions,
        )

    def client_versions(self, api_versions=[], requested_version=None):
        """Process the available client versions...override
        """
        #raise NotImplementedError()
        """Return a list of client versions

        :param api_name: the name of the API, e.g. 'compute', 'image', etc
        :param api_versions: a list of supported client versions
        :param requested_version: the requested API version
        :rtype: a list of ApiVersion resources available for use
        """
        if requested_version:
            client_versions = [ApiVersion(
                name=self.api_name,
                id=requested_version,
                status=None,
            )]
        else:
            client_versions = []
            for v in api_versions:
                client_versions.append(ApiVersion(
                    name=self.api_name,
                    id=v,
                    status=None,
                ))
        return client_versions

    def query_server(self):
        """Perform the version string retrieval

        Override this to make API-specific adjustments such
        as stripping version strings out of URLs, etc
        """
        try:
            resp = self.session.get(self.auth_url).json()
        except requests.HTTPError:
            resp = {}

        if 'version' in resp:
            # We only got one, make it a list
            versions = [resp['version']]
        else:
            if 'versions' in resp:
                versions = resp['versions']
            else:
                # Handle bad server response
                versions = []

        return versions

    def query_server_versions(self, url=None):
        """Query REST server for supported API versions

        The passed in URL is stripped to host:port to query the root
        of the REST server to get available API versions.

        Identity /:
        {"versions": {"values": [ {}, {}, ] } }

        Identity /v2.0 /v3:
        {"version": {} }

        Compute /:
        {"versions": [ {}, {}, ] }

        Set strict=False to allow the following transformations to the URL in
        an attempt to find a usable version:
        - strip off the last path component; This handles the old-style auth
          url that ends with a version.
        - strip off the entire path; When the Identity API has not been
          relocated to a non-root URL this will get the entire list of
          supported versions.

        :param api_name: the name of the API, e.g. 'compute', 'image', etc
        :param url: the URL to query
        :param strict: allows munging on the url to find a version when False
        :rtype: a list of ApiVersion resources available on the server
        """

        # See what we can find
        if url:
            self.auth_url = url
        version_list = self.query_server()

        server_versions = []
        for v in version_list:
            server_versions.append(ApiVersion(
                name=self.api_name,
                url=self.auth_url,
                **v
            ))
        return server_versions

    def match_versions(self, server_list, client_list):
        """Match the highest client and server versions available

        Returns the matching server and client ApiVersion objects

        :param server_list: list of server ApiVersion objects
        :param client_list: list of client ApiVersion objects
        :rtype: a tuple of matching server and client ApiVersion objects,
                (None, None) if no match
        """
        # Build some dicts with normalized version strings for key
        slist = {s.key: s for s in server_list}
        clist = {c.key: c for c in client_list}

        # Loop through client and server versions highest first
        for ckey in sorted(clist.keys(), reverse=True):
            cver = clist[ckey].version_list()
            for skey in sorted(slist.keys(), reverse=True):
                sver = slist[skey].version_list()
                # Check for major version match
                if cver[0] == sver[0]:
                    # Check that client minor is <= server minor
                    if cver[1] <= sver[1]:
                        return (slist[skey], clist[ckey])

        # No match, sad panda
        return (None, None)


class ApiVersion(object):
    """Represent an API version

    :param name: API type name, i.e. 'identity', 'compute', etc.
    :param id: API version, i.e. '2.0', '3', etc.
    :param status: API status, i.e. 'stable', 'deprecated', etc
    :param class_name: The name of the client class for this version
    """
    def __init__(self, length=3, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        self._data = kwargs
        self.length = length
        self.id = self._normal(self.id)

    def __repr__(self):
        if hasattr(self, 'class_name'):
            return "<%s %s %s %s=%s>" % (
                self.__class__.__name__,
                self.name,
                self.id,
                self.status,
                self.class_name,
            )
        else:
            return "<%s %s %s %s>" % (
                self.__class__.__name__,
                self.name,
                self.id,
                self.status,
            )

    def __eq__(self, other):
        return self.key == other.key and self.status == other.status

    def _normal(self, version):
        # Dump the leading 'v'
        try:
            version = version.lstrip('v')
        except AttributeError:
            pass
        return version

    def version_list(self):
        """Return the version as a list of N integers"""
        s = ''.join(i for i in self.id if i.isdigit() or i == '.')
        v = [int(i) for i in s.split('.')]
        while len(v) < self.length:
            v.append(0)
        return v[:self.length]

    @property
    def key(self):
        s = ""
        for v in self.version_list():
            s += "%03u" % v
        return s
