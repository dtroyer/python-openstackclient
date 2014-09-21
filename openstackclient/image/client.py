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

from glanceclient import exc as gc_exceptions
from glanceclient.v1 import client as gc_v1_client
from glanceclient.v1 import images as gc_v1_images
from openstackclient.common import utils


LOG = logging.getLogger(__name__)

DEFAULT_IMAGE_API_VERSION = '1'
API_VERSION_OPTION = 'os_image_api_version'
API_NAME = "image"
API_VERSIONS = {
    "1": "openstackclient.image.client.Client_v1",
    "2": "glanceclient.v2.client.Client",
}
API_VERSIONS_2 = {
    '1': 'openstackclient.api.image_v1.APIv1',
    '2': 'openstackclient.api.image_v2.APIv2',
}


def make_client(instance):
    """Returns an image service client."""
    image_client = utils.get_client_class(
        API_NAME,
        instance._api_version[API_NAME],
        API_VERSIONS)
    LOG.debug('Instantiating image client: %s', image_client)

    image_api = utils.get_client_class(
        API_NAME,
        instance._api_version[API_NAME],
        API_VERSIONS_2)
    LOG.debug('Instantiating image api: %s', image_api)

    if not instance._url:
        instance._url = instance.get_endpoint_for_service_type(API_NAME)

    client = image_client(
        instance._url,
        token=instance._token,
        cacert=instance._cacert,
        insecure=instance._insecure,
    )

    client.api = image_api(
        session=instance.session,
        service_type="image",
        endpoint=instance.get_endpoint_for_service_type(
            API_NAME,
            endpoint_type="public",
        )
    )

    return client


def build_option_parser(parser):
    """Hook to add global options"""
    parser.add_argument(
        '--os-image-api-version',
        metavar='<image-api-version>',
        default=utils.env(
            'OS_IMAGE_API_VERSION',
            default=DEFAULT_IMAGE_API_VERSION),
        help='Image API version, default=' +
             DEFAULT_IMAGE_API_VERSION +
             ' (Env: OS_IMAGE_API_VERSION)')
    return parser


# NOTE(dtroyer): glanceclient.v1.image.ImageManager() doesn't have a find()
#                method so add one here until the common client libs arrive
#                A similar subclass will be required for v2

class Client_v1(gc_v1_client.Client):
    """An image v1 client that uses ImageManager_v1"""

    def __init__(self, *args, **kwargs):
        super(Client_v1, self).__init__(*args, **kwargs)
        self.images = ImageManager_v1(getattr(self, 'http_client', self))


class ImageManager_v1(gc_v1_images.ImageManager):
    """Add find() and findall() to the ImageManager class"""

    def find(self, **kwargs):
        """Find a single item with attributes matching ``**kwargs``.

        This isn't very efficient: it loads the entire list then filters on
        the Python side.
        """
        rl = self.findall(**kwargs)
        num = len(rl)

        if num == 0:
            raise gc_exceptions.NotFound
        elif num > 1:
            raise gc_exceptions.NoUniqueMatch
        else:
            return rl[0]

    def findall(self, **kwargs):
        """Find all items with attributes matching ``**kwargs``.

        This isn't very efficient: it loads the entire list then filters on
        the Python side.
        """
        found = []
        searches = kwargs.items()

        for obj in self.list():
            try:
                if all(getattr(obj, attr) == value
                       for (attr, value) in searches):
                    found.append(obj)
            except AttributeError:
                continue

        return found
