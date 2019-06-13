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
        self._contexts = pd.DataFrame(columns=[])
        self._nodes = pd.DataFrame(columns=[])
        self._publishers = pd.DataFrame(columns=[])
        self._subscriptions = pd.DataFrame(columns=[])
        self._services = pd.DataFrame(columns=[])
        self._clients = pd.DataFrame(columns=[])
        self._timers = pd.DataFrame(columns=[])

        # Events
        # TODO


    def print(self):
        """Debug method to print every contained df."""
        print('====================DATA MODEL====================')
        print(f'Contexts:\n{self._contexts.to_string()}')
        print(f'Nodes:\n{self._nodes.to_string()}')
        print(f'Publishers:\n{self._publishers.to_string()}')
        print(f'Subscription:\n{self._subscriptions.to_string()}')
        print(f'Services:\n{self._services.to_string()}')
        print(f'Clients:\n{self._clients.to_string()}')
        print(f'Timers:\n{self._timers.to_string()}')
        print('==================================================')
