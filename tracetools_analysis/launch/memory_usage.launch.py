# Copyright 2019 Robert Bosch GmbH
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

"""Example launch file for a memory_usage analysis."""

from launch import LaunchDescription
from launch_ros.actions import Node
from tracetools_launch.action import Trace
from tracetools_trace.tools.names import DEFAULT_EVENTS_ROS


def generate_launch_description():
    return LaunchDescription([
        Trace(
            session_name='memory-usage',
            events_ust=[
                'lttng_ust_libc:malloc',
                'lttng_ust_libc:calloc',
                'lttng_ust_libc:realloc',
                'lttng_ust_libc:free',
                'lttng_ust_libc:memalign',
                'lttng_ust_libc:posix_memalign',
            ] + DEFAULT_EVENTS_ROS,
            events_kernel=[
                'kmem_mm_page_alloc',
                'kmem_mm_page_free',
            ],
        ),
        Node(
            package='test_tracetools',
            executable='test_ping',
            arguments=['do_more'],
            output='screen',
        ),
        Node(
            package='test_tracetools',
            executable='test_pong',
            arguments=['do_more'],
            output='screen',
        ),
    ])
