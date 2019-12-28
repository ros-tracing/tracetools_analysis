# Copyright 2019 Apex.AI, Inc.
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

"""Module for memory usage data model utils."""

from collections import defaultdict
from typing import Dict

from pandas import DataFrame

from . import DataModelUtil
from ..data_model.memory_usage import MemoryUsageDataModel


class MemoryUsageDataModelUtil(DataModelUtil):
    """Memory usage data model utility class."""

    def __init__(
        self,
        *,
        data_model_userspace: MemoryUsageDataModel = None,
        data_model_kernel: MemoryUsageDataModel = None,
    ) -> None:
        """
        Create a MemoryUsageDataModelUtil.

        At least one non-`None` `MemoryUsageDataModel` must be given

        :param data_model_userspace: the userspace data model object to use
        :param data_model_kernel: the kernel data model object to use
        """
        # Not giving any model to the base class; we'll own them ourselves
        super().__init__(None)

        if data_model_userspace is None and data_model_kernel is None:
            raise RuntimeError('must provide at least one (userspace or kernel) data model!')

        self.data_ust = data_model_userspace
        self.data_kernel = data_model_kernel

    def get_absolute_userspace_memory_usage_by_tid(self) -> Dict[int, DataFrame]:
        """
        Get absolute userspace memory usage over time per tid.

        :return (tid -> DataFrame of absolute memory usage over time)
        """
        return self._get_absolute_memory_usage_by_tid(self.data_ust)

    def get_absolute_kernel_memory_usage_by_tid(self) -> Dict[int, DataFrame]:
        """
        Get absolute kernel memory usage over time per tid.

        :return (tid -> DataFrame of absolute memory usage over time)
        """
        return self._get_absolute_memory_usage_by_tid(self.data_kernel)

    def _get_absolute_memory_usage_by_tid(
        self,
        data: MemoryUsageDataModel,
    ) -> Dict[int, DataFrame]:
        previous = defaultdict(int)
        data = defaultdict(list)
        for index, row in self.data.memory_diff.iterrows():
            timestamp = row['timestamp']
            tid = int(row['tid'])
            diff = row['memory_diff']
            previous_value = previous[tid]
            next_value = previous_value + diff
            data[tid].append({
                'timestamp': timestamp,
                'tid': tid,
                'memory_usage': previous_value,
            })
            data[tid].append({
                'timestamp': timestamp,
                'tid': tid,
                'memory_usage': next_value,
            })
            previous[tid] = next_value
        return {
            tid: self.convert_time_columns(
                DataFrame(data[tid], columns=['timestamp', 'tid', 'memory_usage']),
                columns_ns_to_datetime=['timestamp'],
                inplace=True,
            )
            for tid in data
        }
