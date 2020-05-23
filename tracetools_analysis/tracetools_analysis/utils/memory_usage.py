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
from typing import List
from typing import Optional
from typing import Union

from pandas import DataFrame

from . import DataModelUtil
from ..data_model.memory_usage import MemoryUsageDataModel
from ..processor.memory_usage import KernelMemoryUsageHandler
from ..processor.memory_usage import UserspaceMemoryUsageHandler


class MemoryUsageDataModelUtil(DataModelUtil):
    """Memory usage data model utility class."""

    def __init__(
        self,
        *,
        userspace: Union[MemoryUsageDataModel, UserspaceMemoryUsageHandler, None] = None,
        kernel: Union[MemoryUsageDataModel, KernelMemoryUsageHandler, None] = None,
    ) -> None:
        """
        Create a MemoryUsageDataModelUtil.

        At least one non-`None` `MemoryUsageDataModel` must be given.

        :param userspace: the userspace data model object to use or the event handler
        :param kernel: the kernel data model object to use or the event handler
        """
        if userspace is None and kernel is None:
            raise RuntimeError('must provide at least one (userspace or kernel) data model!')

        # Not giving any model to the base class; we'll own them ourselves
        super().__init__(None)

        self.data_ust = userspace.data \
            if isinstance(userspace, UserspaceMemoryUsageHandler) else userspace
        self.data_kernel = kernel.data \
            if isinstance(kernel, KernelMemoryUsageHandler) else kernel

    @staticmethod
    def format_size(size: int, precision: int = 2):
        """
        Format a memory size to a string with a units suffix.

        From: https://stackoverflow.com/a/32009595/6476709

        :param size: the memory size, in bytes
        :param precision: the number of digits to display after the period
        """
        suffixes = ['B', 'KB', 'MB', 'GB', 'TB']
        suffix_index = 0
        mem_size = float(size)
        while mem_size > 1024.0 and suffix_index < 4:
            # Increment the index of the suffix
            suffix_index += 1
            # Apply the division
            mem_size = mem_size / 1024.0
        return f'{mem_size:.{precision}f} {suffixes[suffix_index]}'

    def get_max_memory_usage_per_tid(self) -> DataFrame:
        """
        Get the maximum memory usage per tid.

        :return dataframe with maximum memory usage (userspace & kernel) per tid
        """
        tids_ust = None
        tids_kernel = None
        ust_memory_usage_dfs = self.get_absolute_userspace_memory_usage_by_tid()
        if ust_memory_usage_dfs is not None:
            tids_ust = set(ust_memory_usage_dfs.keys())
        kernel_memory_usage_dfs = self.get_absolute_kernel_memory_usage_by_tid()
        if kernel_memory_usage_dfs is not None:
            tids_kernel = set(kernel_memory_usage_dfs.keys())
        # Use only the userspace tid values if available, otherwise use the kernel tid values
        tids = tids_ust or tids_kernel
        # Should not happen, since it is checked in __init__
        if tids is None:
            raise RuntimeError('no data')
        data = [
            [
                tid,
                self.format_size(ust_memory_usage_dfs[tid]['memory_usage'].max(), precision=1)
                if ust_memory_usage_dfs is not None
                and ust_memory_usage_dfs.get(tid) is not None
                else None,
                self.format_size(kernel_memory_usage_dfs[tid]['memory_usage'].max(), precision=1)
                if kernel_memory_usage_dfs is not None
                and kernel_memory_usage_dfs.get(tid) is not None
                else None,
            ]
            for tid in tids
        ]
        return DataFrame(data, columns=['tid', 'max_memory_usage_ust', 'max_memory_usage_kernel'])

    def get_absolute_userspace_memory_usage_by_tid(self) -> Optional[Dict[int, DataFrame]]:
        """
        Get absolute userspace memory usage over time per tid.

        :return (tid -> DataFrame of absolute memory usage over time)
        """
        if self.data_ust is None:
            return None
        return self._get_absolute_memory_usage_by_tid(self.data_ust)

    def get_absolute_kernel_memory_usage_by_tid(self) -> Optional[Dict[int, DataFrame]]:
        """
        Get absolute kernel memory usage over time per tid.

        :return (tid -> DataFrame of absolute memory usage over time)
        """
        if self.data_kernel is None:
            return None
        return self._get_absolute_memory_usage_by_tid(self.data_kernel)

    def _get_absolute_memory_usage_by_tid(
        self,
        data_model: MemoryUsageDataModel,
    ) -> Dict[int, DataFrame]:
        previous: Dict[int, int] = defaultdict(int)
        data: Dict[int, List[Dict[str, int]]] = defaultdict(list)
        for index, row in data_model.memory_diff.iterrows():
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
