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

"""Identity v2 API Library"""

from openstackclient.api import api


class APIv2(api.BaseAPI):
    """Identity v2 API"""

    def __init__(self, **kwargs):
        super(APIv2, self).__init__(**kwargs)

    def project_list(
        self,
    ):
        """Get available projects

        can add limit/marker
        """

        return self.list('tenants')['tenants']

    def user_list(
        self,
        project=None,
        limit=None,
        marker=None,
    ):
        """Get available users

        can add limit/marker

        :param string project:
            Filter users by project
        :param integer limit:
            query return count limit
        :param string marker:
            query marker
        """

        params = {}
        if limit:
            params['limit'] = limit
        if marker:
            params['marker'] = marker

        if project is None:
            return self.list('users', **params)['users']
        else:
            return self.list('tenants/%s/users' % project, **params)['users']
