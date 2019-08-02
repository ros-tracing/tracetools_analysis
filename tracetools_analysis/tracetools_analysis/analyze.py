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

"""Entrypoint/script for analysis."""

import argparse
import time

from tracetools_analysis.loading import load_pickle
from tracetools_analysis.processor.cpu_time import CpuTimeHandler
from tracetools_analysis.processor.profile import ProfileHandler
from tracetools_analysis.utils import ProfileDataModelUtil


def parse_args():
    parser = argparse.ArgumentParser(description='Process a pickle file generated '
                                                 'from tracing and analyze the data.')
    parser.add_argument('pickle_file', help='the pickle file to import')
    return parser.parse_args()


def main():
    args = parse_args()
    pickle_filename = args.pickle_file

    start_time = time.time()

    events = load_pickle(pickle_filename)

    # cpu_handler = CpuTimeHandler.process(events)
    profile_handler = ProfileHandler.process(events)

    time_diff = time.time() - start_time
    print(f'processed {len(events)} events in {time_diff * 1000:.2f} ms')

    # cpu_handler.get_data_model().print_model()
    profile_handler.get_data_model().print_model()
    util = ProfileDataModelUtil(profile_handler.get_data_model())
    print(util.get_tids())
    util.get_stats(12616)
    print(util.get_call_tree(12616))
