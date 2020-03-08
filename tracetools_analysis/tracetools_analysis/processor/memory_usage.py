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

"""Module for memory usage events processing."""

from typing import Dict
from typing import Set

from tracetools_read import get_field

from . import EventHandler
from . import EventMetadata
from . import HandlerMap
from ..data_model.memory_usage import MemoryUsageDataModel


class MemoryUsageHandler(EventHandler):
    """Generic handler for memory usage."""

    def __init__(
        self,
        **kwargs,
    ) -> None:
        if type(self) is MemoryUsageHandler:
            raise RuntimeError('Do not instantiate directly!')
        super().__init__(
            data_model=MemoryUsageDataModel(),
            **kwargs,
        )

    @property
    def data(self) -> MemoryUsageDataModel:
        return super().data  # type: ignore

    def _update(
        self,
        timestamp: int,
        tid: int,
        memory_difference: int,
    ) -> None:
        # Add to data model
        self.data.add_memory_difference(timestamp, tid, memory_difference)


class UserspaceMemoryUsageHandler(MemoryUsageHandler):
    """
    Handler that extracts userspace memory usage data.

    It uses the following events:
        * lttng_ust_libc:malloc
        * lttng_ust_libc:calloc
        * lttng_ust_libc:realloc
        * lttng_ust_libc:free
        * lttng_ust_libc:memalign
        * lttng_ust_libc:posix_memalign

    The above events are generated when LD_PRELOAD-ing liblttng-ust-libc-wrapper.so, see:
    https://lttng.org/docs/v2.10/#doc-liblttng-ust-libc-pthread-wrapper

    Implementation inspired by Trace Compass' implementation:
    https://git.eclipse.org/c/tracecompass/org.eclipse.tracecompass.git/tree/lttng/org.eclipse.tracecompass.lttng2.ust.core/src/org/eclipse/tracecompass/internal/lttng2/ust/core/analysis/memory/UstMemoryStateProvider.java#n161
    """

    def __init__(
        self,
        **kwargs,
    ) -> None:
        # Link event to handling method
        handler_map: HandlerMap = {
            'lttng_ust_libc:malloc':
                self._handle_malloc,
            'lttng_ust_libc:calloc':
                self._handle_calloc,
            'lttng_ust_libc:realloc':
                self._handle_realloc,
            'lttng_ust_libc:free':
                self._handle_free,
            'lttng_ust_libc:memalign':
                self._handle_memalign,
            'lttng_ust_libc:posix_memalign':
                self._handle_posix_memalign,
        }
        super().__init__(
            handler_map=handler_map,
            **kwargs,
        )

        # Temporary buffers
        # pointer -> current memory size
        # (used to know keep track of the memory size allocated at a given pointer)
        self._memory: Dict[int, int] = {}

    @staticmethod
    def required_events() -> Set[str]:
        return {
            'lttng_ust_libc:malloc',
            'lttng_ust_libc:free',
        }

    def _handle_malloc(
        self, event: Dict, metadata: EventMetadata
    ) -> None:
        ptr = get_field(event, 'ptr')
        if ptr != 0:
            size = get_field(event, 'size')
            self._handle(event, metadata, ptr, size)

    def _handle_calloc(
        self, event: Dict, metadata: EventMetadata
    ) -> None:
        ptr = get_field(event, 'ptr')
        if ptr != 0:
            nmemb = get_field(event, 'nmemb')
            size = get_field(event, 'size')
            self._handle(event, metadata, ptr, size * nmemb)

    def _handle_realloc(
        self, event: Dict, metadata: EventMetadata
    ) -> None:
        ptr = get_field(event, 'ptr')
        if ptr != 0:
            new_ptr = get_field(event, 'in_ptr')
            size = get_field(event, 'size')
            self._handle(event, metadata, ptr, 0)
            self._handle(event, metadata, new_ptr, size)

    def _handle_free(
        self, event: Dict, metadata: EventMetadata
    ) -> None:
        ptr = get_field(event, 'ptr')
        if ptr != 0:
            self._handle(event, metadata, ptr, 0)

    def _handle_memalign(
        self, event: Dict, metadata: EventMetadata
    ) -> None:
        ptr = get_field(event, 'ptr')
        if ptr != 0:
            size = get_field(event, 'size')
            self._handle(event, metadata, ptr, size)

    def _handle_posix_memalign(
        self, event: Dict, metadata: EventMetadata
    ) -> None:
        ptr = get_field(event, 'out_ptr')
        if ptr != 0:
            size = get_field(event, 'size')
            self._handle(event, metadata, ptr, size)

    def _handle(
        self,
        event: Dict,
        metadata: EventMetadata,
        ptr: int,
        size: int,
    ) -> None:
        timestamp = metadata.timestamp
        tid = metadata.tid

        memory_difference = size
        # Store the size allocated for the given pointer
        if memory_difference != 0:
            self._memory[ptr] = memory_difference
        else:
            # Othersize, if size is 0, it means it was deleted
            # Try to fetch the size stored previously
            allocated_memory = self._memory.get(ptr, None)
            if allocated_memory is not None:
                memory_difference = -allocated_memory

        self._update(timestamp, tid, memory_difference)


class KernelMemoryUsageHandler(MemoryUsageHandler):
    """
    Handler that extracts userspace memory usage data.

    It uses the following events:
        * kmem_mm_page_alloc
        * kmem_mm_page_free

    Implementation inspired by Trace Compass' implementation:
    https://git.eclipse.org/c/tracecompass/org.eclipse.tracecompass.git/tree/analysis/org.eclipse.tracecompass.analysis.os.linux.core/src/org/eclipse/tracecompass/analysis/os/linux/core/kernelmemoryusage/KernelMemoryStateProvider.java#n84
    """

    PAGE_SIZE = 4096

    def __init__(
        self,
        **kwargs,
    ) -> None:
        # Link event to handling method
        handler_map: HandlerMap = {
            'kmem_mm_page_alloc':
                self._handle_malloc,
            'kmem_mm_page_free':
                self._handle_free,
        }
        super().__init__(
            handler_map=handler_map,
            **kwargs,
        )

    @staticmethod
    def required_events() -> Set[str]:
        return {
            'kmem_mm_page_alloc',
            'kmem_mm_page_free',
        }

    def _handle_malloc(
        self, event: Dict, metadata: EventMetadata
    ) -> None:
        self._handle(event, metadata, self.PAGE_SIZE)

    def _handle_free(
        self, event: Dict, metadata: EventMetadata
    ) -> None:
        self._handle(event, metadata, -self.PAGE_SIZE)

    def _handle(
        self,
        event: Dict,
        metadata: EventMetadata,
        inc: int,
    ) -> None:
        order = get_field(event, 'order')
        inc <<= order

        timestamp = metadata.timestamp
        tid = metadata.tid

        self._update(timestamp, tid, inc)
