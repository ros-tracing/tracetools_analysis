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

"""Module for pickle loading."""

import pickle
from typing import Dict
from typing import List


def load_pickle(pickle_file_path: str) -> List[Dict]:
    """
    Load pickle file containing converted trace events.

    :param pickle_file_path: the path to the pickle file to load
    :return: the list of events read from the file
    """
    events = []
    with open(pickle_file_path, 'rb') as f:
        p = pickle.Unpickler(f)
        while True:
            try:
                events.append(p.load())
            except EOFError:
                break  # we're done

    return events
