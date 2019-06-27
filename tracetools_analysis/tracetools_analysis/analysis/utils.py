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

"""Module for data model utility class."""

from typing import Mapping

from pandas import DataFrame

from .data_model import DataModel


class DataModelUtil():
    """
    Data model utility class.

    Provides functions to get info on a data model.
    """

    def __init__(self, data_model: DataModel) -> None:
        """
        Constructor.

        :param data_model: the data model object to use
        """
        self._data = data_model

    def get_callback_symbols(self) -> Mapping[int, str]:
        """
        Get mappings between a callback object and its resolved symbol.

        :return: the map
        """
        callback_instances = self._data.callback_instances
        callback_symbols = self._data.callback_symbols

        # Get a list of callback objects
        callback_objects = set(callback_instances['callback_object'])
        # Get their symbol
        return {obj: callback_symbols.loc[obj, 'symbol'] for obj in callback_objects}

    def get_callback_durations(self, callback_obj: int) -> DataFrame:
        """
        Get durations of callback instances for a given callback object.

        :param callback_obj: a callback object value
        :return: a dataframe containing the durations of all callback instances for that object
        """
        return self._data.callback_instances.loc[
            self._data.callback_instances.loc[:, 'callback_object'] == callback_obj,
            :
        ]
