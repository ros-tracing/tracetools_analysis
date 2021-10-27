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

"""Example launch file for a profiling analysis."""

from launch import LaunchDescription
from launch_ros.actions import Node
from tracetools_launch.action import Trace
from tracetools_trace.tools.names import DEFAULT_CONTEXT
from tracetools_trace.tools.names import DEFAULT_EVENTS_ROS


def generate_launch_description():
    return LaunchDescription([
        Trace(
            session_name='profile',
            events_ust=[
                'lttng_ust_cyg_profile_fast:func_entry',
                'lttng_ust_cyg_profile_fast:func_exit',
                'lttng_ust_statedump:start',
                'lttng_ust_statedump:end',
                'lttng_ust_statedump:bin_info',
                'lttng_ust_statedump:build_id',
            ] + DEFAULT_EVENTS_ROS,
            events_kernel=[
                'sched_switch',
            ],
            context_fields={
                'kernel': DEFAULT_CONTEXT,
                'userspace': DEFAULT_CONTEXT + ['ip'],
            },
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
