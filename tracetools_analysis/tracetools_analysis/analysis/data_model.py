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

"""Module for data model."""

import pandas as pd


class DataModel():
    """
    Container to model pre-processed data for analysis.

    Contains data for an analysis to use. This is a middleground between trace events data and the
    output data of an analysis. This aims to represent the data in a ROS-aware way.
    It uses pandas DataFrames directly.
    """

    def __init__(self) -> None:
        # Objects (one-time events, usually when something is created)
        self.contexts = pd.DataFrame(columns=['context_handle',
                                              'timestamp',
                                              'pid',
                                              'version'])
        self.contexts.set_index(['context_handle'], inplace=True, drop=True)
        self.nodes = pd.DataFrame(columns=['node_handle',
                                           'timestamp',
                                           'tid',
                                           'rmw_handle',
                                           'name',
                                           'namespace'])
        self.nodes.set_index(['node_handle'], inplace=True, drop=True)
        self.publishers = pd.DataFrame(columns=['publisher_handle',
                                                'timestamp',
                                                'node_handle',
                                                'rmw_handle',
                                                'topic_name',
                                                'depth'])
        self.publishers.set_index(['publisher_handle'], inplace=True, drop=True)
        self.subscriptions = pd.DataFrame(columns=['subscription_handle',
                                                   'timestamp',
                                                   'node_handle',
                                                   'rmw_handle',
                                                   'topic_name',
                                                   'depth'])
        self.subscriptions.set_index(['subscription_handle'], inplace=True, drop=True)
        self.services = pd.DataFrame(columns=['service_handle',
                                              'timestamp',
                                              'node_handle',
                                              'rmw_handle',
                                              'service_name'])
        self.services.set_index(['service_handle'], inplace=True, drop=True)
        self.clients = pd.DataFrame(columns=['client_handle',
                                             'timestamp',
                                             'node_handle',
                                             'rmw_handle',
                                             'service_name'])
        self.clients.set_index(['client_handle'], inplace=True, drop=True)
        self.timers = pd.DataFrame(columns=['timer_handle',
                                            'timestamp',
                                            'period',
                                            'tid'])
        self.timers.set_index(['timer_handle'], inplace=True, drop=True)

        self.callback_objects = pd.DataFrame(columns=['handle',
                                                      'timestamp',
                                                      'callback_object'])
        self.callback_objects.set_index(['handle'], inplace=True, drop=True)
        self.callback_symbols = pd.DataFrame(columns=['callback_object',
                                                      'timestamp',
                                                      'symbol'])
        self.callback_symbols.set_index(['callback_object'], inplace=True, drop=True)

        # Events (multiple instances, may not have a meaningful index)
        self.callback_instances = pd.DataFrame(columns=['callback_object',
                                                        'timestamp',
                                                        'duration',
                                                        'intra_process'])

    def add_context(
        self, context_handle, timestamp, pid, version
    ) -> None:
        self.contexts.loc[context_handle] = [timestamp, pid, version]

    def add_node(
        self, node_handle, timestamp, tid, rmw_handle, name, namespace
    ) -> None:
        self.nodes.loc[node_handle] = [timestamp, tid, rmw_handle, name, namespace]

    def add_publisher(
        self, handle, timestamp, node_handle, rmw_handle, topic_name, depth
    ) -> None:
        self.publishers.loc[handle] = [timestamp, node_handle, rmw_handle, topic_name, depth]

    def add_subscription(
        self, handle, timestamp, node_handle, rmw_handle, topic_name, depth
    ) -> None:
        self.subscriptions.loc[handle] = [timestamp, node_handle, rmw_handle, topic_name, depth]

    def add_service(
        self, handle, timestamp, node_handle, rmw_handle, service_name
    ) -> None:
        self.services.loc[handle] = [timestamp, node_handle, rmw_handle, service_name]

    def add_client(
        self, handle, timestamp, node_handle, rmw_handle, service_name
    ) -> None:
        self.clients.loc[handle] = [timestamp, node_handle, rmw_handle, service_name]

    def add_timer(
        self, handle, timestamp, period, tid
    ) -> None:
        self.timers.loc[handle] = [timestamp, period, tid]

    def add_callback_object(
        self, handle, timestamp, callback_object
    ) -> None:
        self.callback_objects.loc[handle] = [timestamp, callback_object]

    def add_callback_symbol(
        self, callback_object, timestamp, symbol
    ) -> None:
        self.callback_symbols.loc[callback_object] = [timestamp, symbol]

    def add_callback_instance(
        self, callback_object, timestamp, duration, intra_process
    ) -> None:
        data = {
            'callback_object': callback_object,
            'timestamp': timestamp,
            'duration': duration,
            'intra_process': intra_process,
        }
        self.callback_instances = self.callback_instances.append(data, ignore_index=True)

    def print_model(self) -> None:
        """Debug method to print every contained df."""
        print('====================DATA MODEL====================')
        print(f'Contexts:\n{self.contexts.to_string()}')
        print()
        print(f'Nodes:\n{self.nodes.to_string()}')
        print()
        print(f'Publishers:\n{self.publishers.to_string()}')
        print()
        print(f'Subscriptions:\n{self.subscriptions.to_string()}')
        print()
        print(f'Services:\n{self.services.to_string()}')
        print()
        print(f'Clients:\n{self.clients.to_string()}')
        print()
        print(f'Timers:\n{self.timers.to_string()}')
        print()
        print(f'Callback objects:\n{self.callback_objects.to_string()}')
        print()
        print(f'Callback symbols:\n{self.callback_symbols.to_string()}')
        print()
        print(f'Callback instances:\n{self.callback_instances.to_string()}')
        print('==================================================')
