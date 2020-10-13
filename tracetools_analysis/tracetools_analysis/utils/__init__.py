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

from datetime import datetime as dt
from typing import List
from typing import Optional
from typing import Union

import numpy as np
from pandas import DataFrame

from ..data_model import DataModel
from ..processor import EventHandler


class DataModelUtil():
    """
    Base data model util class, which provides functions to get more info about a data model.

    This class provides basic util functions.
    """

    def __init__(
        self,
        data_object: Union[DataModel, EventHandler, None],
    ) -> None:
        """
        Create a DataModelUtil.

        :param data_object: the data model or the event handler which has a data model
        """
        self.__data = data_object.data if isinstance(data_object, EventHandler) else data_object

    @property
    def data(self) -> Optional[DataModel]:
        return self.__data

    @staticmethod
    def convert_time_columns(
        original: DataFrame,
        columns_ns_to_ms: Union[List[str], str] = [],
        columns_ns_to_datetime: Union[List[str], str] = [],
        inplace: bool = True,
    ) -> DataFrame:
        """
        Convert time columns from nanoseconds to either milliseconds or `datetime` objects.

        :param original: the original `DataFrame`
        :param columns_ns_to_ms: the column(s) for which to convert ns to ms
        :param columns_ns_to_datetime: the column(s) for which to convert ns to `datetime`
        :param inplace: whether to convert in place or to return a copy
        :return: the resulting `DataFrame`
        """
        if not isinstance(columns_ns_to_ms, list):
            columns_ns_to_ms = list(columns_ns_to_ms)
        if not isinstance(columns_ns_to_datetime, list):
            columns_ns_to_datetime = list(columns_ns_to_datetime)

        df = original if inplace else original.copy()
        # Convert from ns to ms
        if len(columns_ns_to_ms) > 0:
            df[columns_ns_to_ms] = df[columns_ns_to_ms].applymap(
                lambda t: t / 1000000.0 if not np.isnan(t) else t
            )
        # Convert from ns to ms + ms to datetime, as UTC
        if len(columns_ns_to_datetime) > 0:
            df[columns_ns_to_datetime] = df[columns_ns_to_datetime].applymap(
                lambda t: dt.utcfromtimestamp(t / 1000000000.0) if not np.isnan(t) else t
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
