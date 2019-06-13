# Data model

import pandas as pd


class DataModel():
    """
    Container to model pre-processed data for analysis.

    Contains data for an analysis to use. This is a middleground between trace events data and the
    output data of an analysis. This aims to represent the data in a ROS-aware way.
    It uses pandas DataFrames directly.
    """

    def __init__(self):
        # Objects (one-time events, usually when something is created)
        self._contexts = pd.DataFrame(columns=['context_handle', 'timestamp', 'pid'])
        self._contexts.set_index(['context_handle'], inplace=True, drop=True)
        self._nodes = pd.DataFrame(columns=['node_handle', 'timestamp', 'tid', 'rmw_handle', 'name', 'namespace'])
        self._nodes.set_index(['node_handle'], inplace=True, drop=True)
        self._publishers = pd.DataFrame(columns=['publisher_handle', 'timestamp', 'node_handle', 'rmw_handle', 'topic_name', 'depth'])
        self._publishers.set_index(['publisher_handle'], inplace=True, drop=True)
        self._subscriptions = pd.DataFrame(columns=['subscription_handle', 'timestamp', 'node_handle', 'rmw_handle', 'topic_name', 'depth'])
        self._subscriptions.set_index(['subscription_handle'], inplace=True, drop=True)
        self._services = pd.DataFrame(columns=['service_handle', 'timestamp', 'node_handle', 'rmw_handle', 'service_name'])
        self._services.set_index(['service_handle'], inplace=True, drop=True)
        self._clients = pd.DataFrame(columns=['client_handle', 'timestamp', 'node_handle', 'rmw_handle', 'service_name'])
        self._clients.set_index(['client_handle'], inplace=True, drop=True)
        self._timers = pd.DataFrame(columns=['timer_handle', 'timestamp', 'period'])
        self._timers.set_index(['timer_handle'], inplace=True, drop=True)

        self._callback_objects = pd.DataFrame(columns=['handle', 'timestamp', 'callback_object'])
        self._callback_objects.set_index(['handle'], inplace=True, drop=True)
        self._callback_symbols = pd.DataFrame(columns=['callback_object', 'timestamp', 'symbol'])
        self._callback_symbols.set_index(['callback_object'], inplace=True, drop=True)

        # Events (multiple instances, may not have a meaningful index)
        self._callbacks_instances = pd.DataFrame(columns=['callback_object', 'timestamp', 'duration', 'intra_process'])

    def add_context(self, context_handle, timestamp, pid):
        self._contexts.loc[context_handle] = [timestamp, pid]

    def add_node(self, node_handle, timestamp, tid, rmw_handle, name, namespace):
        self._nodes.loc[node_handle] = [timestamp, tid, rmw_handle, name, namespace]

    def add_publisher(self, publisher_handle, timestamp, node_handle, rmw_handle, topic_name, depth):
        self._publishers.loc[publisher_handle] = [timestamp, node_handle, rmw_handle, topic_name, depth]

    def add_subscription(self, subscription_handle, timestamp, node_handle, rmw_handle, topic_name, depth):
        self._subscriptions.loc[subscription_handle] = [timestamp, node_handle, rmw_handle, topic_name, depth]

    def add_service(self, service_handle, timestamp, node_handle, rmw_handle, service_name):
        self._services.loc[service_handle] = [timestamp, node_handle, rmw_handle, service_name]

    def add_client(self, client_handle, timestamp, node_handle, rmw_handle, service_name):
        self._clients.loc[client_handle] = [timestamp, node_handle, rmw_handle, service_name]

    def add_timer(self, timer_handle, timestamp, period):
        self._timers.loc[timer_handle] = [timestamp, period]

    def add_callback_object(self, handle, timestamp, callback_object):
        self._callback_objects.loc[handle] = [timestamp, callback_object]

    def add_callback_symbol(self, callback_object, timestamp, symbol):
        self._callback_symbols.loc[callback_object] = [timestamp, symbol]
    
    def add_callback_instance(self, callback_object, timestamp, duration, intra_process):
        self._callbacks_instances = self._callbacks_instances.append({'callback_object': callback_object, 'timestamp': timestamp, 'duration': duration, 'intra_process': intra_process}, ignore_index=True)

    def print(self):
        """Debug method to print every contained df."""
        print('====================DATA MODEL====================')
        print(f'Contexts:\n{self._contexts.to_string()}')
        print()
        print(f'Nodes:\n{self._nodes.to_string()}')
        print()
        print(f'Publishers:\n{self._publishers.to_string()}')
        print()
        print(f'Subscriptions:\n{self._subscriptions.to_string()}')
        print()
        print(f'Services:\n{self._services.to_string()}')
        print()
        print(f'Clients:\n{self._clients.to_string()}')
        print()
        print(f'Timers:\n{self._timers.to_string()}')
        print()
        print(f'Callback objects:\n{self._callback_objects.to_string()}')
        print()
        print(f'Callback symbols:\n{self._callback_symbols.to_string()}')
        print()
        print(f'Callback instances:\n{self._callbacks_instances.to_string()}')
        print('==================================================')
