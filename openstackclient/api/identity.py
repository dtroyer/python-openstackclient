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

"""Identity API Library"""

from six.moves.urllib import parse as urlparse

from openstackclient.api import api


class IdentityAPIVersion(api.BaseAPIVersion):
    """Identity API version discovery"""

    def query_server_root(
            self,
            strict=True,
    ):
        """Perform the version string retrieval

        Historically auth (Identity API) URL values given to users
        include '/v2.0' at the end, which only returns the version
        information for the V2 API.  If strict is True, the last
        component of the api URL path is removed if it is exactly 'v2.0'.

        Identity /:
        {"versions": {"values": [ {}, {}, ] } }

        Identity /v2.0 /v3:
        {"version": {} }
        """

        # Hack off '/v2.0' to do proper discovery with old auth URLs
        u = urlparse.urlparse(self.endpoint.rstrip('/'))
        path = u.path
        if not strict:
            # Hack out the old v2_0
                if path.endswith('v2.0'):
                    # Strip off the last path component
                    path = '/'.join(path.split('/')[:-1])

        self.endpoint = "%s://%s%s" % (u.scheme, u.netloc, path)
        resp = super(IdentityAPIVersion, self).query_server_root()

        # Adjust the returned dict to match the rest of the world
        if 'values' in resp:
            resp = resp['values']

        # We have to re-do this because of Identity's 'values' problem above
        # but also take in to account some other non-standard variations
        if 'version' in resp:
            # We only got one, make it a list
            versions = resp['version']
            if type(versions) != list:
                versions = [versions]
        else:
            if 'versions' in resp:
                versions = resp['versions']
            else:
                # Nothing to see here, move along
                versions = resp

        return versions
