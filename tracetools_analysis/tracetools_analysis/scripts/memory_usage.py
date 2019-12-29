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

from tracetools_analysis.loading import load_file
from tracetools_analysis.processor import Processor
from tracetools_analysis.processor.memory_usage import KernelMemoryUsageHandler
from tracetools_analysis.processor.memory_usage import UserspaceMemoryUsageHandler
from tracetools_analysis.processor.ros2 import Ros2Handler
from tracetools_analysis.utils.memory_usage import MemoryUsageDataModelUtil
from tracetools_analysis.utils.ros2 import Ros2DataModelUtil

from . import get_input_path


def main():
    input_path = get_input_path()

    events = load_file(input_path)
    ust_memory_handler = UserspaceMemoryUsageHandler()
    kernel_memory_handler = KernelMemoryUsageHandler()
    ros2_handler = Ros2Handler()
    Processor(ust_memory_handler, kernel_memory_handler, ros2_handler).process(events)

    memory_data_util = MemoryUsageDataModelUtil(
        userspace=ust_memory_handler.data,
        kernel=kernel_memory_handler.data,
    )
    ros2_data_util = Ros2DataModelUtil(ros2_handler.data)

    summary_df = memory_data_util.get_max_memory_usage_per_tid()
    tids = ros2_data_util.get_tids()
    filtered_df = summary_df.loc[summary_df['tid'].isin(tids)]
    print('\n' + filtered_df.to_string(index=False))
