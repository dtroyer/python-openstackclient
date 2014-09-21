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

"""Identity v3 API Library"""

from openstackclient.api import api


class APIv3(api.BaseAPI):
    """Identity v3 API"""

    def __init__(self, **kwargs):
        super(APIv3, self).__init__(**kwargs)

    def find_domain(self, domain):
        """Find domain by name or id"""
        return self.find('domain', attr='name', search=domain)['domain']

    def project_list(
        self,
        **params
    ):
        """Get available projects

        can add limit/marker
        need to convert to v3...
        """

        return self.list('projects')['projects']
