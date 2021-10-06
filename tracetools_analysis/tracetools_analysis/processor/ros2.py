# Copyright 2019 Robert Bosch GmbH
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

"""Module for trace events processor and ROS 2 model creation."""

from typing import Dict
from typing import Set
from typing import Tuple

from tracetools_read import get_field

from . import EventHandler
from . import EventMetadata
from . import HandlerMap
from ..data_model.ros2 import Ros2DataModel


class Ros2Handler(EventHandler):
    """
    ROS 2-aware event handling class implementation.

    Handles a trace's events and builds a model with the data.
    """

    def __init__(
        self,
        **kwargs,
    ) -> None:
        """Create a Ros2Handler."""
        # Link a ROS trace event to its corresponding handling method
        handler_map: HandlerMap = {
            'ros2:rcl_init':
                self._handle_rcl_init,
            'ros2:rcl_node_init':
                self._handle_rcl_node_init,
            'ros2:rmw_publisher_init':
                self._handle_rmw_publisher_init,
            'ros2:rcl_publisher_init':
                self._handle_rcl_publisher_init,
            'ros2:rclcpp_publish':
                self._handle_rclcpp_publish,
            'ros2:rcl_publish':
                self._handle_rcl_publish,
            'ros2:rmw_publish':
                self._handle_rmw_publish,
            'ros2:rmw_subscription_init':
                self._handle_rmw_subscription_init,
            'ros2:rcl_subscription_init':
                self._handle_rcl_subscription_init,
            'ros2:rclcpp_subscription_init':
                self._handle_rclcpp_subscription_init,
            'ros2:rclcpp_subscription_callback_added':
                self._handle_rclcpp_subscription_callback_added,
            'ros2:rmw_take':
                self._handle_rmw_take,
            'ros2:rcl_take':
                self._handle_rcl_take,
            'ros2:rclcpp_take':
                self._handle_rclcpp_take,
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
            'ros2:rclcpp_timer_link_node':
                self._handle_rclcpp_timer_link_node,
            'ros2:rclcpp_callback_register':
                self._handle_rclcpp_callback_register,
            'ros2:callback_start':
                self._handle_callback_start,
            'ros2:callback_end':
                self._handle_callback_end,
            'ros2:rcl_lifecycle_state_machine_init':
                self._handle_rcl_lifecycle_state_machine_init,
            'ros2:rcl_lifecycle_transition':
                self._handle_rcl_lifecycle_transition,
        }
        super().__init__(
            handler_map=handler_map,
            data_model=Ros2DataModel(),
            **kwargs,
        )

        # Temporary buffers
        self._callback_instances: Dict[int, Tuple[Dict, EventMetadata]] = {}

    @staticmethod
    def required_events() -> Set[str]:
        return {
            'ros2:rcl_init',
        }

    @property
    def data(self) -> Ros2DataModel:
        return super().data  # type: ignore

    def _handle_rcl_init(
        self, event: Dict, metadata: EventMetadata,
    ) -> None:
        context_handle = get_field(event, 'context_handle')
        timestamp = metadata.timestamp
        pid = metadata.pid
        version = get_field(event, 'version')
        self.data.add_context(context_handle, timestamp, pid, version)

    def _handle_rcl_node_init(
        self, event: Dict, metadata: EventMetadata,
    ) -> None:
        handle = get_field(event, 'node_handle')
        timestamp = metadata.timestamp
        tid = metadata.tid
        rmw_handle = get_field(event, 'rmw_handle')
        name = get_field(event, 'node_name')
        namespace = get_field(event, 'namespace')
        self.data.add_node(handle, timestamp, tid, rmw_handle, name, namespace)

    def _handle_rmw_publisher_init(
        self, event: Dict, metadata: EventMetadata,
    ) -> None:
        handle = get_field(event, 'rmw_publisher_handle')
        timestamp = metadata.timestamp
        gid = get_field(event, 'gid')
        self.data.add_rmw_publisher(handle, timestamp, gid)

    def _handle_rcl_publisher_init(
        self, event: Dict, metadata: EventMetadata,
    ) -> None:
        handle = get_field(event, 'publisher_handle')
        timestamp = metadata.timestamp
        node_handle = get_field(event, 'node_handle')
        rmw_handle = get_field(event, 'rmw_publisher_handle')
        topic_name = get_field(event, 'topic_name')
        depth = get_field(event, 'queue_depth')
        self.data.add_rcl_publisher(handle, timestamp, node_handle, rmw_handle, topic_name, depth)

    def _handle_rclcpp_publish(
        self, event: Dict, metadata: EventMetadata,
    ) -> None:
        timestamp = metadata.timestamp
        message = get_field(event, 'message')
        self.data.add_rclcpp_publish_instance(timestamp, message)

    def _handle_rcl_publish(
        self, event: Dict, metadata: EventMetadata,
    ) -> None:
        handle = get_field(event, 'publisher_handle')
        timestamp = metadata.timestamp
        message = get_field(event, 'message')
        self.data.add_rcl_publish_instance(handle, timestamp, message)

    def _handle_rmw_publish(
        self, event: Dict, metadata: EventMetadata,
    ) -> None:
        timestamp = metadata.timestamp
        message = get_field(event, 'message')
        self.data.add_rmw_publish_instance(timestamp, message)

    def _handle_rmw_subscription_init(
        self, event: Dict, metadata: EventMetadata,
    ) -> None:
        handle = get_field(event, 'rmw_subscription_handle')
        timestamp = metadata.timestamp
        gid = get_field(event, 'gid')
        self.data.add_rmw_subscription(handle, timestamp, gid)

    def _handle_rcl_subscription_init(
        self, event: Dict, metadata: EventMetadata,
    ) -> None:
        handle = get_field(event, 'subscription_handle')
        timestamp = metadata.timestamp
        node_handle = get_field(event, 'node_handle')
        rmw_handle = get_field(event, 'rmw_subscription_handle')
        topic_name = get_field(event, 'topic_name')
        depth = get_field(event, 'queue_depth')
        self.data.add_rcl_subscription(
            handle, timestamp, node_handle, rmw_handle, topic_name, depth,
        )

    def _handle_rclcpp_subscription_init(
        self, event: Dict, metadata: EventMetadata,
    ) -> None:
        subscription_pointer = get_field(event, 'subscription')
        timestamp = metadata.timestamp
        handle = get_field(event, 'subscription_handle')
        self.data.add_rclcpp_subscription(subscription_pointer, timestamp, handle)

    def _handle_rclcpp_subscription_callback_added(
        self, event: Dict, metadata: EventMetadata,
    ) -> None:
        subscription_pointer = get_field(event, 'subscription')
        timestamp = metadata.timestamp
        callback_object = get_field(event, 'callback')
        self.data.add_callback_object(subscription_pointer, timestamp, callback_object)

    def _handle_rmw_take(
        self, event: Dict, metadata: EventMetadata,
    ) -> None:
        subscription_handle = get_field(event, 'rmw_subscription_handle')
        timestamp = metadata.timestamp
        message = get_field(event, 'message')
        source_timestamp = get_field(event, 'source_timestamp')
        taken = bool(get_field(event, 'taken'))
        self.data.add_rmw_take_instance(
            subscription_handle, timestamp, message, source_timestamp, taken
        )

    def _handle_rcl_take(
        self, event: Dict, metadata: EventMetadata,
    ) -> None:
        timestamp = metadata.timestamp
        message = get_field(event, 'message')
        self.data.add_rcl_take_instance(timestamp, message)

    def _handle_rclcpp_take(
        self, event: Dict, metadata: EventMetadata,
    ) -> None:
        timestamp = metadata.timestamp
        message = get_field(event, 'message')
        self.data.add_rclcpp_take_instance(timestamp, message)

    def _handle_rcl_service_init(
        self, event: Dict, metadata: EventMetadata,
    ) -> None:
        handle = get_field(event, 'service_handle')
        timestamp = metadata.timestamp
        node_handle = get_field(event, 'node_handle')
        rmw_handle = get_field(event, 'rmw_service_handle')
        service_name = get_field(event, 'service_name')
        self.data.add_service(handle, timestamp, node_handle, rmw_handle, service_name)

    def _handle_rclcpp_service_callback_added(
        self, event: Dict, metadata: EventMetadata,
    ) -> None:
        handle = get_field(event, 'service_handle')
        timestamp = metadata.timestamp
        callback_object = get_field(event, 'callback')
        self.data.add_callback_object(handle, timestamp, callback_object)

    def _handle_rcl_client_init(
        self, event: Dict, metadata: EventMetadata,
    ) -> None:
        handle = get_field(event, 'client_handle')
        timestamp = metadata.timestamp
        node_handle = get_field(event, 'node_handle')
        rmw_handle = get_field(event, 'rmw_client_handle')
        service_name = get_field(event, 'service_name')
        self.data.add_client(handle, timestamp, node_handle, rmw_handle, service_name)

    def _handle_rcl_timer_init(
        self, event: Dict, metadata: EventMetadata,
    ) -> None:
        handle = get_field(event, 'timer_handle')
        timestamp = metadata.timestamp
        period = get_field(event, 'period')
        tid = metadata.tid
        self.data.add_timer(handle, timestamp, period, tid)

    def _handle_rclcpp_timer_callback_added(
        self, event: Dict, metadata: EventMetadata,
    ) -> None:
        handle = get_field(event, 'timer_handle')
        timestamp = metadata.timestamp
        callback_object = get_field(event, 'callback')
        self.data.add_callback_object(handle, timestamp, callback_object)

    def _handle_rclcpp_timer_link_node(
        self, event: Dict, metadata: EventMetadata,
    ) -> None:
        handle = get_field(event, 'timer_handle')
        timestamp = metadata.timestamp
        node_handle = get_field(event, 'node_handle')
        self.data.add_timer_node_link(handle, timestamp, node_handle)

    def _handle_rclcpp_callback_register(
        self, event: Dict, metadata: EventMetadata,
    ) -> None:
        callback_object = get_field(event, 'callback')
        timestamp = metadata.timestamp
        symbol = get_field(event, 'symbol')
        self.data.add_callback_symbol(callback_object, timestamp, symbol)

    def _handle_callback_start(
        self, event: Dict, metadata: EventMetadata,
    ) -> None:
        # Add to dict
        callback_addr = get_field(event, 'callback')
        self._callback_instances[callback_addr] = (event, metadata)

    def _handle_callback_end(
        self, event: Dict, metadata: EventMetadata,
    ) -> None:
        # Fetch from dict
        callback_object = get_field(event, 'callback')
        callback_instance_data = self._callback_instances.get(callback_object)
        if callback_instance_data is not None:
            (event_start, metadata_start) = callback_instance_data
            del self._callback_instances[callback_object]
            duration = metadata.timestamp - metadata_start.timestamp
            is_intra_process = get_field(event_start, 'is_intra_process', raise_if_not_found=False)
            self.data.add_callback_instance(
                callback_object,
                metadata_start.timestamp,
                duration,
                bool(is_intra_process))
        else:
            print(f'No matching callback start for callback object "{callback_object}"')

    def _handle_rcl_lifecycle_state_machine_init(
        self, event: Dict, metadata: EventMetadata,
    ) -> None:
        node_handle = get_field(event, 'node_handle')
        state_machine = get_field(event, 'state_machine')
        self.data.add_lifecycle_state_machine(state_machine, node_handle)

    def _handle_rcl_lifecycle_transition(
        self, event: Dict, metadata: EventMetadata,
    ) -> None:
        timestamp = metadata.timestamp
        state_machine = get_field(event, 'state_machine')
        start_label = get_field(event, 'start_label')
        goal_label = get_field(event, 'goal_label')
        self.data.add_lifecycle_state_transition(state_machine, start_label, goal_label, timestamp)
