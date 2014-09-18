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

"""Base API Library"""

import simplejson as json

from six.moves.urllib import parse as urlparse

from keystoneclient.openstack.common.apiclient \
    import exceptions as ksc_exceptions
from openstackclient.common import exceptions


class KeystoneSession(object):
    """Wrapper for the Keystone Session

    Restore some requests.session.Session compatibility
    """

    def __init__(
        self,
        session=None,
        endpoint=None,
        **kwargs
    ):
        """Base object that contains some common API objects and methods

        :param Session session:
            The default session to be used for making the HTTP API calls.
        :param string endpoint:
            The URL from the Service Catalog to be used as the base for API
            requests on this API.
        """

        super(KeystoneSession, self).__init__()

        # a requests.Session-style interface
        self.session = session
        self.endpoint = endpoint

        if self.endpoint is None:
            # TODO(dtroyer): look it up via session
            pass

    def _request(self, method, url, session=None, **kwargs):
        """Perform call into session

        All API calls are funneled through this method to provide a common
        place to finalize the passed URL and other things.

        :param string method:
            The HTTP method name, i.e. ``GET``, ``PUT``, etc
        :param string url:
            The API-specific portion of the URL path
        :param Session session:
            HTTP client session
        :param kwargs:
            keyword arguments passed to requests.request().
        :return: the requests.Response object
        """

        if not session:
            session = self.session
        if not session:
            # TODO(dtroyer): sort this
            raise Exception

        if self.endpoint:
            url = '/'.join([self.endpoint.rstrip('/'), url.lstrip('/')])

        # Why is ksc session backwards???
        return session.request(url, method, **kwargs)


class BaseAPI(KeystoneSession):
    """Base API"""

    def __init__(
        self,
        session=None,
        service_type=None,
        endpoint=None,
        **kwargs
    ):
        """Base object that contains some common API objects and methods

        :param Session session:
            The default session to be used for making the HTTP API calls.
        :param string service_type:
            API name, i.e. ``identity`` or ``compute``
        :param string endpoint:
            The URL from the Service Catalog to be used as the base for API
            requests on this API.
        """

        super(BaseAPI, self).__init__(session=session, endpoint=endpoint)

        self.service_type = service_type

    # The basic action methods all take a Session and return dict/lists

    def create(
        self,
        url,
        session=None,
        method=None,
        **params
    ):
        """Create a new resource

        :param string url:
            The API-specific portion of the URL path
        :param Session session:
            HTTP client session
        :param string method:
            HTTP method (default POST)
        """

        if not method:
            method = 'POST'
        ret = self._request(method, url, session=session, **params)
        # Should this move into _requests()?
        try:
            return ret.json()
        except json.JSONDecodeError:
            return ret

    def delete(
        self,
        url,
        session=None,
        **params
    ):
        """Delete a resource

        :param string url:
            The API-specific portion of the URL path
        :param Session session:
            HTTP client session
        """

        return self._request('DELETE', url, **params)

    def list(
        self,
        path,
        session=None,
        body=None,
        detailed=False,
        **params
    ):
        """Return a list of resources

        GET ${ENDPOINT}/${PATH}

        path is often the object's plural resource type

        :param string path:
            The API-specific portion of the URL path
        :param Session session:
            HTTP client session
        :param body: data that will be encoded as JSON and passed in POST
            request (GET will be sent by default)
        :param bool detailed:
            Adds '/details' to path for some APIs to return extended attributes
        :returns:
            JSON-decoded response, could be a list or a dict-wrapped-list
        """

        if detailed:
            path = '/'.join([path.rstrip('/'), 'details'])

        if body:
            ret = self._request(
                'POST',
                path,
                # service=self.service_type,
                json=body,
                params=params,
            )
        else:
            ret = self._request(
                'GET',
                path,
                # service=self.service_type,
                params=params,
            )
        try:
            return ret.json()
        except json.JSONDecodeError:
            return ret

    # Layered actions built on top of the basic action methods do not
    # explicitly take a Session but may still be passed on kwargs

    def find_attr(
        self,
        path,
        value=None,
        attr=None,
        resource=None,
    ):
        """Find a resource via attribute or ID

        Most APIs return a list wrapped by a dict with the resource
        name as key.  Some APIs (Identity) return a dict when a query
        string is present and there is one return value.  Take steps to
        unwrap these bodies and return a single dict without any resource
        wrappers.

        :param string value:
            value to search for
        :param string attr:
            attribute to use for resource search
        :param string resource:
            plural of the object resource name; defaults to path
        For example:
            n = find(netclient, 'network', 'networks', 'matrix')
        """

        # Default attr is 'name'
        if attr is None:
            attr = 'name'

        # Default resource is path - in many APIs they are the same
        if resource is None:
            resource = path

        def getlist(kw):
            """Do list call, unwrap resource dict if present"""
            ret = self.list(path, **kw)
            if type(ret) == dict and resource in ret:
                ret = ret[resource]
            return ret

        # Search by attribute
        kwargs = {attr: value}
        data = getlist(kwargs)
        if type(data) == dict:
            return data
        if len(data) == 1:
            return data[0]
        if len(data) > 1:
            msg = "Multiple %s exist with %s='%s'"
            raise ksc_exceptions.CommandError(
                msg % (resource, attr, value),
            )

        # Search by id
        kwargs = {'id': value}
        data = getlist(kwargs)
        if len(data) == 1:
            return data[0]
        msg = "No %s with a %s or ID of '%s' found"
        raise exceptions.CommandError(msg % (resource, attr, value))

    def find_bulk(
        self,
        url,
        **kwargs
    ):
        """Bulk load and filter locally

        :param string url:
            The API-specific portion of the URL path
        :param kwargs: dict of AVPs to match - logical AND
        :returns: list of resource dicts
        """

        items = self.list(url)
        if type(items) == dict:
            # strip off the enclosing dict
            key = list(items.keys())[0]
            items = items[key]

        ret = []
        for o in items:
            try:
                if all(o[attr] == kwargs[attr] for attr in kwargs.keys()):
                    ret.append(o)
            except KeyError:
                continue

        return ret

    def find_one(
        self,
        url,
        **kwargs
    ):
        """Find a resource by name or ID

        :param string url:
            The API-specific portion of the URL path
        :returns:
            resource dict
        """

        bulk_list = self.find_bulk(url, **kwargs)
        num_bulk = len(bulk_list)
        if num_bulk == 0:
            msg = "none found"
            raise ksc_exceptions.NotFound(msg)
        elif num_bulk > 1:
            msg = "many found"
            raise RuntimeError(msg)
        return bulk_list[0]

    def find(
        self,
        path,
        value=None,
        attr=None,
    ):
        """Find a single resource by name or ID

        :param string url:
            The API-specific portion of the URL path
        :param string search:
            search expression
        :param string attr:
            name of attribute for secondary search
        """

        try:
            ret = self._request('GET', "/%s/%s" % (path, value)).json()
        except ksc_exceptions.NotFound:
            kwargs = {attr: value}
            try:
                ret = self.find_one("/%s/detail" % (path), **kwargs)
            except ksc_exceptions.NotFound:
                msg = "%s not found" % value
                raise ksc_exceptions.NotFound(msg)

        return ret


class BaseAPIVersion(KeystoneSession):
    """Base API version discovery"""

    def query_server_root(self):
        """Perform the version string retrieval

        Override this to make API-specific adjustments such
        as stripping version strings out of URLs, etc

        Compute /:
        {"versions": [ {}, {}, ] }

        Returns a list of server version dicts from the configured endpoint
        """
        try:
            resp = self._request('GET', '/').json()
        except Exception as e:  # requests.ConnectionError:
            resp = {}
            # TODO(dtroyer): sort out right exception here
            raise e

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

    def server_versions(
            self,
            url_host_hack=False,
    ):
        """Query REST server for supported API versions

        If url_host_hack is True the passed in URL is stripped to
        scheme://host:port/ to query the root of the REST server to get
        available API versions.

        [ {
            'id': '<id-from-server>',
            'status': '<api-status>',
            'url': '<endpoint>',
            'version': (<major>, <minor>),
        } ]
        """

        version_list = self.query_server_root()
        for v in version_list:
            ver_url = None
            for link in v['links']:
                if link['rel'] == 'self':
                    ver_url = link['href']
                    break

            if url_host_hack and ver_url:
                # break down api_url
                v_u = urlparse.urlparse(ver_url)
                a_u = urlparse.urlparse(self._api_url)
                # from url: scheme, netloc
                # from api_url: path, query (basically, the rest)
                if v_u.netloc.startswith('localhost'):
                    # Only hack this if it is the default setting
                    ver_url = urlparse.urlunparse((
                        a_u.scheme,
                        a_u.netloc,
                        v_u.path,
                        v_u.params,
                        v_u.query,
                        v_u.fragment,
                    ))
            v['url'] = ver_url
            v.pop('links')
            v['version'] = self.make_version_tuple(v['id'])

        return version_list

    def normalize_version(self, ver_str):
        """Strip non-numerics from version string"""
        if ver_str is not None:
            return ''.join(i for i in ver_str if i.isdigit() or i == '.')
        else:
            return ''

    def make_version_tuple(self, ver_str):
        """Create a version tuple (major, minor) from a string

        The version string may have non-numeric in it, they will be stripped
        and the version computed from the remainder.

        Version strings without a dot ('.') will be interpreted simply
        as a major version and the minor version will be zero.
        """

        if ver_str is not None and ver_str != '':
            ver = [int(i) for i in self.normalize_version(ver_str).split('.')]
            try:
                version = (ver[0], ver[1])
            except IndexError:
                # Handle a single version component (no '.')
                version = (ver[0], 0)
        else:
            version = ()

        return version
