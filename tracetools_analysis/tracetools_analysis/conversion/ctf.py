# CTF to pickle conversion

from pickle import Pickler

from tracetools_read import utils


def ctf_to_pickle(trace_directory: str, target: Pickler) -> int:
    """
    Load CTF trace and convert to a pickle file.

    :param trace_directory: the main/top trace directory
    :param target: the target pickle file to write to
    :return: the number of events written
    """
    # add traces
    print(f'Importing trace directory: {trace_directory}')
    ctf_events = utils._get_trace_ctf_events(trace_directory)

    count = 0
    count_written = 0
    # count_pid_matched = 0
    # traced = set()

    # PID_KEYS = ['vpid', 'pid']
    for event in ctf_events:
        count += 1
        # pid = None
        # for key in PID_KEYS:
        #     if key in event.keys():
        #         pid = event[key]
        #         break

        # Write all for now
        pod = utils.event_to_dict(event)
        target.dump(pod)
        count_written += 1

    return count_written
