# Copyright 2024 Apex.AI, Inc.
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

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from typing import Dict
from typing import List
from typing import Optional
import unittest

from launch import LaunchDescription
from launch import LaunchService
from launch_ros.actions import Node
from tracetools_trace.tools.lttng import is_lttng_installed


def are_tracepoints_included() -> bool:
    """
    Check if tracing instrumentation is enabled and if tracepoints are included.

    :return: True if tracepoints are included, False otherwise
    """
    if not is_lttng_installed():
        return False
    process = subprocess.run(
        ['ros2', 'run', 'tracetools', 'status'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding='utf-8',
    )
    return 0 == process.returncode


@unittest.skipIf(not is_lttng_installed(minimum_version='2.9.0'), 'LTTng is required')
class TestROS2TraceAnalysisCLI(unittest.TestCase):

    def __init__(self, *args) -> None:
        super().__init__(
            *args,
        )

    def create_test_tmpdir(self, test_name: str) -> str:
        prefix = self.__class__.__name__ + '__' + test_name
        return tempfile.mkdtemp(prefix=prefix)

    def run_command(
        self,
        args: List[str],
        *,
        env: Optional[Dict[str, str]] = None,
    ) -> subprocess.Popen:
        print('=>running:', args)
        process_env = os.environ.copy()
        process_env['PYTHONUNBUFFERED'] = '1'
        if env:
            process_env.update(env)
        return subprocess.Popen(
            args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding='utf-8',
            env=process_env,
        )

    def wait_and_print_command_output(
        self,
        process: subprocess.Popen,
    ) -> int:
        stdout, stderr = process.communicate()
        stdout = stdout.strip(' \r\n\t')
        stderr = stderr.strip(' \r\n\t')
        print('=>stdout:\n' + stdout)
        print('=>stderr:\n' + stderr)
        return process.wait()

    def run_command_and_wait(
        self,
        args: List[str],
        *,
        env: Optional[Dict[str, str]] = None,
    ) -> int:
        process = self.run_command(args, env=env)
        return self.wait_and_print_command_output(process)

    def run_nodes(self) -> None:
        nodes = [
            Node(
                package='test_tracetools',
                executable='test_ping',
                output='screen',
            ),
            Node(
                package='test_tracetools',
                executable='test_pong',
                output='screen',
            ),
        ]
        ld = LaunchDescription(nodes)
        ls = LaunchService()
        ls.include_launch_description(ld)
        exit_code = ls.run()
        self.assertEqual(0, exit_code)

    def test_process_bad_input_path(self) -> None:
        tmpdir = self.create_test_tmpdir('test_process_bad_input_path')

        # No input path
        ret = self.run_command_and_wait(['ros2', 'trace-analysis', 'process'])
        self.assertEqual(2, ret)

        # Does not exist
        ret = self.run_command_and_wait(['ros2', 'trace-analysis', 'process', ''])
        self.assertEqual(1, ret)
        fake_input = os.path.join(tmpdir, 'doesnt_exist')
        ret = self.run_command_and_wait(['ros2', 'trace-analysis', 'process', fake_input])
        self.assertEqual(1, ret)

        # Exists but empty
        empty_input = os.path.join(tmpdir, 'empty')
        os.mkdir(empty_input)
        ret = self.run_command_and_wait(['ros2', 'trace-analysis', 'process', empty_input])
        self.assertEqual(1, ret)

        # Exists but converted file empty
        empty_converted_file = os.path.join(empty_input, 'converted')
        Path(empty_converted_file).touch()
        ret = self.run_command_and_wait(['ros2', 'trace-analysis', 'process', empty_input])
        self.assertEqual(1, ret)

        shutil.rmtree(tmpdir)

    @unittest.skipIf(not are_tracepoints_included(), 'tracepoints are required')
    def test_process(self) -> None:
        tmpdir = self.create_test_tmpdir('test_process')
        session_name = 'test_process'

        # Run and trace nodes
        ret = self.run_command_and_wait(
            [
                'ros2', 'trace',
                'start', session_name,
                '--path', tmpdir,
            ],
        )
        self.assertEqual(0, ret)
        trace_dir = os.path.join(tmpdir, session_name)
        self.run_nodes()
        ret = self.run_command_and_wait(['ros2', 'trace', 'stop', session_name])
        self.assertEqual(0, ret)

        # Process trace
        ret = self.run_command_and_wait(['ros2', 'trace-analysis', 'process', trace_dir])
        self.assertEqual(0, ret)

        # Check that converted file exists and isn't empty
        converted_file = os.path.join(trace_dir, 'converted')
        self.assertTrue(os.path.isfile(converted_file))
        self.assertGreater(os.path.getsize(converted_file), 0)

        shutil.rmtree(tmpdir)
