#!/usr/bin/env python3
# Copyright 2019 Apex.AI, Inc.
# Copyright 2020 Christophe Bedard
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import contextlib
from io import StringIO
import os
import shutil
import tempfile
import unittest

from tracetools_analysis.loading import _inspect_input_path


class TestLoading(unittest.TestCase):

    def __init__(self, *args) -> None:
        super().__init__(
            *args,
        )

    def setUp(self):
        self.test_dir_path = tempfile.mkdtemp()

        # Create directory that contains a 'converted' file
        self.with_converted_file_dir = os.path.join(
            self.test_dir_path,
            'with_converted_file',
        )
        os.mkdir(self.with_converted_file_dir)
        self.converted_file_path = os.path.join(
            self.with_converted_file_dir,
            'converted',
        )
        open(self.converted_file_path, 'a').close()
        self.assertTrue(os.path.exists(self.converted_file_path))

        # Create directory that contains a file with another name that is not 'converted'
        self.without_converted_file_dir = os.path.join(
            self.test_dir_path,
            'without_converted_file',
        )
        os.mkdir(self.without_converted_file_dir)
        self.random_file_path = os.path.join(
            self.without_converted_file_dir,
            'a_file',
        )
        open(self.random_file_path, 'a').close()
        self.assertTrue(os.path.exists(self.random_file_path))

    def tearDown(self):
        shutil.rmtree(self.test_dir_path)

    def test_inspect_input_path(
        self,
        quiet: bool = False,
    ) -> None:
        # Should find converted file under directory
        file_path, create_file = _inspect_input_path(self.with_converted_file_dir, False, quiet)
        self.assertEqual(self.converted_file_path, file_path)
        self.assertFalse(create_file)
        # Should find it but set it to be re-created
        file_path, create_file = _inspect_input_path(self.with_converted_file_dir, True, quiet)
        self.assertEqual(self.converted_file_path, file_path)
        self.assertTrue(create_file)

        # Should fail to find converted file under directory
        file_path, create_file = _inspect_input_path(self.without_converted_file_dir, False, quiet)
        self.assertIsNone(file_path)
        self.assertFalse(create_file)
        file_path, create_file = _inspect_input_path(self.without_converted_file_dir, True, quiet)
        self.assertIsNone(file_path)
        self.assertFalse(create_file)

        # Should accept any file path if it exists
        file_path, create_file = _inspect_input_path(self.random_file_path, False, quiet)
        self.assertEqual(self.random_file_path, file_path)
        self.assertFalse(create_file)
        # Should set it to be re-created
        file_path, create_file = _inspect_input_path(self.random_file_path, True, quiet)
        self.assertEqual(self.random_file_path, file_path)
        self.assertTrue(create_file)

        # TODO try with a trace directory

    def test_inspect_input_path_quiet(self) -> None:
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            # Just run the other test again
            self.test_inspect_input_path(quiet=True)
        # Shouldn't be any output
        output = temp_stdout.getvalue()
        self.assertEqual(0, len(output), f'was not quiet: "{output}"')
