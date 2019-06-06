# Model objects for LTTng traces/events

def get_field(event, field_name, default=None):
    return event.get(field_name, d=default)

def get_name(event):
    return get_field(event, '_name')


class EventMetadata():
    def __init__(self, event_name, pid, tid, timestamp, procname):
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
