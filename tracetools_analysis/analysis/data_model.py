# Data model

import pandas as pd


class DataModel():
    """
    Container to model processed data.

    Contains data for an analysis to use.
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
