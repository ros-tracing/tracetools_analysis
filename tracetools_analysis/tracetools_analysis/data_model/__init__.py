# Copyright 2019 Robert Bosch GmbH
# Copyright 2021 Christophe Bedard
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

"""Base data model module."""

from typing import Any
from typing import Dict
from typing import List


DataModelIntermediateStorage = List[Dict[str, Any]]


class DataModel():
    """
    Container with pre-processed data for an analysis to use.

    Contains data for an analysis to use. This is a middleground between trace events data and the
    output data of an analysis.
    It uses native/simple Python data structures (e.g. lists of dicts) during processing, but
    converts them to pandas `DataFrame` at the end.
    """

    def __init__(self) -> None:
        self._finalized = False

    def finalize(self) -> None:
        """
        Finalize the data model.

        Call this once data is done being generated or added to the model.
        Finalization tasks are up to the inheriting/concrete class.
        """
        # Avoid calling it twice for data models which might be shared
        if not self._finalized:
            self._finalized = True
            self._finalize()

    def _finalize(self) -> None:
        """
        Do the finalization.

        Only called once.
        """
        raise NotImplementedError

    def print_data(self) -> None:
        """Print the data model."""
        raise NotImplementedError
