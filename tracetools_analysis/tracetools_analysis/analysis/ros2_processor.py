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

"""Module for trace events processor and ROS model creation."""

from typing import Dict
from typing import List

from tracetools_read.utils import get_field

from .data_model import DataModel
from .handler import EventHandler
from .lttng_models import EventMetadata


class Ros2Processor(EventHandler):
    """
    ROS 2-aware event processing/handling class implementation.

    Handles a trace's events and builds a model with the data.
    """

    def __init__(self) -> None:
        # Link a ROS trace event to its corresponding handling method
        handler_map = {
            'ros2:rcl_init':
                self._handle_rcl_init,
            'ros2:rcl_node_init':
                self._handle_rcl_node_init,
            'ros2:rcl_publisher_init':
                self._handle_rcl_publisher_init,
            'ros2:rcl_subscription_init':
                self._handle_subscription_init,
            'ros2:rclcpp_subscription_callback_added':
                self._handle_rclcpp_subscription_callback_added,
            'ros2:rcl_service_init':
                self._handle_rcl_service_init,
            'ros2:rclcpp_service_callback_added':
                self._handle_rclcpp_service_callback_added,
            'ros2:rcl_client_init':
                self._handle_rcl_client_init,
            'ros2:rcl_timer_init':
                self._handle_rcl_timer_init,
            'ros2:rclcpp_timer_callback_added':
                self._handle_rclcpp_timer_callback_added,
            'ros2:rclcpp_callback_register':
                self._handle_rclcpp_callback_register,
            'ros2:callback_start':
                self._handle_callback_start,
            'ros2:callback_end':
                self._handle_callback_end,
        }
        super().__init__(handler_map)

        self._data = DataModel()

        # Temporary buffers
        self._callback_instances = {}

    def get_data_model(self) -> DataModel:
        return self._data

    def _handle_rcl_init(
        self, event: Dict, metadata: EventMetadata
    ) -> None:
        context_handle = get_field(event, 'context_handle')
        timestamp = metadata.timestamp
        pid = metadata.pid
        version = get_field(event, 'version')
        self._data.add_context(context_handle, timestamp, pid, version)

    def _handle_rcl_node_init(
        self, event: Dict, metadata: EventMetadata
    ) -> None:
        handle = get_field(event, 'node_handle')
        timestamp = metadata.timestamp
        tid = metadata.tid
        rmw_handle = get_field(event, 'rmw_handle')
        name = get_field(event, 'node_name')
        namespace = get_field(event, 'namespace')
        self._data.add_node(handle, timestamp, tid, rmw_handle, name, namespace)

    def _handle_rcl_publisher_init(
        self, event: Dict, metadata: EventMetadata
    ) -> None:
        handle = get_field(event, 'publisher_handle')
        timestamp = metadata.timestamp
        node_handle = get_field(event, 'node_handle')
        rmw_handle = get_field(event, 'rmw_publisher_handle')
        topic_name = get_field(event, 'topic_name')
        depth = get_field(event, 'queue_depth')
        self._data.add_publisher(handle, timestamp, node_handle, rmw_handle, topic_name, depth)

    def _handle_subscription_init(
        self, event: Dict, metadata: EventMetadata
    ) -> None:
        handle = get_field(event, 'subscription_handle')
        timestamp = metadata.timestamp
        node_handle = get_field(event, 'node_handle')
        rmw_handle = get_field(event, 'rmw_subscription_handle')
        topic_name = get_field(event, 'topic_name')
        depth = get_field(event, 'queue_depth')
        self._data.add_subscription(handle, timestamp, node_handle, rmw_handle, topic_name, depth)

    def _handle_rclcpp_subscription_callback_added(
        self, event: Dict, metadata: EventMetadata
    ) -> None:
        handle = get_field(event, 'subscription_handle')
        timestamp = metadata.timestamp
        callback_object = get_field(event, 'callback')
        self._data.add_callback_object(handle, timestamp, callback_object)

    def _handle_rcl_service_init(
        self, event: Dict, metadata: EventMetadata
    ) -> None:
        handle = get_field(event, 'service_handle')
        timestamp = metadata.timestamp
        node_handle = get_field(event, 'node_handle')
        rmw_handle = get_field(event, 'rmw_service_handle')
        service_name = get_field(event, 'service_name')
        self._data.add_service(handle, timestamp, node_handle, rmw_handle, service_name)

    def _handle_rclcpp_service_callback_added(
        self, event: Dict, metadata: EventMetadata
    ) -> None:
        handle = get_field(event, 'service_handle')
        timestamp = metadata.timestamp
        callback_object = get_field(event, 'callback')
        self._data.add_callback_object(handle, timestamp, callback_object)

    def _handle_rcl_client_init(
        self, event: Dict, metadata: EventMetadata
    ) -> None:
        handle = get_field(event, 'client_handle')
        timestamp = metadata.timestamp
        node_handle = get_field(event, 'node_handle')
        rmw_handle = get_field(event, 'rmw_client_handle')
        service_name = get_field(event, 'service_name')
        self._data.add_client(handle, timestamp, node_handle, rmw_handle, service_name)

    def _handle_rcl_timer_init(
        self, event: Dict, metadata: EventMetadata
    ) -> None:
        handle = get_field(event, 'timer_handle')
        timestamp = metadata.timestamp
        period = get_field(event, 'period')
        tid = metadata.tid
        self._data.add_timer(handle, timestamp, period, tid)

    def _handle_rclcpp_timer_callback_added(
        self, event: Dict, metadata: EventMetadata
    ) -> None:
        handle = get_field(event, 'timer_handle')
        timestamp = metadata.timestamp
        callback_object = get_field(event, 'callback')
        self._data.add_callback_object(handle, timestamp, callback_object)

    def _handle_rclcpp_callback_register(
        self, event: Dict, metadata: EventMetadata
    ) -> None:
        callback_object = get_field(event, 'callback')
        timestamp = metadata.timestamp
        symbol = get_field(event, 'symbol')
        self._data.add_callback_symbol(callback_object, timestamp, symbol)

    def _handle_callback_start(
        self, event: Dict, metadata: EventMetadata
    ) -> None:
        # Add to dict
        callback_addr = get_field(event, 'callback')
        self._callback_instances[callback_addr] = (event, metadata)

    def _handle_callback_end(
        self, event: Dict, metadata: EventMetadata
    ) -> None:
        # Fetch from dict
        callback_object = get_field(event, 'callback')
        (event_start, metadata_start) = self._callback_instances.get(callback_object)
        if event_start is not None and metadata_start is not None:
            del self._callback_instances[callback_object]
            duration = metadata.timestamp - metadata_start.timestamp
            is_intra_process = get_field(event_start, 'is_intra_process', raise_if_not_found=False)
            self._data.add_callback_instance(
                callback_object,
                metadata_start.timestamp,
                duration,
                bool(is_intra_process))
        else:
            print(f'No matching callback start for callback object "{callback_object}"')


def ros2_process(events: List[Dict[str, str]]) -> Ros2Processor:
    """
    Process unpickled events and create ROS 2 model.

    :param events: the list of events
    :return: the processor object
    """
    processor = Ros2Processor()
    processor.handle_events(events)
    return processor
