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

"""Module for profile data model."""

from typing import Optional

import pandas as pd

from . import DataModel
from . import DataModelIntermediateStorage


class ProfileDataModel(DataModel):
    """
    Container to model pre-processed profiling data for analysis.

    Duration is the time difference between the function entry and the function exit.
    Actual duration is the actual time spent executing the function (or a child function).
    """

    def __init__(self) -> None:
        """Create a ProfileDataModel."""
        super().__init__()
        self._times: DataModelIntermediateStorage = []

    def add_duration(
        self,
        tid: int,
        depth: int,
        function_name: str,
        parent_name: Optional[str],
        start_timestamp: int,
        duration: int,
        actual_duration: int,
    ) -> None:
        self._times.append({
            'tid': tid,
            'depth': depth,
            'function_name': function_name,
            'parent_name': parent_name,
            'start_timestamp': start_timestamp,
            'duration': duration,
            'actual_duration': actual_duration,
        })

    def _finalize(self) -> None:
        self.times = pd.DataFrame.from_dict(self._times)

    def print_data(self) -> None:
        print('====================PROFILE DATA MODEL====================')
        tail = 20
        print(f'Times (tail={tail}):')
        print(self.times.tail(tail).to_string())
        print('==========================================================')
