
class Episode(tuple):

    def __init__(self, sequence_of_event_types):
        self.initialized = [None] * len(sequence_of_event_types)
        self.freq_count = 0
        self.relative_frequency = 0
        self.inwindow = None
        self.has_gaps = None# True / False
        self = sequence_of_event_types

    def __repr__(self, *args, **kwargs):
        return str(self.freq_count) + ' ' + super(Episode, self).__repr__()
        
    def reset_initialized(self):
        self.initialized = [None] * len(self)


def episode_frequences(event_sequence, collection_of_serial_episodes, window_width, only_full_windows, gaps_skipping):
    if len(event_sequence.sequence_of_events) == 0: 
        return collection_of_serial_episodes
    waits = {}
    for episode in collection_of_serial_episodes:
        episode.reset_initialized()
        waits.setdefault(episode[0], []).append((episode, 0))
    waits_copy = (waits).copy() 
    last_event_time = event_sequence.sequence_of_events[0].event_time
    beginsat = {} 
            
    event_dict = {}
    for event in event_sequence.sequence_of_events:
        event_dict.setdefault(event.event_time, []).append(event)
            
    for start in range(event_sequence.start-window_width+1, event_sequence.end+1):
        beginsat[start+window_width-1] = []
        if start + window_width - 1 < event_sequence.end:
            removes = []
            appends = []
            for event in event_dict.setdefault(start+window_width-1, []):#get hoopis?
                if not gaps_skipping and event.event_time-last_event_time > 1:
                    waits = waits_copy.copy()
                    last_event_time = event.event_time
                waits.setdefault(event.event_type, []).sort(key = lambda pair: pair[1], reverse = True)
                for episode, j in waits[event.event_type]: 
                    if j == 0:
                        episode.initialized[0] = event
                        if len(episode) == 1:
                            beginsat[episode.initialized[0].event_time].append(episode)
                            if episode.inwindow == None:
                                episode.inwindow = start
                                if only_full_windows and start < 0:
                                    episode.inwindow = 0
                        else:
                            appends.append((episode, 1))                    
                    elif j < len(episode) - 1: 
                        episode.initialized[j] = None
                        if episode.initialized[j-1] != None and episode.initialized[j-1].event_time > start: # seda saab täpsustada
                            episode.initialized[j] = episode.initialized[j-1]
                            appends.append((episode, j+1))
                        removes.append((episode, j))
                    elif j == len(episode) - 1:
                        if episode.initialized[j] == None and episode.initialized[j-1] != None and episode.initialized[j-1].event_time >= start:
                            episode.inwindow = start
                            if only_full_windows and start < 0:
                                episode.inwindow = 0
                        if episode.initialized[j-1] != None and episode.initialized[j-1].event_time >= start:
                            episode.initialized[j] = episode.initialized[j-1]
                            beginsat[episode.initialized[j].event_time].append(episode)
                        removes.append((episode, j))
                for episode, j in removes:
                    waits[episode[j]].remove((episode, j))            
                for episode, j in appends:
                    waits.setdefault(episode[j], []).append((episode, j))
        
        if start >= 0:
            for episode in beginsat[start]:
                if episode.initialized[-1] != None and episode.initialized[-1].event_time == start:
                    episode.freq_count += episode.initialized[-1].event_time - episode.inwindow + 1
                    if only_full_windows and start + window_width > event_sequence.end:
                        episode.freq_count -= start + window_width - event_sequence.end
                    episode.inwindow = None
                    episode.initialized[-1] = None
        if start in beginsat:
            del beginsat[start]

    return collection_of_serial_episodes

'''Algoritm 3
'''
def candidate_serial_episodes(F):
    if len(F) == 0: return [] 
    F_block_start = list(range(len(F)))
    for k in range(1, len(F)):
        if F[k - 1][:-1] == F[k][:-1]:
            F_block_start[k] = F_block_start[k - 1]
    C = []
    k = -1
    l = len(F[0])
    C_block_start = []
    for i in range(len(F)):
        episode = []
        b = []
        current_block_start = k + 1
        j = F_block_start[i]
        while j < len(F) and F_block_start[j] == F_block_start[i]:
            episode = F[i][:l] + F[j][l - 1:]
            
            next_event = True
            for y in range(l - 1):
                b = episode[:y] + episode[y + 1:]
                if b not in F:
                    next_event = False
                    continue
            if next_event:
                k += 1
                C.append(Episode(episode))
                C_block_start += [current_block_start]
            j += 1
    return C

def collection_of_frequent_episodes(event_sequences, window_width, min_frequency, 
                                    only_full_windows=False, gaps_skipping=True, **kwargs):
    """Find frequent serial episodes in event sequences
    
    Parameters
    ----------
    event_sequences: EventSequence, list of EventSequence
        One or more ``EventSequence`` to search for frequent episodes
    window_width: int
        Width of Winepi window
    min_frequency: float
        Minimal frequency (in range [0, 1]) of episodes to search for.
    only_full_windows: bool
        If True, the start of the first window is at the start of the sequence of events
        and the end of the last window is at the end of the sequence of events.
        If False, the end of the first window is at the start of the sequence of events
        and the start of the last window is at the end of the sequence of events.
    gaps_skipping: bool
        If True, all serial episodes are found
        If False, only serial episodes with no gaps are found
    number_of_examples: int
        Maximum number of examples attached with each episode
    event_types: list of hashable
        The event types that are searched for. 
        If not given, generated from event_sequences
    
    Returns
    -------
    (list of Episode, dict)
        List of episodes that have at least min_frequency.
        Dictionary that maps episodes to examples.
    """

    if not isinstance(event_sequences, list):
        event_sequences = [event_sequences]
    
    if 'event_types' in kwargs:
        event_types = kwargs['event_types']
    else:
        event_types = set([event.event_type 
                           for event_sequence in event_sequences 
                           for event in event_sequence.sequence_of_events])
    collection_of_episodes = [Episode([event_type]) for event_type in event_types]

    number_of_windows = (window_width - 1) * len(event_sequences)
    if only_full_windows:
        number_of_windows = -number_of_windows
    for event_sequence in event_sequences:
        number_of_windows += event_sequence.end - event_sequence.start
        if only_full_windows and event_sequence.end - event_sequence.start < window_width:
            print('Winepi: Event sequence shorter than window width.')

    frequent_episodes = []
    while len(collection_of_episodes) > 0:
        for event_sequence in event_sequences:
            episode_frequences(event_sequence, collection_of_episodes, window_width, only_full_windows, gaps_skipping)

        new_frequent_episodes = []
        for episode in collection_of_episodes:
            episode.relative_frequency = episode.freq_count / number_of_windows
            if episode.relative_frequency >= min_frequency:
                new_frequent_episodes.append(episode)
        collection_of_episodes = candidate_serial_episodes(new_frequent_episodes)
        frequent_episodes += new_frequent_episodes
    return frequent_episodes

