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

"""Module with CTF to pickle conversion functions."""

from pickle import Pickler

from tracetools_read.trace import event_to_dict
from tracetools_read.trace import get_trace_ctf_events


def ctf_to_pickle(trace_directory: str, target: Pickler) -> int:
    """
    Load CTF trace, convert events, and dump to a pickle file.

    :param trace_directory: the trace directory
    :param target: the target file to write to
    :return: the number of events written
    """
    ctf_events = get_trace_ctf_events(trace_directory)

    count = 0
    count_written = 0

    for event in ctf_events:
        count += 1

        pod = event_to_dict(event)
        target.dump(pod)
        count_written += 1

    return count_written


def convert(trace_directory: str, output_file_path: str) -> int:
    """
    Convert CTF trace to pickle file.

    :param trace_directory: the trace directory
    :param output_file_path: the path to the output file that will be created
    :return: the number of events written to the output file
    """
    with open(output_file_path, 'wb') as f:
        p = Pickler(f, protocol=4)
        count = ctf_to_pickle(trace_directory, p)

    return count
