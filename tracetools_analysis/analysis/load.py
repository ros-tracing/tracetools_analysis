import pickle


def load_pickle(pickle_file_path):
    """
    Load pickle file containing converted trace events.

    :param pickle_file_path (str): the path to the pickle file to load
    :return list(dict): the list of events (dicts) read from the file
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
