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

"""Image v1 API Library"""

from openstackclient.api import api


class APIv1(api.BaseAPI):
    """Image v1 API"""

    def __init__(self, **kwargs):
        super(APIv1, self).__init__(**kwargs)

    def image_list(
        self,
        detailed=True,
        public=True,
    ):
        """Get available images

        can add limit/marker

        :param detailed:
            Retrieve detailed response from server if True
        :param is_public:
            Return only public flavors if True
        """

        params = {}

        if not public:
            params['is_public'] = public

        url = "/images"
        if detailed:
            url += "/detail"

        return self.list(url, **params)['images']
