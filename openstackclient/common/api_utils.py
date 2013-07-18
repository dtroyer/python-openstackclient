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

"""API client utilities"""

import urlparse

from openstackclient.common import http_utils


def get_client_versions(api_name, api_versions={}, requested_version=None):
    """Return a list of client versions

    :param api_name: the name of the API, e.g. 'compute', 'image', etc
    :param api_versions: a dict of client classes keyed by version
    :param requested_version: the requested API version
    :rtype: a list of ApiVersion resources available for use
    """
    if requested_version:
        client_versions = [ApiVersion(
            name=api_name,
            id=requested_version,
            class_name='',
        )]
    else:
        client_versions = []
        for v in api_versions:
            client_versions.append(ApiVersion(
                name=api_name,
                id=v,
                class_name=api_versions[v],
            ))
    return client_versions


def get_server_versions(api_name, url):
    """Query REST server for supported API versions

    The passed in URL is stripped to host:port to query the root
    of the REST server to get available API versions.

    :param api_name: the name of the API, e.g. 'compute', 'image', etc
    :param url: the URL to query
    :rtype: a list of ApiVersion resources available on the server
    """
    u = urlparse.urlparse(url)
    resp = http_utils.request('GET', "%s://%s/" % (u.scheme, u.netloc)).json()

    if 'versions' not in resp:
        # Handle bad server response
        return []

    # Handle Identity^H^H^H^H^HKeystone anomaly
    if 'values' in resp['versions']:
        versions = resp['versions']['values']
    else:
        versions = resp['versions']

    server_versions = []
    for v in versions:
        server_versions.append(ApiVersion(
            name=api_name,
            **v
        ))
    return server_versions


def match_versions(server_list, client_list):
    """Match the highest client and server versions available

    Returns the matching server and client ApiVersion objects

    :param server_list: list of server ApiVersion
    :param client_list: list of client ApiVersion
    :rtype: a tuple of server and client ApiVersion objects
    """
    # Build some dicts with normalized version strings for key
    slist = {s.key(): s for s in server_list}
    clist = {c.key(): c for c in client_list}

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
    """Represent an API version"""
    def __init__(self, length=3, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        self._data = kwargs
        self.length = length

    def __repr__(self):
        return "<%s %s %s>" % (self.__class__.__name__, self.name, self.id)

    def version_list(self):
        """Return the version as a list of N integers"""
        s = ''.join(i for i in self.id if i.isdigit() or i == '.')
        v = [int(i) for i in s.split('.')]
        while len(v) < self.length:
            v.append(0)
        return v[:self.length]

    def key(self):
        s = ""
        for v in self.version_list():
            s += "%03u" % v
        return s
