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

"""Module for data model utility classes."""

from collections import defaultdict
from datetime import datetime as dt
from typing import Any
from typing import Dict
from typing import List
from typing import Mapping
from typing import Set
from typing import Union

from pandas import DataFrame

from .data_model import DataModel
from .data_model.cpu_time import CpuTimeDataModel
from .data_model.profile import ProfileDataModel
from .data_model.ros import RosDataModel


class DataModelUtil():
    """
    Base data model util class, which provides functions to get more info about a data model.

    This class provides basic util functions.
    """

    def __init__(self, data_model: DataModel) -> None:
        """
        Constructor.

        :param data_model: the data model
        """
        self.__data = data_model

    @property
    def data(self) -> DataModel:
        return self.__data

    @staticmethod
    def convert_time_columns(
        original: DataFrame,
        columns_ns_to_ms: List[str] = [],
        columns_ns_to_datetime: List[str] = [],
        inplace: bool = True,
    ) -> DataFrame:
        """
        Convert time columns from nanoseconds to either milliseconds or `datetime` objects.

        :param original: the original `DataFrame`
        :param columns_ns_to_ms: the columns for which to convert ns to ms
        :param columns_ns_to_datetime: the columns for which to convert ns to `datetime`
        :param inplace: whether to convert in place or to return a copy
        :return: the resulting `DataFrame`
        """
        df = original if inplace else original.copy()
        # Convert from ns to ms
        if len(columns_ns_to_ms) > 0:
            df[columns_ns_to_ms] = df[columns_ns_to_ms].applymap(
                lambda t: t / 1000000.0
            )
        # Convert from ns to ms + ms to datetime, as UTC
        if len(columns_ns_to_datetime) > 0:
            df[columns_ns_to_datetime] = df[columns_ns_to_datetime].applymap(
                lambda t: dt.utcfromtimestamp(t / 1000000000.0)
            )
        return df

    @staticmethod
    def compute_column_difference(
        df: DataFrame,
        left_column: str,
        right_column: str,
        diff_column: str,
    ) -> None:
        """
        Create new column with difference between two columns.

        :param df: the dataframe (inplace)
        :param left_column: the name of the left column
        :param right_column: the name of the right column
        :param diff_column: the name of the new column with differences
        """
        df[diff_column] = df.apply(lambda row: row[left_column] - row[right_column], axis=1)


class ProfileDataModelUtil(DataModelUtil):
    """Profiling data model utility class."""

    def __init__(self, data_model: ProfileDataModel) -> None:
        """
        Constructor.

        :param data_model: the data model object to use
        """
        super().__init__(data_model)

    def with_tid(self, tid: int) -> DataFrame:
        return self.data.times.loc[self.data.times['tid'] == tid]

    def get_tids(self) -> Set[int]:
        """Get the TIDs in the data model."""
        return set(self.data.times['tid'])

    def get_call_tree(self, tid: int) -> Dict[str, List[str]]:
        depth_names = self.with_tid(tid)[
            ['depth', 'function_name', 'parent_name']
        ].drop_duplicates()
        # print(depth_names.to_string())
        tree = defaultdict(set)
        for _, row in depth_names.iterrows():
            depth = row['depth']
            name = row['function_name']
            parent = row['parent_name']
            if depth == 0:
                tree[name]
            else:
                tree[parent].add(name)
        return dict(tree)

    def get_function_duration_data(self, tid: int) -> List[Dict[str, Union[int, str, DataFrame]]]:
        """Get duration data for each function."""
        tid_df = self.with_tid(tid)
        depth_names = tid_df[['depth', 'function_name', 'parent_name']].drop_duplicates()
        functions_data = []
        for _, row in depth_names.iterrows():
            depth = row['depth']
            name = row['function_name']
            parent = row['parent_name']
            data = tid_df.loc[
                (tid_df['depth'] == depth) &
                (tid_df['function_name'] == name)
            ][['start_timestamp', 'duration', 'actual_duration']]
            self.compute_column_difference(
                data,
                'duration',
                'actual_duration',
                'duration_difference',
            )
            functions_data.append({
                'depth': depth,
                'function_name': name,
                'parent_name': parent,
                'data': data,
            })
        return functions_data


class CpuTimeDataModelUtil(DataModelUtil):
    """CPU time data model utility class."""

    def __init__(self, data_model: CpuTimeDataModel) -> None:
        """
        Constructor.

        :param data_model: the data model object to use
        """
        super().__init__(data_model)

    def get_time_per_thread(self) -> DataFrame:
        """Get a DataFrame of total duration for each thread."""
        return self.data.times.loc[:, ['tid', 'duration']].groupby(by='tid').sum()


class RosDataModelUtil(DataModelUtil):
    """ROS data model utility class."""

    def __init__(self, data_model: RosDataModel) -> None:
        """
        Constructor.

        :param data_model: the data model object to use
        """
        super().__init__(data_model)

    def _prettify(self, original: str) -> str:
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
        self, callback_obj: int
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
        return self.convert_time_columns(data, ['timestamp', 'duration'], ['timestamp'])

    def get_node_tid_from_name(
        self, node_name: str
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
        self, tid: str
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
        self, callback_obj: int
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
        # Get handle corresponding to callback object
        handle = self.data.callback_objects.loc[
            self.data.callback_objects['callback_object'] == callback_obj
        ].index.values.astype(int)[0]

        type_name = None
        info = None
        # Check if it's a timer first (since it's slightly different than the others)
        if handle in self.data.timers.index:
            type_name = 'Timer'
            info = self.get_timer_handle_info(handle)
        elif handle in self.data.publishers.index:
            type_name = 'Publisher'
            info = self.get_publisher_handle_info(handle)
        elif handle in self.data.subscriptions.index:
            type_name = 'Subscription'
            info = self.get_subscription_handle_info(handle)
        elif handle in self.data.services.index:
            type_name = 'Service'
            info = self.get_subscription_handle_info(handle)
        elif handle in self.data.clients.index:
            type_name = 'Client'
            info = self.get_client_handle_info(handle)

        if info is not None:
            info = f'{type_name} -- {self.format_info_dict(info)}'
        return info

    def get_timer_handle_info(
        self, timer_handle: int
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
        self, publisher_handle: int
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

    def get_subscription_handle_info(
        self, subscription_handle: int
    ) -> Union[Mapping[str, Any], None]:
        """
        Get information about a subscription handle.

        :param subscription_handle: the subscription handle value
        :return: a dictionary with name:value info, or `None` if it fails
        """
        subscriptions_info = self.data.subscriptions.merge(
            self.data.nodes,
            left_on='node_handle',
            right_index=True)
        if subscription_handle not in self.data.subscriptions.index:
            return None

        node_handle = subscriptions_info.loc[subscription_handle, 'node_handle']
        node_handle_info = self.get_node_handle_info(node_handle)
        topic_name = subscriptions_info.loc[subscription_handle, 'topic_name']
        subscription_info = {'topic': topic_name}
        return {**node_handle_info, **subscription_info}

    def get_service_handle_info(
        self, service_handle: int
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
        self, client_handle: int
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
        self, node_handle: int
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

    def format_info_dict(self, info_dict: Mapping[str, Any]) -> str:
        return ', '.join([f'{key}: {val}' for key, val in info_dict.items()])
