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

import mock

from openstackclient.tests import fakes
from openstackclient.tests import utils
from openstackclient.tests.volume.v1 import fakes as volume_fakes


image_id = 'im1'
image_name = 'graven'
image_owner = 'baal'
image_protected = False
image_public = True
image_properties = {
    'Alpha': 'a',
    'Beta': 'b',
    'Gamma': 'g',
}
image_properties_str = "{'Alpha': 'a', 'Beta': 'b', 'Gamma': 'g'}"
image_data = 'line 1\nline 2\n'

IMAGE = {
    'id': image_id,
    'name': image_name,
    'container_format': '',
    'disk_format': '',
    'owner': image_owner,
    'min_disk': 0,
    'min_ram': 0,
    'is_public': image_public,
    'protected': image_protected,
    'properties': image_properties,
}

IMAGE_columns = tuple(sorted(IMAGE))
IMAGE_data = tuple((IMAGE[x] for x in sorted(IMAGE)))


class FakeImagev2Client(object):
    def __init__(self, **kwargs):
        self.images = mock.Mock()
        self.images.resource_class = fakes.FakeResource(None, {})
        self.auth_token = kwargs['token']
        self.management_url = kwargs['endpoint']


class TestImagev2(utils.TestCommand):
    def setUp(self):
        super(TestImagev2, self).setUp()

        self.app.client_manager.image = FakeImagev2Client(
            endpoint=fakes.AUTH_URL,
            token=fakes.AUTH_TOKEN,
        )
        self.app.client_manager.volume = volume_fakes.FakeVolumev1Client(
            endpoint=fakes.AUTH_URL,
            token=fakes.AUTH_TOKEN,
        )
