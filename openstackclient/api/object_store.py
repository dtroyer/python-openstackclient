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

"""Object Store v1 API Library"""

import six

try:
    from urllib.parse import urlparse  # noqa
except ImportError:
    from urlparse import urlparse  # noqa

from openstackclient.api import api


class APIv1(api.BaseAPI):
    """Object Store v1 API"""

    def __init__(self, **kwargs):
        super(APIv1, self).__init__(**kwargs)

    def container_create(
        self,
        container=None,
    ):
        """Create a container

        :param container: name of container to create
        :returns: dict of returned headers
        """

        response = self.create(container, method='PUT')
        url_parts = urlparse(self.endpoint)
        data = {
            'account': url_parts.path.split('/')[-1],
            'container': container,
            'x-trans-id': response.headers.get('x-trans-id', None),
        }

        return data

    def container_delete(
        self,
        container=None,
    ):
        """Delete a container

        :param container: name of container to delete
        """

        if container:
            self.delete(container)

    def container_list(
        self,
        all_data=False,
        marker=None,
        limit=None,
        end_marker=None,
        prefix=None,
        **params
    ):
        """Get containers in an account

        :param all_data: if True, return a full listing, else returns a max
                         of 10000 listings
        :param marker: marker query
        :param limit: limit query
        :param end_marker: end_marker query
        :param prefix: prefix query
        :returns: list of container names
        """

        params['format'] = 'json'

        if all_data:
            data = listing = self.container_list(
                marker=marker,
                limit=limit,
                end_marker=end_marker,
                prefix=prefix,
                **params
            )
            while listing:
                # TODO(dtroyer): How can we use name here instead?
                marker = listing[-1]['name']
                listing = self.container_list(
                    marker=marker,
                    limit=limit,
                    end_marker=end_marker,
                    prefix=prefix,
                    **params
                )
                if listing:
                    data.extend(listing)
            return data

        if marker:
            params['marker'] = marker
        if limit:
            params['limit'] = limit
        if end_marker:
            params['end_marker'] = end_marker
        if prefix:
            params['prefix'] = prefix

        return self.list('', **params)

    def container_show(
        self,
        session=None,
        container=None,
    ):
        """Get container details

        :param session: a requests.Session
        :param container: name of container to show
        :returns: dict of returned headers
        """

        if not session:
            session = self.session
        if not session:
            # TODO(dtroyer): sort this
            raise Exception

        response = self._request('HEAD', container)
        data = {
            'account': response.headers.get('x-container-meta-owner', None),
            'container': container,
            'object_count': response.headers.get(
                'x-container-object-count',
                None,
            ),
            'bytes_used': response.headers.get('x-container-bytes-used', None),
            'read_acl': response.headers.get('x-container-read', None),
            'write_acl': response.headers.get('x-container-write', None),
            'sync_to': response.headers.get('x-container-sync-to', None),
            'sync_key': response.headers.get('x-container-sync-key', None),
        }
        return data

    def object_create(
        self,
        container=None,
        object=object,
    ):
        """Create an object inside a container

        :param container: name of container to store object
        :param object: local path to object
        :returns: dict of returned headers
        """

        full_url = "%s/%s" % (container, object)
        response = self.create(full_url, method='PUT', data=open(object))
        url_parts = urlparse(self.endpoint)
        data = {
            'account': url_parts.path.split('/')[-1],
            'container': container,
            'object': object,
            'x-trans-id': response.headers.get('X-Trans-Id', None),
            'etag': response.headers.get('Etag', None),
        }

        return data

    def object_delete(
        self,
        container=None,
        object=None,
    ):
        """Delete an object from a container

        :param container: name of container that stores object
        :param object: name of object to delete
        """

        self.delete("%s/%s" % (container, object))

    def object_list(
        self,
        container=None,
        all_data=False,
        marker=None,
        limit=None,
        end_marker=None,
        delimiter=None,
        prefix=None,
        **params
    ):
        """List objects in a container

        :param container: container name to get a listing for
        :param all_data: if True, return a full listing, else returns a max
            of 10000 listings
        :param marker: marker query
        :param limit: limit query
        :param end_marker: marker query
        :param delimiter: string to delimit the queries on
        :param prefix: prefix query
        :returns: a tuple of (response headers, a list of objects) The response
            headers will be a dict and all header names will be lowercase.
        """

#         params['format'] = 'json'

        if all_data:
            data = listing = self.object_list(
                container=container,
                marker=marker,
                limit=limit,
                end_marker=end_marker,
                delimiter=delimiter,
                prefix=prefix,
                **params
            )
            while listing:
                if delimiter:
                    marker = listing[-1].get('name', listing[-1].get('subdir'))
                else:
                    marker = listing[-1]['name']
                listing = self.object_list(
                    container=container,
                    marker=marker,
                    limit=limit,
                    end_marker=end_marker,
                    delimiter=delimiter,
                    prefix=prefix,
                    **params
                )
                if listing:
                    data.extend(listing)
            return data

        params = {}
        if marker:
            params['marker'] = marker
        if limit:
            params['limit'] = limit
        if end_marker:
            params['end_marker'] = end_marker
        if delimiter:
            params['delimiter'] = delimiter
        if prefix:
            params['prefix'] = prefix

        return self.list(container, **params)

    def object_show(
        self,
        session=None,
        container=None,
        object=None,
    ):
        """Get object details

        :param session: a requests.Session
        :param container: container name for object to get
        :param object: name of object to get
        :returns: dict of object properties
        """

        if not session:
            session = self.session
        if not session:
            # TODO(dtroyer): sort this
            raise Exception

        response = self._request('HEAD', "%s/%s" % (container, object))
        data = {
            'account': response.headers.get('x-container-meta-owner', None),
            'container': container,
            'object': object,
            'content-type': response.headers.get('content-type', None),
        }
        if 'content-length' in response.headers:
            data['content-length'] = response.headers.get(
                'content-length',
                None,
            )
        if 'last-modified' in response.headers:
            data['last-modified'] = response.headers.get('last-modified', None)
        if 'etag' in response.headers:
            data['etag'] = response.headers.get('etag', None)
        if 'x-object-manifest' in response.headers:
            data['x-object-manifest'] = response.headers.get(
                'x-object-manifest', None)
        for key, value in six.iteritems(response.headers):
            if key.startswith('x-object-meta-'):
                data[key[len('x-object-meta-'):].lower()] = value
            elif key not in (
                    'content-type',
                    'content-length',
                    'last-modified',
                    'etag',
                    'date',
                    'x-object-manifest',
                    'x-container-meta-owner',
            ):
                data[key.lower()] = value

        return data
