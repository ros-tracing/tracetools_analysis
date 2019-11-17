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

from pandas import DataFrame

from . import DataModelUtil
from ..data_model.cpu_time import CpuTimeDataModel


class CpuTimeDataModelUtil(DataModelUtil):
    """CPU time data model utility class."""

    def __init__(
        self,
        data_model: CpuTimeDataModel,
    ) -> None:
        """
        Constructor.

        :param data_model: the data model object to use
        """
        super().__init__(data_model)

    def get_time_per_thread(self) -> DataFrame:
        """Get a DataFrame of total duration for each thread."""
        return self.data.times.loc[:, ['tid', 'duration']].groupby(by='tid').sum()
