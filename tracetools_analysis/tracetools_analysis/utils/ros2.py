# Copyright 2019 Robert Bosch GmbH
# Copyright 2019 Apex.AI, Inc.
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
from typing import Union

from pandas import DataFrame

from . import DataModelUtil
from ..data_model.ros2 import Ros2DataModel


class Ros2DataModelUtil(DataModelUtil):
    """ROS 2 data model utility class."""

    def __init__(
        self,
        data_model: Ros2DataModel,
    ) -> None:
        """
        Constructor.

        :param data_model: the data model object to use
        """
        super().__init__(data_model)

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
        STD_ALLOCATOR = '_<std::allocator<void>>'
        pretty = pretty.replace(STD_ALLOCATOR, '')
        # default_delete
        STD_DEFAULTDELETE = 'std::default_delete'
        if STD_DEFAULTDELETE in pretty:
            dd_start = pretty.find(STD_DEFAULTDELETE)
            template_param_open = dd_start + len(STD_DEFAULTDELETE)
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
        STD_BIND = 'std::_Bind<'
        if pretty.startswith(STD_BIND):
            # remove bind<>
            pretty = pretty.replace(STD_BIND, '')
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

    def get_callback_durations(
        self,
        callback_obj: int,
    ) -> DataFrame:
        """
        Get durations of callback instances for a given callback object.

        :param callback_obj: the callback object value
        :return: a dataframe containing the start timestamp (datetime)
        and duration (ms) of all callback instances for that object
        """
        data = self.data.callback_instances.loc[
            self.data.callback_instances.loc[:, 'callback_object'] == callback_obj,
            ['timestamp', 'duration']
        ]
        # Time conversion
        return self.convert_time_columns(data, ['duration'], ['timestamp'])

    def get_node_tid_from_name(
        self,
        node_name: str,
    ) -> Union[int, None]:
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
    ) -> Union[List[str], None]:
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
    ) -> Union[str, None]:
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
        elif reference in self.data.publishers.index:
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

        if info is not None:
            info = f'{type_name} -- {self.format_info_dict(info)}'
        return info

    def get_timer_handle_info(
        self,
        timer_handle: int,
    ) -> Union[Mapping[str, Any], None]:
        """
        Get information about the owner of a timer.

        :param timer_handle: the timer handle value
        :return: a dictionary with name:value info, or `None` if it fails
        """
        # TODO find a way to link a timer to a specific node
        if timer_handle not in self.data.timers.index:
            return None

        tid = self.data.timers.loc[timer_handle, 'tid']
        period_ns = self.data.timers.loc[timer_handle, 'period']
        period_ms = period_ns / 1000000.0
        return {'tid': tid, 'period': f'{period_ms:.0f} ms'}

    def get_publisher_handle_info(
        self,
        publisher_handle: int,
    ) -> Union[Mapping[str, Any], None]:
        """
        Get information about a publisher handle.

        :param publisher_handle: the publisher handle value
        :return: a dictionary with name:value info, or `None` if it fails
        """
        if publisher_handle not in self.data.publishers.index:
            return None

        node_handle = self.data.publishers.loc[publisher_handle, 'node_handle']
        node_handle_info = self.get_node_handle_info(node_handle)
        topic_name = self.data.publishers.loc[publisher_handle, 'topic_name']
        publisher_info = {'topic': topic_name}
        return {**node_handle_info, **publisher_info}

    def get_subscription_reference_info(
        self,
        subscription_reference: int,
    ) -> Union[Mapping[str, Any], None]:
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
        subscriptions_simple = self.data.subscriptions.drop(
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
        topic_name = subscriptions_info.loc[subscription_reference, 'topic_name']
        subscription_info = {'topic': topic_name}
        return {**node_handle_info, **subscription_info}

    def get_service_handle_info(
        self,
        service_handle: int,
    ) -> Union[Mapping[str, Any], None]:
        """
        Get information about a service handle.

        :param service_handle: the service handle value
        :return: a dictionary with name:value info, or `None` if it fails
        """
        if service_handle not in self.data.services:
            return None

        node_handle = self.data.services.loc[service_handle, 'node_handle']
        node_handle_info = self.get_node_handle_info(node_handle)
        service_name = self.data.services.loc[service_handle, 'service_name']
        service_info = {'service': service_name}
        return {**node_handle_info, **service_info}

    def get_client_handle_info(
        self,
        client_handle: int,
    ) -> Union[Mapping[str, Any], None]:
        """
        Get information about a client handle.

        :param client_handle: the client handle value
        :return: a dictionary with name:value info, or `None` if it fails
        """
        if client_handle not in self.data.clients:
            return None

        node_handle = self.data.clients.loc[client_handle, 'node_handle']
        node_handle_info = self.get_node_handle_info(node_handle)
        service_name = self.data.clients.loc[client_handle, 'service_name']
        service_info = {'service': service_name}
        return {**node_handle_info, **service_info}

    def get_node_handle_info(
        self,
        node_handle: int,
    ) -> Union[Mapping[str, Any], None]:
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

    def format_info_dict(
        self,
        info_dict: Mapping[str, Any],
    ) -> str:
        return ', '.join([f'{key}: {val}' for key, val in info_dict.items()])
