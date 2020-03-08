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

"""Module for CPU time events processing."""

from typing import Dict
from typing import Set

from tracetools_read import get_field

from . import EventHandler
from . import EventMetadata
from . import HandlerMap
from ..data_model.cpu_time import CpuTimeDataModel


class CpuTimeHandler(EventHandler):
    """
    Handler that extracts data for CPU time.

    It extracts timestamps from sched_switch events to later compute CPU time per thread.
    """

    def __init__(
        self,
        **kwargs,
    ) -> None:
        """Create a CpuTimeHandler."""
        # Link event to handling method
        handler_map: HandlerMap = {
            'sched_switch':
                self._handle_sched_switch,
        }
        super().__init__(
            handler_map=handler_map,
            data_model=CpuTimeDataModel(),
            **kwargs,
        )

        # Temporary buffers
        # cpu_id -> start timestamp of the running thread
        self._cpu_start: Dict[int, int] = {}

    @staticmethod
    def required_events() -> Set[str]:
        return {
            'sched_switch',
        }

    @property
    def data(self) -> CpuTimeDataModel:
        return super().data  # type: ignore

    def _handle_sched_switch(
        self, event: Dict, metadata: EventMetadata
    ) -> None:
        timestamp = metadata.timestamp
        cpu_id = metadata.cpu_id
        # Process if there is a previous thread timestamp
        # TODO instead of discarding it, use first ever timestamp
        # of the trace (with TraceCollection.timestamp_begin)
        prev_timestamp = self._cpu_start.get(cpu_id, None)
        if prev_timestamp is not None:
            prev_tid = get_field(event, 'prev_tid')
            duration = timestamp - prev_timestamp
            self.data.add_duration(prev_tid, prev_timestamp, duration, cpu_id)
        # Set start timestamp of next thread
        self._cpu_start[cpu_id] = timestamp
