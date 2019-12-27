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

import sys

import pandas as pd

from tracetools_analysis.loading import load_file
from tracetools_analysis.processor import Processor
from tracetools_analysis.processor.memory_usage import MemoryUsageHandler
from tracetools_analysis.processor.ros2 import Ros2Handler
from tracetools_analysis.utils.memory_usage import MemoryUsageDataModelUtil
from tracetools_analysis.utils.ros2 import Ros2DataModelUtil


# From: https://stackoverflow.com/a/32009595/6476709
def format_memory_size(size: int, precision: int = 2):
    suffixes = ['B', 'KB', 'MB', 'GB', 'TB']
    suffixIndex = 0
    while size > 1024 and suffixIndex < 4:
        # Increment the index of the suffix
        suffixIndex += 1
        # Apply the division
        size = size / 1024.0
    return f'{size:.{precision}f} {suffixes[suffixIndex]}'


def main():
    if len(sys.argv) < 2:
        print('Syntax: <converted tracefile>')
        sys.exit(-1)
    file_path = sys.argv[1]

    events = load_file(file_path)
    memory_handler = MemoryUsageHandler()
    ros2_handler = Ros2Handler()
    Processor(memory_handler, ros2_handler).process(events)

    memory_data_util = MemoryUsageDataModelUtil(memory_handler.data)
    ros2_data_util = Ros2DataModelUtil(ros2_handler.data)

    memory_usage_dfs = memory_data_util.get_absolute_memory_usage_by_tid()
    tids = ros2_data_util.get_tids()

    data = [
        [
            tid,
            ros2_data_util.get_node_names_from_tid(tid),
            format_memory_size(memory_usage['memory_usage'].max(), precision=1),
        ]
        for tid, memory_usage in memory_usage_dfs.items()
        if tid in tids
    ]

    summary_df = pd.DataFrame(data, columns=['tid', 'node_names', 'max_memory_usage'])
    print('\n' + summary_df.to_string(index=False))
