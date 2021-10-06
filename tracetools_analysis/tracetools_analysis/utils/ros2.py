# Copyright 2019 Robert Bosch GmbH
# Copyright 2019 Apex.AI, Inc.
# Copyright 2021 Christophe Bedard
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

"""Module for ROS data model utils."""

from typing import Any
from typing import List
from typing import Mapping
from typing import Optional
from typing import Union

import numpy as np
from pandas import concat
from pandas import DataFrame

from . import DataModelUtil
from ..data_model.ros2 import Ros2DataModel
from ..processor.ros2 import Ros2Handler


class Ros2DataModelUtil(DataModelUtil):
    """ROS 2 data model utility class."""

    def __init__(
        self,
        data_object: Union[Ros2DataModel, Ros2Handler],
    ) -> None:
        """
        Create a Ros2DataModelUtil.

        :param data_object: the data model or the event handler which has a data model
        """
        super().__init__(data_object)

    @property
    def data(self) -> Ros2DataModel:
        return super().data  # type: ignore

    def _prettify(
        self,
        original: str,
    ) -> str:
        """
        Process symbol to make it more readable.

        * remove std::allocator
        * remove std::default_delete
        * bind object: remove placeholder

        :param original: the original symbol
        :return: the prettified symbol
        """
        pretty = original
        # remove spaces
        pretty = pretty.replace(' ', '')
        # allocator
        std_allocator = '_<std::allocator<void>>'
        pretty = pretty.replace(std_allocator, '')
        # default_delete
        std_defaultdelete = 'std::default_delete'
        if std_defaultdelete in pretty:
            dd_start = pretty.find(std_defaultdelete)
            template_param_open = dd_start + len(std_defaultdelete)
            # find index of matching/closing GT sign
            template_param_close = template_param_open
            level = 0
            done = False
            while not done:
                template_param_close += 1
                if pretty[template_param_close] == '<':
                    level += 1
                elif pretty[template_param_close] == '>':
                    if level == 0:
                        done = True
                    else:
                        level -= 1
            pretty = pretty[:dd_start] + pretty[(template_param_close + 1):]
        # bind
        std_bind = 'std::_Bind<'
        if pretty.startswith(std_bind):
            # remove bind<>
            pretty = pretty.replace(std_bind, '')
            pretty = pretty[:-1]
            # remove placeholder stuff
            placeholder_from = pretty.find('*')
            placeholder_to = pretty.find(')', placeholder_from)
            pretty = pretty[:placeholder_from] + '?' + pretty[(placeholder_to + 1):]
        # remove dangling comma
        pretty = pretty.replace(',>', '>')
        # restore meaningful spaces
        if pretty.startswith('void'):
            pretty = 'void' + ' ' + pretty[len('void'):]
        if pretty.endswith('const'):
            pretty = pretty[:(len(pretty) - len('const'))] + ' ' + 'const'
        return pretty

    def get_callback_symbols(self) -> Mapping[int, str]:
        """
        Get mappings between a callback object and its resolved symbol.

        :return: the map
        """
        callback_instances = self.data.callback_instances
        callback_symbols = self.data.callback_symbols

        # Get a list of callback objects
        callback_objects = set(callback_instances['callback_object'])
        # Get their symbol
        return {
            obj: self._prettify(callback_symbols.loc[obj, 'symbol']) for obj in callback_objects
        }

    def get_tids(self) -> List[str]:
        """Get a list of thread ids corresponding to the nodes."""
        return self.data.nodes['tid'].unique().tolist()

    def get_rcl_publish_instances(self, topic_name) -> Optional[DataFrame]:
        """
        Get rcl publish instances for all publishers with the given topic name.

        :param topic_name: the topic name
        :return: dataframe with [publisher handle, publish timestamp, message] columns,
            or `None` if topic name not found
        """
        # We could have more than one publisher for the topic
        publisher_handles = self.data.rcl_publishers.loc[
            self.data.rcl_publishers['topic_name'] == topic_name
        ].index.values.astype(int)
        if len(publisher_handles) == 0:
            return None
        publish_instances = self.data.rcl_publish_instances.loc[
            self.data.rcl_publish_instances['publisher_handle'].isin(publisher_handles)
        ]
        publish_instances.reset_index(drop=True, inplace=True)
        self.convert_time_columns(publish_instances, [], ['timestamp'], True)
        return publish_instances

    def get_publish_instances(self) -> DataFrame:
        """
        Get all publish instances (rclcpp, rcl, rmw) in a single dataframe.

        The rows are ordered by publish timestamp, so the order will usually be: rclcpp, rcl, rmw.
        However, this does not apply to publications from internal publishers, i.e.,
        publications that originate from below rclcpp (rcl or rmw).
        TODO(christophebedard) find heuristic to exclude those?

        :return: dataframe with [timestamp, message, layer 'rclcpp'|'rcl'|'rmw', publisher handle]
            columns, ordered by timestamp,
            and where the publisher handle is only set (non-zero) for 'rcl' publish instances
        """
        # Add publisher handle columns with zeros for dataframes that do not have this column,
        # otherwise NaN is used and the publisher handle values for rcl are converted to float
        rclcpp_instances = self.data.rclcpp_publish_instances.copy()
        rclcpp_instances['layer'] = 'rclcpp'
        rclcpp_instances['publisher_handle'] = 0
        rcl_instances = self.data.rcl_publish_instances.copy()
        rcl_instances['layer'] = 'rcl'
        rmw_instances = self.data.rmw_publish_instances.copy()
        rmw_instances['layer'] = 'rmw'
        rmw_instances['publisher_handle'] = 0
        publish_instances = concat([rclcpp_instances, rcl_instances, rmw_instances], axis=0)
        publish_instances.sort_values('timestamp', inplace=True)
        publish_instances.reset_index(drop=True, inplace=True)
        self.convert_time_columns(publish_instances, [], ['timestamp'], True)
        return publish_instances

    def get_take_instances(self) -> DataFrame:
        """
        Get all take instances (rmw, rcl, rclcpp) in a single dataframe.

        The rows are ordered by take timestamp, so the order will usually be: rmw, rcl, rclcpp.
        However, thsi does not apply to takes from internal subscriptions, i.e.,
        takes that originate from below rclcpp (rcl or rmw).
        TODO(christophebedard) find heuristic to exclude those?

        :return: dataframe with
            [timestamp, message, source timestamp,
                layer 'rmw'|'rcl'|'rmw', rmw subscription handle, taken]
            columns, ordered by timestamp,
            and where the rmw subscription handle, source timestamp, and taken flag are only set
            (non-zero, non-False) for 'rmw' take instances
        """
        rmw_instances = self.data.rmw_take_instances.copy()
        rmw_instances['layer'] = 'rmw'
        rmw_instances.rename(
            columns={'subscription_handle': 'rmw_subscription_handle'},
            inplace=True,
        )
        rcl_instances = self.data.rcl_take_instances.copy()
        rcl_instances['layer'] = 'rcl'
        rcl_instances['rmw_subscription_handle'] = 0
        rcl_instances['source_timestamp'] = 0
        rcl_instances['taken'] = False
        rclcpp_instances = self.data.rclcpp_take_instances.copy()
        rclcpp_instances['layer'] = 'rclcpp'
        rclcpp_instances['rmw_subscription_handle'] = 0
        rclcpp_instances['source_timestamp'] = 0
        rclcpp_instances['taken'] = False
        take_instances = concat([rmw_instances, rcl_instances, rclcpp_instances], axis=0)
        take_instances.sort_values('timestamp', inplace=True)
        take_instances.reset_index(drop=True, inplace=True)
        self.convert_time_columns(take_instances, [], ['timestamp', 'source_timestamp'], True)
        return take_instances

    def get_callback_durations(
        self,
        callback_obj: int,
    ) -> DataFrame:
        """
        Get durations of callback instances for a given callback object.

        :param callback_obj: the callback object value
        :return: a dataframe containing the start timestamp (np.timestamp64)
            and duration (np.timedelta64) of all callback instances for that object
        """
        return self.data.callback_instances.loc[
            self.data.callback_instances.loc[:, 'callback_object'] == callback_obj,
            ['timestamp', 'duration']
        ]

    def get_node_tid_from_name(
        self,
        node_name: str,
    ) -> Optional[int]:
        """
        Get the tid corresponding to a node.

        :param node_name: the name of the node
        :return: the tid, or `None` if not found
        """
        # Assuming there is only one row with the given name
        node_row = self.data.nodes.loc[
            self.data.nodes['name'] == node_name
        ]
        assert len(node_row.index) <= 1, 'more than 1 node found'
        return node_row.iloc[0]['tid'] if not node_row.empty else None

    def get_node_names_from_tid(
        self,
        tid: str,
    ) -> Optional[List[str]]:
        """
        Get the list of node names corresponding to a tid.

        :param tid: the tid
        :return: the list of node names, or `None` if not found
        """
        return self.data.nodes[
            self.data.nodes['tid'] == tid
        ]['name'].tolist()

    def get_callback_owner_info(
        self,
        callback_obj: int,
    ) -> Optional[str]:
        """
        Get information about the owner of a callback.

        Depending on the type of callback, it will give different kinds of info:
          * subscription: node name, topic name
          * timer: tid, period of timer
          * service/client: node name, service name

        :param callback_obj: the callback object value
        :return: information about the owner of the callback, or `None` if it fails
        """
        # Get reference corresponding to callback object
        reference = self.data.callback_objects.loc[
            self.data.callback_objects['callback_object'] == callback_obj
        ].index.values.astype(int)[0]

        type_name = None
        info = None
        # Check if it's a timer first (since it's slightly different than the others)
        if reference in self.data.timers.index:
            type_name = 'Timer'
            info = self.get_timer_handle_info(reference)
        elif reference in self.data.rcl_publishers.index:
            type_name = 'Publisher'
            info = self.get_publisher_handle_info(reference)
        elif reference in self.data.subscription_objects.index:
            type_name = 'Subscription'
            info = self.get_subscription_reference_info(reference)
        elif reference in self.data.services.index:
            type_name = 'Service'
            info = self.get_service_handle_info(reference)
        elif reference in self.data.clients.index:
            type_name = 'Client'
            info = self.get_client_handle_info(reference)

        if info is None:
            return None
        return f'{type_name} -- {self.format_info_dict(info)}'

    def get_timer_handle_info(
        self,
        timer_handle: int,
    ) -> Union[Mapping[str, Any], None]:
        """
        Get information about the owner of a timer.

        :param timer_handle: the timer handle value
        :return: a dictionary with name:value info, or `None` if it fails
        """
        if timer_handle not in self.data.timers.index:
            return None

        node_handle = self.data.timer_node_links.loc[timer_handle, 'node_handle']
        node_handle_info = self.get_node_handle_info(node_handle)
        if node_handle_info is None:
            return None

        tid = self.data.timers.loc[timer_handle, 'tid']
        period_ns = self.data.timers.loc[timer_handle, 'period']
        period_ms = period_ns / 1000000.0
        return {**node_handle_info, 'tid': tid, 'period': f'{period_ms:.0f} ms'}

    def get_publisher_handle_info(
        self,
        publisher_handle: int,
    ) -> Union[Mapping[str, Any], None]:
        """
        Get information about a publisher handle.

        :param publisher_handle: the publisher handle value
        :return: a dictionary with name:value info, or `None` if it fails
        """
        if publisher_handle not in self.data.rcl_publishers.index:
            return None

        node_handle = self.data.rcl_publishers.loc[publisher_handle, 'node_handle']
        node_handle_info = self.get_node_handle_info(node_handle)
        if node_handle_info is None:
            return None
        topic_name = self.data.rcl_publishers.loc[publisher_handle, 'topic_name']
        publisher_info = {'topic': topic_name}
        return {**node_handle_info, **publisher_info}

    def get_subscription_reference_info(
        self,
        subscription_reference: int,
    ) -> Optional[Mapping[str, Any]]:
        """
        Get information about a subscription handle.

        :param subscription_reference: the subscription reference value
        :return: a dictionary with name:value info, or `None` if it fails
        """
        # First check that the subscription reference exists
        if subscription_reference not in self.data.subscription_objects.index:
            return None

        # To get information about a subscription reference, we need 3 dataframes
        #   * subscription_objects
        #      * subscription (reference) <--> subscription_handle
        #   * subscriptions
        #      * subscription_handle <--> topic_name
        #      * subscription_handle <--> node_handle
        #   * nodes
        #      * node_handle <--> (node info)
        # First, drop unnecessary common columns for debugging simplicity
        subscription_objects_simple = self.data.subscription_objects.drop(
            columns=['timestamp'],
            axis=1,
        )
        subscriptions_simple = self.data.rcl_subscriptions.drop(
            columns=['timestamp', 'rmw_handle'],
            inplace=False,
        )
        nodes_simple = self.data.nodes.drop(
            columns=['timestamp', 'rmw_handle'],
            inplace=False,
        )
        # Then merge the 3 dataframes
        subscriptions_info = subscription_objects_simple.merge(
            subscriptions_simple,
            left_on='subscription_handle',
            right_index=True,
        ).merge(
            nodes_simple,
            left_on='node_handle',
            right_index=True,
        )

        node_handle = subscriptions_info.loc[subscription_reference, 'node_handle']
        node_handle_info = self.get_node_handle_info(node_handle)
        if node_handle_info is None:
            return None
        topic_name = subscriptions_info.loc[subscription_reference, 'topic_name']
        subscription_info = {'topic': topic_name}
        return {**node_handle_info, **subscription_info}

    def get_service_handle_info(
        self,
        service_handle: int,
    ) -> Optional[Mapping[str, Any]]:
        """
        Get information about a service handle.

        :param service_handle: the service handle value
        :return: a dictionary with name:value info, or `None` if it fails
        """
        if service_handle not in self.data.services:
            return None

        node_handle = self.data.services.loc[service_handle, 'node_handle']
        node_handle_info = self.get_node_handle_info(node_handle)
        if node_handle_info is None:
            return None
        service_name = self.data.services.loc[service_handle, 'service_name']
        service_info = {'service': service_name}
        return {**node_handle_info, **service_info}

    def get_client_handle_info(
        self,
        client_handle: int,
    ) -> Optional[Mapping[str, Any]]:
        """
        Get information about a client handle.

        :param client_handle: the client handle value
        :return: a dictionary with name:value info, or `None` if it fails
        """
        if client_handle not in self.data.clients:
            return None

        node_handle = self.data.clients.loc[client_handle, 'node_handle']
        node_handle_info = self.get_node_handle_info(node_handle)
        if node_handle_info is None:
            return None
        service_name = self.data.clients.loc[client_handle, 'service_name']
        service_info = {'service': service_name}
        return {**node_handle_info, **service_info}

    def get_node_handle_info(
        self,
        node_handle: int,
    ) -> Optional[Mapping[str, Any]]:
        """
        Get information about a node handle.

        :param node_handle: the node handle value
        :return: a dictionary with name:value info, or `None` if it fails
        """
        if node_handle not in self.data.nodes.index:
            return None

        node_name = self.data.nodes.loc[node_handle, 'name']
        tid = self.data.nodes.loc[node_handle, 'tid']
        return {'node': node_name, 'tid': tid}

    def get_lifecycle_node_handle_info(
        self,
        lifecycle_node_handle: int,
    ) -> Optional[Mapping[str, Any]]:
        """
        Get information about a lifecycle node handle.

        :param lifecycle_node_handle: the lifecycle node handle value
        :return: a dictionary with name:value info, or `None` if it fails
        """
        node_info = self.get_node_handle_info(lifecycle_node_handle)
        if not node_info:
            return None
        # TODO(christophebedard) validate that it is an actual lifecycle node and not just a node
        node_info['lifecycle node'] = node_info.pop('node')  # type: ignore
        return node_info

    def get_lifecycle_node_state_intervals(
        self,
    ) -> DataFrame:
        """
        Get state intervals (start, end) for all lifecycle nodes.

        The returned dictionary contains a dataframe for each lifecycle node handle:
            (lifecycle node handle -> [state string, start timestamp, end timestamp])

        In cases where there is no explicit timestamp (e.g. end of state),
        `np.nan` is used instead.
        The node creation timestamp is used as the start timestamp of the first state.
        TODO(christophebedard) do the same with context shutdown for the last end time

        :return: dictionary with a dataframe (with each row containing state interval information)
            for each lifecycle node
        """
        data = {}
        lifecycle_transitions = self.data.lifecycle_transitions.copy()
        state_machine_handles = set(lifecycle_transitions['state_machine_handle'])
        for state_machine_handle in state_machine_handles:
            transitions = lifecycle_transitions.loc[
                lifecycle_transitions.loc[:, 'state_machine_handle'] == state_machine_handle,
                ['start_label', 'goal_label', 'timestamp']
            ]
            # Get lifecycle node handle from state machine handle
            lifecycle_node_handle = self.data.lifecycle_state_machines.loc[
                state_machine_handle, 'node_handle'
            ]

            # Infer first start time from node creation timestamp
            node_creation_timestamp = self.data.nodes.loc[lifecycle_node_handle, 'timestamp']

            # Add initial and final timestamps
            # Last states has an unknown end timestamp
            first_state_label = transitions.loc[0, 'start_label']
            last_state_label = transitions.loc[transitions.index[-1], 'goal_label']
            transitions.loc[-1] = ['', first_state_label, node_creation_timestamp]
            transitions.index = transitions.index + 1
            transitions.sort_index(inplace=True)
            transitions.loc[transitions.index.max() + 1] = [last_state_label, '', np.nan]

            # Process transitions to get start/end timestamp of each instance of a state
            end_timestamps = transitions[['timestamp']].shift(periods=-1)
            end_timestamps.rename(
                columns={end_timestamps.columns[0]: 'end_timestamp'}, inplace=True)
            states = concat([transitions, end_timestamps], axis=1)
            states.drop(['start_label'], axis=1, inplace=True)
            states.rename(
                columns={'goal_label': 'state', 'timestamp': 'start_timestamp'}, inplace=True)
            states.drop(states.tail(1).index, inplace=True)

            # Convert time columns
            self.convert_time_columns(states, [], ['start_timestamp', 'end_timestamp'], True)

            data[lifecycle_node_handle] = states
        return data

    def format_info_dict(
        self,
        info_dict: Mapping[str, Any],
    ) -> str:
        return ', '.join([f'{key}: {val}' for key, val in info_dict.items()])
