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
        suffixIndex = 0
        while size > 1024 and suffixIndex < 4:
            # Increment the index of the suffix
            suffixIndex += 1
            # Apply the division
            size = size / 1024.0
        return f'{size:.{precision}f} {suffixes[suffixIndex]}'

    def get_max_memory_usage_per_tid(self) -> DataFrame:
        """
        Get the maximum memory usage per tid.

        :return dataframe with maximum memory usage (userspace & kernel) per tid
        """
        if self.data_ust is not None:
            ust_memory_usage_dfs = self.get_absolute_userspace_memory_usage_by_tid()
            tids_ust = set(ust_memory_usage_dfs.keys())
        if self.data_kernel is not None:
            kernel_memory_usage_dfs = self.get_absolute_kernel_memory_usage_by_tid()
            tids_kernel = set(kernel_memory_usage_dfs.keys())
        # Use only the userspace tid values if available, otherwise use the kernel tid values
        tids = tids_ust if self.data_ust is not None else tids_kernel
        data = [
            [
                tid,
                self.format_size(ust_memory_usage_dfs[tid]['memory_usage'].max(), precision=1)
                if self.data_ust is not None
                else None,
                self.format_size(kernel_memory_usage_dfs[tid]['memory_usage'].max(), precision=1)
                if self.data_kernel is not None and ust_memory_usage_dfs.get(tid) is not None
                else None,
            ]
            for tid in tids
        ]
        return DataFrame(data, columns=['tid', 'max_memory_usage_ust', 'max_memory_usage_kernel'])

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
        data_model: MemoryUsageDataModel,
    ) -> Dict[int, DataFrame]:
        previous = defaultdict(int)
        data = defaultdict(list)
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
