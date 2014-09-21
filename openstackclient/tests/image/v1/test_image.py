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

import copy
import mock

from openstackclient.common import exceptions
from openstackclient.image.v1 import image
from openstackclient.tests import fakes
from openstackclient.tests.image.v1 import fakes as image_fakes


class TestImage(image_fakes.TestImagev1):

    def setUp(self):
        super(TestImage, self).setUp()

        # Get a shortcut to the ServerManager Mock
        self.images_mock = self.app.client_manager.image.images
        self.images_mock.reset_mock()


class TestImageCreate(TestImage):

    def setUp(self):
        super(TestImageCreate, self).setUp()

        self.images_mock.create.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(image_fakes.IMAGE),
            loaded=True,
        )
        # This is the return value for utils.find_resource()
        self.images_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(image_fakes.IMAGE),
            loaded=True,
        )
        self.images_mock.update.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(image_fakes.IMAGE),
            loaded=True,
        )

        # Get the command object to test
        self.cmd = image.CreateImage(self.app, None)

    def test_image_reserve_no_options(self):
        mock_exception = {
            'find.side_effect': exceptions.CommandError('x'),
            'get.side_effect': exceptions.CommandError('x'),
        }
        self.images_mock.configure_mock(**mock_exception)
        arglist = [
            image_fakes.image_name,
        ]
        verifylist = [
            ('container_format', image.DEFAULT_CONTAINER_FORMAT),
            ('disk_format', image.DEFAULT_DISK_FORMAT),
            ('name', image_fakes.image_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # ImageManager.create(name=, **)
        self.images_mock.create.assert_called_with(
            name=image_fakes.image_name,
            container_format=image.DEFAULT_CONTAINER_FORMAT,
            disk_format=image.DEFAULT_DISK_FORMAT,
            data=mock.ANY,
        )

        # Verify update() was not called, if it was show the args
        self.assertEqual(self.images_mock.update.call_args_list, [])

        self.assertEqual(image_fakes.IMAGE_columns, columns)
        self.assertEqual(image_fakes.IMAGE_data, data)

    def test_image_reserve_options(self):
        mock_exception = {
            'find.side_effect': exceptions.CommandError('x'),
            'get.side_effect': exceptions.CommandError('x'),
        }
        self.images_mock.configure_mock(**mock_exception)
        arglist = [
            '--container-format', 'ovf',
            '--disk-format', 'fs',
            '--min-disk', '10',
            '--min-ram', '4',
            '--protected',
            '--private',
            image_fakes.image_name,
        ]
        verifylist = [
            ('container_format', 'ovf'),
            ('disk_format', 'fs'),
            ('min_disk', 10),
            ('min_ram', 4),
            ('protected', True),
            ('unprotected', False),
            ('public', False),
            ('private', True),
            ('name', image_fakes.image_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # ImageManager.create(name=, **)
        self.images_mock.create.assert_called_with(
            name=image_fakes.image_name,
            container_format='ovf',
            disk_format='fs',
            min_disk=10,
            min_ram=4,
            protected=True,
            is_public=False,
            data=mock.ANY,
        )

        # Verify update() was not called, if it was show the args
        self.assertEqual(self.images_mock.update.call_args_list, [])

        self.assertEqual(image_fakes.IMAGE_columns, columns)
        self.assertEqual(image_fakes.IMAGE_data, data)

    @mock.patch('six.moves.builtins.open')
    def test_image_create_file(self, open_mock):
        mock_exception = {
            'find.side_effect': exceptions.CommandError('x'),
            'get.side_effect': exceptions.CommandError('x'),
        }
        self.images_mock.configure_mock(**mock_exception)
        open_mock.return_value = image_fakes.image_data
        arglist = [
            '--file', 'filer',
            '--unprotected',
            '--public',
            '--property', 'Alpha=1',
            '--property', 'Beta=2',
            image_fakes.image_name,
        ]
        verifylist = [
            ('file', 'filer'),
            ('protected', False),
            ('unprotected', True),
            ('public', True),
            ('private', False),
            ('properties', {'Alpha': '1', 'Beta': '2'}),
            ('name', image_fakes.image_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        open_mock.assert_called_with('filer', 'rb')

        # ImageManager.get(name)
        self.images_mock.get.assert_called_with(image_fakes.image_name)

        # ImageManager.create(name=, **)
        self.images_mock.create.assert_called_with(
            name=image_fakes.image_name,
            container_format=image.DEFAULT_CONTAINER_FORMAT,
            disk_format=image.DEFAULT_DISK_FORMAT,
            protected=False,
            is_public=True,
            properties={
                'Alpha': '1',
                'Beta': '2',
            },
            data=image_fakes.image_data,
        )

        # Verify update() was not called, if it was show the args
        self.assertEqual(self.images_mock.update.call_args_list, [])

        self.assertEqual(image_fakes.IMAGE_columns, columns)
        self.assertEqual(image_fakes.IMAGE_data, data)

    def test_image_create_volume(self):
        # Set up VolumeManager Mock
        volumes_mock = self.app.client_manager.volume.volumes
        volumes_mock.reset_mock()
        volumes_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy({'id': 'vol1', 'name': 'volly'}),
            loaded=True,
        )
        response = {
            "id": 'volume_id',
            "updated_at": 'updated_at',
            "status": 'uploading',
            "display_description": 'desc',
            "size": 'size',
            "volume_type": 'volume_type',
            "image_id": 'image1',
            "container_format": image.DEFAULT_CONTAINER_FORMAT,
            "disk_format": image.DEFAULT_DISK_FORMAT,
            "image_name": image_fakes.image_name,
        }
        full_response = {"os-volume_upload_image": response}
        volumes_mock.upload_to_image.return_value = (201, full_response)

        arglist = [
            '--volume', 'volly',
            image_fakes.image_name,
        ]
        verifylist = [
            ('private', False),
            ('protected', False),
            ('public', False),
            ('unprotected', False),
            ('volume', 'volly'),
            ('force', False),
            ('name', image_fakes.image_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # VolumeManager.upload_to_image(volume, force, image_name,
        #     container_format, disk_format)
        volumes_mock.upload_to_image.assert_called_with(
            'vol1',
            False,
            image_fakes.image_name,
            'bare',
            'raw',
        )

        # ImageManager.update(image_id, remove_props=, **)
        self.images_mock.update.assert_called_with(
            image_fakes.image_id,
            name=image_fakes.image_name,
            container_format=image.DEFAULT_CONTAINER_FORMAT,
            disk_format=image.DEFAULT_DISK_FORMAT,
            properties=image_fakes.image_properties,
            volume='volly',
        )

        self.assertEqual(image_fakes.IMAGE_columns, columns)
        self.assertEqual(image_fakes.IMAGE_data, data)


class TestImageDelete(TestImage):

    def setUp(self):
        super(TestImageDelete, self).setUp()

        # This is the return value for utils.find_resource()
        self.images_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(image_fakes.IMAGE),
            loaded=True,
        )
        self.images_mock.delete.return_value = None

        # Get the command object to test
        self.cmd = image.DeleteImage(self.app, None)

    def test_image_delete_no_options(self):
        arglist = [
            image_fakes.image_id,
        ]
        verifylist = [
            ('image', image_fakes.image_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        self.cmd.take_action(parsed_args)

        self.images_mock.delete.assert_called_with(
            image_fakes.image_id,
        )


class TestImageSet(TestImage):

    def setUp(self):
        super(TestImageSet, self).setUp()

        # This is the return value for utils.find_resource()
        self.images_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(image_fakes.IMAGE),
            loaded=True,
        )
        self.images_mock.update.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(image_fakes.IMAGE),
            loaded=True,
        )

        # Get the command object to test
        self.cmd = image.SetImage(self.app, None)

    def test_image_set_no_options(self):
        arglist = [
            image_fakes.image_name,
        ]
        verifylist = [
            ('image', image_fakes.image_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        self.cmd.take_action(parsed_args)

        # Verify update() was not called, if it was show the args
        self.assertEqual(self.images_mock.update.call_args_list, [])

    def test_image_set_options(self):
        arglist = [
            '--name', 'new-name',
            '--owner', 'new-owner',
            '--min-disk', '2',
            '--min-ram', '4',
            image_fakes.image_name,
        ]
        verifylist = [
            ('name', 'new-name'),
            ('owner', 'new-owner'),
            ('min_disk', 2),
            ('min_ram', 4),
            ('image', image_fakes.image_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        kwargs = {
            'name': 'new-name',
            'owner': 'new-owner',
            'min_disk': 2,
            'min_ram': 4,
        }
        # ImageManager.update(image, **kwargs)
        self.images_mock.update.assert_called_with(
            image_fakes.image_id,
            **kwargs
        )

        self.assertEqual(image_fakes.IMAGE_columns, columns)
        self.assertEqual(image_fakes.IMAGE_data, data)

    def test_image_set_bools1(self):
        arglist = [
            '--protected',
            '--private',
            image_fakes.image_name,
        ]
        verifylist = [
            ('protected', True),
            ('unprotected', False),
            ('public', False),
            ('private', True),
            ('image', image_fakes.image_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        self.cmd.take_action(parsed_args)

        kwargs = {
            'protected': True,
            'is_public': False,
        }
        # ImageManager.update(image, **kwargs)
        self.images_mock.update.assert_called_with(
            image_fakes.image_id,
            **kwargs
        )

    def test_image_set_bools2(self):
        arglist = [
            '--unprotected',
            '--public',
            image_fakes.image_name,
        ]
        verifylist = [
            ('protected', False),
            ('unprotected', True),
            ('public', True),
            ('private', False),
            ('image', image_fakes.image_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        self.cmd.take_action(parsed_args)

        kwargs = {
            'protected': False,
            'is_public': True,
        }
        # ImageManager.update(image, **kwargs)
        self.images_mock.update.assert_called_with(
            image_fakes.image_id,
            **kwargs
        )

    def test_image_set_properties(self):
        arglist = [
            '--property', 'Alpha=1',
            '--property', 'Beta=2',
            image_fakes.image_name,
        ]
        verifylist = [
            ('properties', {'Alpha': '1', 'Beta': '2'}),
            ('image', image_fakes.image_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        self.cmd.take_action(parsed_args)

        kwargs = {
            'properties': {
                'Alpha': '1',
                'Beta': '2',
                'Gamma': 'g',
            },
        }
        # ImageManager.update(image, **kwargs)
        self.images_mock.update.assert_called_with(
            image_fakes.image_id,
            **kwargs
        )


class TestImageList(TestImage):

    def setUp(self):
        super(TestImageList, self).setUp()

        self.api_mock = mock.Mock()
        self.api_mock.image_list.return_value = [
            copy.deepcopy(image_fakes.IMAGE),
        ]
        self.app.client_manager.image.api = self.api_mock

        # Get the command object to test
        self.cmd = image.ListImage(self.app, None)

    def test_image_list_long_option(self):
        arglist = [
            '--long',
        ]
        verifylist = [
            ('long', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)
        self.api_mock.image_list.assert_called_with()

        collist = ('ID', 'Name', 'Disk Format', 'Container Format',
                   'Size', 'Status')

        self.assertEqual(columns, collist)
        datalist = ((
            image_fakes.image_id,
            image_fakes.image_name,
            '',
            '',
            '',
            '',
        ), )
        self.assertEqual(datalist, tuple(data))
