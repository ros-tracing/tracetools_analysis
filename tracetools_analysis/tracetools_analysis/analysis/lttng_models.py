# Model objects for LTTng traces/events


class EventMetadata():
    """Container for event metadata."""

    def __init__(self, event_name, pid, tid, timestamp, procname) -> None:
        self._event_name = event_name
        self._pid = pid
        self._tid = tid
        self._timestamp = timestamp
        self._procname = procname

    @property
    def event_name(self):
        return self._event_name

    @property
    def pid(self):
        return self._pid

    @property
    def tid(self):
        return self._tid

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def procname(self):
        return self._procname
