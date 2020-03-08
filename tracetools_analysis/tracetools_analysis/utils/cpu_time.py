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

"""Module for CPU time data model utils."""

from typing import Union

from pandas import DataFrame

from . import DataModelUtil
from ..data_model.cpu_time import CpuTimeDataModel
from ..processor.cpu_time import CpuTimeHandler


class CpuTimeDataModelUtil(DataModelUtil):
    """CPU time data model utility class."""

    def __init__(
        self,
        data_object: Union[CpuTimeDataModel, CpuTimeHandler],
    ) -> None:
        """
        Create a CpuTimeDataModelUtil.

        :param data_object: the data model or the event handler which has a data model
        """
        super().__init__(data_object)

    @property
    def data(self) -> CpuTimeDataModel:
        return super().data  # type: ignore

    def get_time_per_thread(self) -> DataFrame:
        """Get a DataFrame of total duration for each thread."""
        return self.data.times.loc[:, ['tid', 'duration']].groupby(by='tid').sum()
