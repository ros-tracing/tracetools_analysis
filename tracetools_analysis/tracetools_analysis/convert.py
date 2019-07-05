#!/usr/bin/env python3
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

"""Entrypoint/script to convert CTF trace data to a pickle file."""

import argparse
import os
import time

from tracetools_analysis.conversion import ctf


def parse_args():
    parser = argparse.ArgumentParser(
        description='Convert CTF trace data to a pickle file.')
    parser.add_argument(
        'trace_directory', help='the path to the main CTF trace directory')
    parser.add_argument(
        '--pickle-path', '-p',
        help='the path to the target pickle file to generate (default: $trace_directory/pickle)')
    args = parser.parse_args()
    if args.pickle_path is None:
        args.pickle_path = os.path.join(args.trace_directory, 'pickle')
    return args


def main():
    args = parse_args()

    trace_directory = args.trace_directory
    pickle_target_path = args.pickle_path

    print(f'importing trace directory: {trace_directory}')
    start_time = time.time()
    count = ctf.convert(trace_directory, pickle_target_path)
    time_diff = time.time() - start_time
    print(f'converted {count} events in {time_diff * 1000:.2f} ms')
    print(f'pickle written to: {pickle_target_path}')
