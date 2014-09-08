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

from keystoneclient.openstack.common.apiclient \
    import exceptions as ksc_exceptions


class BaseAPI(object):
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

        super(BaseAPI, self).__init__()

        # a requests.Session-style interface
        self.session = session
        self.service_type = service_type
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
        ret = session.request(url, method, **kwargs)
        return ret

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
            pass
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
        url,
        session=None,
        body=None,
        **params
    ):
        """Return a list of resources

        :param string url:
            The API-specific portion of the URL path
        :param Session session:
            HTTP client session
        :param body: data that will be encoded as JSON and passed in POST
            request (GET will be sent by default)
        """

        if body:
            return self._request(
                'POST',
                url,
                # service=self.service_type,
                json=body,
                params=params,
            ).json()
        else:
            return self._request(
                'GET',
                url,
                # service=self.service_type,
                params=params,
            ).json()

    # Layered actions built on top of the basic action methods do not
    # explicitly take a Session but may still be passed on kwargs

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
        :returns: list of resource dicts
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
        url,
        attr=None,
        search=None,
    ):
        """Find a single resource by name or ID

        :param string url:
            The API-specific portion of the URL path
        :param attr: name of attribute for secondary search
        :param search: search expression
        """

        try:
            ret = self._request('GET', "/%s/%s" % (url, search)).json()
        except ksc_exceptions.NotFound:
            kwargs = {attr: search}
            try:
                ret = self.find_one("/%s/detail" % (url), **kwargs)
            except ksc_exceptions.NotFound:
                msg = "%s not found" % search
                raise ksc_exceptions.NotFound(msg)

        return ret
