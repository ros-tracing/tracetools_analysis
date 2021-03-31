#! /usr/bin/python
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

import numpy as np
import pandas as pd

from tracetools_analysis.loading import load_file
from tracetools_analysis.processor.ros2 import Ros2Handler
from tracetools_analysis.utils.ros2 import Ros2DataModelUtil

from . import get_input_path


removals = [
    'void (', 'rclcpp::', 'std::shared_ptr<', '>', '::msg'
]
replaces = [
    ('?)', '?')
]


def format_fn(fname: str):
    for r in removals:
        fname = fname.replace(r, '')
    for a, b in replaces:
        fname = fname.replace(a, b)

    return fname


def main():
    input_path = get_input_path()

    events = load_file(input_path)
    handler = Ros2Handler.process(events)
    du = Ros2DataModelUtil(handler.data)

    stat_data = []
    for ptr, name in du.get_callback_symbols().items():
        # Convert to milliseconds to display it
        durations = du.get_callback_durations(ptr)['duration'] * 1000 / np.timedelta64(1, 's')
        stat_data.append((
            durations.count(),
            durations.sum(),
            durations.mean(),
            durations.std(),
            format_fn(name),
        ))

    stat_df = pd.DataFrame(
        columns=['Count', 'Sum (ms)', 'Mean (ms)', 'Std', 'Name'],
        data=stat_data,
    )
    print(stat_df.sort_values(by='Sum (ms)', ascending=False).to_string())
