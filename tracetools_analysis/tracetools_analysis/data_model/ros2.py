# Copyright 2019 Robert Bosch GmbH
# Copyright 2020-2021 Christophe Bedard
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

"""Module for ROS 2 data model."""

import pandas as pd

from . import DataModel
from . import DataModelIntermediateStorage


class Ros2DataModel(DataModel):
    """
    Container to model pre-processed ROS 2 data for analysis.

    This aims to represent the data in a ROS 2-aware way.
    """

    def __init__(self) -> None:
        """Create a Ros2DataModel."""
        super().__init__()
        # Objects (one-time events, usually when something is created)
        self._contexts: DataModelIntermediateStorage = []
        self._nodes: DataModelIntermediateStorage = []
        self._publishers: DataModelIntermediateStorage = []
        self._subscriptions: DataModelIntermediateStorage = []
        self._subscription_objects: DataModelIntermediateStorage = []
        self._services: DataModelIntermediateStorage = []
        self._clients: DataModelIntermediateStorage = []
        self._timers: DataModelIntermediateStorage = []
        self._callback_objects: DataModelIntermediateStorage = []
        self._callback_symbols: DataModelIntermediateStorage = []
        # Events (multiple instances, may not have a meaningful index)
        self._callback_instances: DataModelIntermediateStorage = []

    def add_context(
        self, context_handle, timestamp, pid, version
    ) -> None:
        self._contexts.append({
            'context_handle': context_handle,
            'timestamp': timestamp,
            'pid': pid,
            'version': version,
        })

    def add_node(
        self, node_handle, timestamp, tid, rmw_handle, name, namespace
    ) -> None:
        self._nodes.append({
            'node_handle': node_handle,
            'timestamp': timestamp,
            'tid': tid,
            'rmw_handle': rmw_handle,
            'name': name,
            'namespace': namespace,
        })

    def add_publisher(
        self, handle, timestamp, node_handle, rmw_handle, topic_name, depth
    ) -> None:
        self._publishers.append({
            'publisher_handle': handle,
            'timestamp': timestamp,
            'node_handle': node_handle,
            'rmw_handle': rmw_handle,
            'topic_name': topic_name,
            'depth': depth,
        })

    def add_rcl_subscription(
        self, handle, timestamp, node_handle, rmw_handle, topic_name, depth
    ) -> None:
        self._subscriptions.append({
            'subscription_handle': handle,
            'timestamp': timestamp,
            'node_handle': node_handle,
            'rmw_handle': rmw_handle,
            'topic_name': topic_name,
            'depth': depth,
        })

    def add_rclcpp_subscription(
        self, subscription_pointer, timestamp, subscription_handle
    ) -> None:
        self._subscription_objects.append({
            'subscription': subscription_pointer,
            'timestamp': timestamp,
            'subscription_handle': subscription_handle,
        })

    def add_service(
        self, handle, timestamp, node_handle, rmw_handle, service_name
    ) -> None:
        self._services.append({
            'service_handle': timestamp,
            'timestamp': timestamp,
            'node_handle': node_handle,
            'rmw_handle': rmw_handle,
            'service_name': service_name,
        })

    def add_client(
        self, handle, timestamp, node_handle, rmw_handle, service_name
    ) -> None:
        self._clients.append({
            'client_handle': handle,
            'timestamp': timestamp,
            'node_handle': node_handle,
            'rmw_handle': rmw_handle,
            'service_name': service_name,
        })

    def add_timer(
        self, handle, timestamp, period, tid
    ) -> None:
        self._timers.append({
            'timer_handle': handle,
            'timestamp': timestamp,
            'period': period,
            'tid': tid,
        })

    def add_callback_object(
        self, reference, timestamp, callback_object
    ) -> None:
        self._callback_objects.append({
            'reference': reference,
            'timestamp': timestamp,
            'callback_object': callback_object,
        })

    def add_callback_symbol(
        self, callback_object, timestamp, symbol
    ) -> None:
        self._callback_symbols.append({
            'callback_object': callback_object,
            'timestamp': timestamp,
            'symbol': symbol,
        })

    def add_callback_instance(
        self, callback_object, timestamp, duration, intra_process
    ) -> None:
        self._callback_instances.append({
            'callback_object': callback_object,
            'timestamp': timestamp,
            'duration': duration,
            'intra_process': intra_process,
        })

    def _finalize(self) -> None:
        # Some of the lists of dicts might be empty, and setting
        # the index for an empty dataframe leads to an error
        self.contexts = pd.DataFrame.from_dict(self._contexts)
        if self._contexts:
            self.contexts.set_index('context_handle', inplace=True, drop=True)
        self.nodes = pd.DataFrame.from_dict(self._nodes)
        if self._nodes:
            self.nodes.set_index('node_handle', inplace=True, drop=True)
        self.publishers = pd.DataFrame.from_dict(self._publishers)
        if self._publishers:
            self.publishers.set_index('publisher_handle', inplace=True, drop=True)
        self.subscriptions = pd.DataFrame.from_dict(self._subscriptions)
        if self._subscriptions:
            self.subscriptions.set_index('subscription_handle', inplace=True, drop=True)
        self.subscription_objects = pd.DataFrame.from_dict(self._subscription_objects)
        if self._subscription_objects:
            self.subscription_objects.set_index('subscription', inplace=True, drop=True)
        self.services = pd.DataFrame.from_dict(self._services)
        if self._services:
            self.services.set_index('service_handle', inplace=True, drop=True)
        self.clients = pd.DataFrame.from_dict(self._clients)
        if self._clients:
            self.clients.set_index('client_handle', inplace=True, drop=True)
        self.timers = pd.DataFrame.from_dict(self._timers)
        if self._timers:
            self.timers.set_index('timer_handle', inplace=True, drop=True)
        self.callback_objects = pd.DataFrame.from_dict(self._callback_objects)
        if self._callback_objects:
            self.callback_objects.set_index('reference', inplace=True, drop=True)
        self.callback_symbols = pd.DataFrame.from_dict(self._callback_symbols)
        if self._callback_symbols:
            self.callback_symbols.set_index('callback_object', inplace=True, drop=True)
        self.callback_instances = pd.DataFrame.from_dict(self._callback_instances)

    def print_data(self) -> None:
        print('====================ROS 2 DATA MODEL===================')
        print('Contexts:')
        print(self.contexts.to_string())
        print()
        print('Nodes:')
        print(self.nodes.to_string())
        print()
        print('Publishers:')
        print(self.publishers.to_string())
        print()
        print('Subscriptions:')
        print(self.subscriptions.to_string())
        print()
        print('Subscription objects:')
        print(self.subscription_objects.to_string())
        print()
        print('Services:')
        print(self.services.to_string())
        print()
        print('Clients:')
        print(self.clients.to_string())
        print()
        print('Timers:')
        print(self.timers.to_string())
        print()
        print('Callback objects:')
        print(self.callback_objects.to_string())
        print()
        print('Callback symbols:')
        print(self.callback_symbols.to_string())
        print()
        print('Callback instances:')
        print(self.callback_instances.to_string())
        print('==================================================')
