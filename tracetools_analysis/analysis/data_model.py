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

        self._services = pd.DataFrame(columns=[])
        self._clients = pd.DataFrame(columns=[])
        self._timers = pd.DataFrame(columns=[])

        # Events
        # TODO

    def add_context(self, context_handle, timestamp, pid):
        self._contexts.loc[context_handle] = [timestamp, pid]
        # self._contexts = self._contexts.append({'context_handle': context_handle, 'timestamp': timestamp, 'pid': pid}, ignore_index=True)

    def add_node(self, node_handle, timestamp, tid, rmw_handle, name, namespace):
        self._nodes.loc[node_handle] = [timestamp, tid, rmw_handle, name, namespace]

    def add_publisher(self, publisher_handle, timestamp, node_handle, rmw_handle, topic_name, depth):
        self._publishers.loc[publisher_handle] = [timestamp, node_handle, rmw_handle, topic_name, depth]

    def add_subscription(self, subscription_handle, timestamp, node_handle, rmw_handle, topic_name, depth):
        self._subscriptions.loc[subscription_handle] = [timestamp, node_handle, rmw_handle, topic_name, depth]

    def print(self):
        """Debug method to print every contained df."""
        print('====================DATA MODEL====================')
        print(f'Contexts:\n{self._contexts.to_string()}')
        print()
        print(f'Nodes:\n{self._nodes.to_string()}')
        print()
        print(f'Publishers:\n{self._publishers.to_string()}')
        print()
        print(f'Subscription:\n{self._subscriptions.to_string()}')
        print()
        print(f'Services:\n{self._services.to_string()}')
        print()
        print(f'Clients:\n{self._clients.to_string()}')
        print()
        print(f'Timers:\n{self._timers.to_string()}')
        print('==================================================')
