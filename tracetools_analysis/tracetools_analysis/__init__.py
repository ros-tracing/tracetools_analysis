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

"""Tools for analysing trace data."""


def time_diff_to_str(
    time_diff: float,
) -> str:
    """
    Format time difference as a string.

    :param time_diff: the difference between two timepoints (e.g. `time.time()`)
    """
    if time_diff < 1.0:
        # ms
        return f'{time_diff * 1000:.0f} ms'
    elif time_diff < 60.0:
        # s
        return f'{time_diff:.1f} s'
    else:
        # m s
        return f'{time_diff // 60.0:.0f} m {time_diff % 60.0:.0f} s'
