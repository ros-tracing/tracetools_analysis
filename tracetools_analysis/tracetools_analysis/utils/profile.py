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

"""Module for profiling data model utils."""

from collections import defaultdict
from typing import Dict
from typing import List
from typing import Set
from typing import Union

from pandas import DataFrame

from . import DataModelUtil
from ..data_model.profile import ProfileDataModel
from ..processor.profile import ProfileHandler


class ProfileDataModelUtil(DataModelUtil):
    """Profiling data model utility class."""

    def __init__(
        self,
        data_object: Union[ProfileDataModel, ProfileHandler],
    ) -> None:
        """
        Create a ProfileDataModelUtil.

        :param data_object: the data model or the event handler which has a data model
        """
        super().__init__(data_object)

    @property
    def data(self) -> ProfileDataModel:
        return super().data  # type: ignore

    def with_tid(
        self,
        tid: int,
    ) -> DataFrame:
        return self.data.times.loc[self.data.times['tid'] == tid]

    def get_tids(self) -> Set[int]:
        """Get the TIDs in the data model."""
        return set(self.data.times['tid'])

    def get_call_tree(
        self,
        tid: int,
    ) -> Dict[str, Set[str]]:
        depth_names = self.with_tid(tid)[
            ['depth', 'function_name', 'parent_name']
        ].drop_duplicates()
        # print(depth_names.to_string())
        tree: Dict[str, Set[str]] = defaultdict(set)
        for _, row in depth_names.iterrows():
            depth = row['depth']
            name = row['function_name']
            parent = row['parent_name']
            if depth == 0:
                tree[name]
            else:
                tree[parent].add(name)
        return dict(tree)

    def get_function_duration_data(
        self,
        tid: int,
    ) -> List[Dict[str, Union[int, str, DataFrame]]]:
        """Get duration data for each function."""
        tid_df = self.with_tid(tid)
        depth_names = tid_df[['depth', 'function_name', 'parent_name']].drop_duplicates()
        functions_data = []
        for _, row in depth_names.iterrows():
            depth = row['depth']
            name = row['function_name']
            parent = row['parent_name']
            data = tid_df.loc[
                (tid_df['depth'] == depth) &
                (tid_df['function_name'] == name)
            ][['start_timestamp', 'duration', 'actual_duration']]
            self.compute_column_difference(
                data,
                'duration',
                'actual_duration',
                'duration_difference',
            )
            functions_data.append({
                'depth': depth,
                'function_name': name,
                'parent_name': parent,
                'data': data,
            })
        return functions_data
