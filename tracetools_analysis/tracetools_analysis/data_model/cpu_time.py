# Copyright 2019 Robert Bosch GmbH
# Copyright 2021 Christophe Bedard
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

"""Module for CPU time data model."""

import pandas as pd

from . import DataModel
from . import DataModelIntermediateStorage


class CpuTimeDataModel(DataModel):
    """
    Container to model pre-processed CPU time data for analysis.

    Contains every duration instance.
    """

    def __init__(self) -> None:
        """Create a CpuTimeDataModel."""
        super().__init__()
        self._times: DataModelIntermediateStorage = []

    def add_duration(
        self,
        tid: int,
        start_timestamp: int,
        duration: int,
        cpu_id: int,
    ) -> None:
        self._times.append({
            'tid': tid,
            'start_timestamp': start_timestamp,
            'duration': duration,
            'cpu_id': cpu_id,
        })

    def _finalize(self) -> None:
        self.times = pd.DataFrame.from_dict(self._times)

    def print_data(self) -> None:
        print('====================CPU TIME DATA MODEL====================')
        tail = 20
        print(f'Times (tail={tail}):')
        print(self.times.tail(tail).to_string())
        print('===========================================================')
