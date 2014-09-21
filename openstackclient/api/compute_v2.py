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

"""Compute v2 API Library"""

from openstackclient.api import api


class APIv2(api.BaseAPI):
    """Compute v2 API"""

    def __init__(self, **kwargs):
        super(APIv2, self).__init__(**kwargs)

    # Flavors

    def flavor_create(
        self,
        name=None,
        ram=None,
        vcpus=None,
        disk=None,
        id=None,
        ephemeral=None,     # x
        swap=None,          # x
        rxtx_factor=None,   # x
        public=None,        # x
    ):
        """Create a new flavor

        http://developer.openstack.org/api-ref-compute-v2-ext.html#ext-os-flavormanage

        :param string name:
            Flavor name
        :param integer ram:
            RAM size in Mb (server default is 256Mb)
        :param integer vcpus:
            Number of virtual CPUs (server default is 1)
        :param integer disk:
            Disk space in Gb (server default is 0)
        :param string id:
            Flavor ID (API ref says unique integer, server default is UUID)

        http://developer.openstack.org/api-ref-compute-v2-ext.html#ext-os-flavorextradata

        :param integer ephemeral:
            Ephemeral disk size in Gb
        :param integer swap:
            Swap size in Gb
        :param real rxtx_factor:
            Bandwidth cap modifier

        http://developer.openstack.org/api-ref-compute-v2-ext.html#ext-os-flavor-access

        :param boolean public:
            Make flavor public
        """

        def _make_int_str(var, min=0):
            """Convert var to string, ensure is an integer >= min"""
            if var is None:
                var = min
            try:
                var = int(var)
            except (TypeError, ValueError) as e:
                raise e
            if var < min:
                var = min
            return str(var)

        params = {
            'name': name,
            'ram': _make_int_str(ram, min=1),
            'vcpus': _make_int_str(vcpus, min=1),
            'disk': _make_int_str(disk),
            'OS-FLV-EXT-DATA:ephemeral': _make_int_str(ephemeral),
            'swap': _make_int_str(swap),
            'rxtx_factor': _make_int_str(rxtx_factor),
        }

        if id == 'auto':
            params['id'] = None
        if public is not None:
            params['os-flavor-access:is_public'] = str(bool(public))

        return self.create('/flavors', json={'flavor': params})['flavor']

    def flavor_delete(
        self,
        flavor=None,
    ):
        """Delete a flavor

        http://developer.openstack.org/api-ref-compute-v2-ext.html#ext-os-flavormanage

        :param string name:
            Flavor name or ID
        """

        flavor = self.find("flavors", 'name', flavor)
        if flavor is not None:
            return self.delete('/flavors/%s' % flavor['id'])

        return None

    def flavor_list(
        self,
        detailed=True,
        public=True,
    ):
        """Get available flavors

        http://developer.openstack.org/api-ref-compute-v2.html#compute_flavors

        :param detailed:
            Retrieve detailed response from server if True

        http://developer.openstack.org/api-ref-compute-v2-ext.html#ext-os-flavor-access

        :param is_public:
            Return only public flavors if True
        """

        params = {}

        if not public:
            params['is_public'] = public

        url = "/flavors"
        if detailed:
            url += "/detail"

        return self.list(url, **params)['flavors']

    def flavor_show(
        self,
        flavor=None,
    ):
        """Get details of a flavor

        http://developer.openstack.org/api-ref-compute-v2.html#compute_flavors

        :param string flavor:
            Flavor name or ID to retrieve
        """

        return self.find("flavors", attr='name', value=flavor)

    # Keys (aka keypairs, except only the public keys are managed?)

    def key_list(
        self,
    ):
        """Get available keys

        This is an extension, look at loading it separately
        """

        # Each effin object has the 'keypair' wrapper...
        ret = []
        for k in self.list('os-keypairs')['keypairs']:
            ret.append(k['keypair'])

        return ret