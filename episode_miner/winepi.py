"""A partial implementation of Winepi algorithm described by Mannila, Toivonen 
and Verkamo in *Discovery of Frequent Episodes in Event Sequences*, 1997.
"""

from episode_miner.event_sequence import EventSequence

class Episode(tuple):
    """An episode is a sequence of event types.
    
    The Winepi algorithm determines the relative and absolute support of episode
    in sequence of events.
    """

    def __init__(self, sequence_of_event_types):
        """Initialize a new Episode instance.
        """
        self._initialized = [None] * len(sequence_of_event_types)
        self._inwindow = None
        self.abs_support = 0
        self.rel_support = 0
        self.allow_intermediate_events = None
        self = sequence_of_event_types

    def __repr__(self, *args, **kwargs):
        return str(self.abs_support) + ' ' + super(Episode, self).__repr__()
        
    def reset_initialized(self):
        self._initialized = [None] * len(self)

    def reset_support(self):
        self.abs_support = 0
        self.rel_support = 0


def episode_frequences(event_sequence, collection_of_serial_episodes, 
                       window_width, only_full_windows, 
                       allow_intermediate_events):
    """The central algorithm of Winepi.
    """
    if len(event_sequence.sequence_of_events) == 0: 
        return collection_of_serial_episodes
    waits = {}
    for episode in collection_of_serial_episodes:
        episode.reset_initialized()
        waits.setdefault(episode[0], []).append((episode, 0))
    waits_init = {}
    for key in waits:
        waits_init[key] = waits[key].copy()          

    beginsat = {} 
            
    event_dict = {}
    for event in event_sequence.sequence_of_events:
        event_dict.setdefault(event.event_time, []).append(event)
            
    for start in range(event_sequence.start-window_width+1, event_sequence.end+1):
        beginsat[start+window_width-1] = []
        if start + window_width - 1 < event_sequence.end:
            removes = []
            appends = []
            event_in_dict = False
            for event in event_dict.setdefault(start+window_width-1, []):#get hoopis?
                event_in_dict = True
                waits.setdefault(event.event_type, []).sort(key = lambda pair: pair[1], reverse = True)
                for episode, j in waits[event.event_type]: 
                    if j == 0:
                        episode._initialized[0] = event
                        if len(episode) == 1:
                            beginsat[episode._initialized[0].event_time].append(episode)
                            if episode._inwindow == None:
                                episode._inwindow = start
                                if only_full_windows and start < 0:
                                    episode._inwindow = 0
                        else:
                            appends.append((episode, 1))                    
                    elif j < len(episode) - 1: 
                        episode._initialized[j] = None
                        if episode._initialized[j-1] != None and episode._initialized[j-1].event_time > start: # seda saab täpsustada
                            episode._initialized[j] = episode._initialized[j-1]
                            appends.append((episode, j+1))
                        removes.append((episode, j))
                    elif j == len(episode) - 1:
                        if episode._initialized[j] == None and episode._initialized[j-1] != None and episode._initialized[j-1].event_time >= start:
                            episode._inwindow = start
                            if only_full_windows and start < 0:
                                episode._inwindow = 0
                        if episode._initialized[j-1] != None and episode._initialized[j-1].event_time >= start:
                            episode._initialized[j] = episode._initialized[j-1]
                            beginsat[episode._initialized[j].event_time].append(episode)
                        removes.append((episode, j))
            if event_in_dict:
                if allow_intermediate_events:
                    for episode, j in removes:
                        waits[episode[j]].remove((episode, j))
                else:
                    waits = {}
                    for key in waits_init:
                        waits[key] = waits_init[key].copy()          
                for episode, j in appends:
                    waits.setdefault(episode[j], []).append((episode, j))
        
        if start >= 0:
            for episode in beginsat[start]:
                if episode._initialized[-1] != None and episode._initialized[-1].event_time == start:
                    episode.abs_support += episode._initialized[-1].event_time - episode._inwindow + 1
                    if only_full_windows and start + window_width > event_sequence.end:
                        episode.abs_support -= start + window_width - event_sequence.end
                    episode._inwindow = None
                    episode._initialized[-1] = None
        if start in beginsat:
            del beginsat[start]

    return collection_of_serial_episodes

def candidate_serial_episodes(F, allow_intermediate_events):
    """Find candidates for frequent serial episodes
    
    Parameters
    ----------
    F: list of Episode
        List of episodes of length n
    allow_intermediate_events: bool
        If True, episodes may have intermediate events
        If False, episodes don't skip events
    
    Returns
    -------
    list of Episode
        List of episodes of length n+1. 
        If allow_intermediate_events==True, every subepisode (with length n) of episode is in F.
        If allow_intermediate_events==False, for every episode e, e[1:] and e[:-1] are in F.
    """
    if len(F) == 0: return [] 
    C = []
    if not allow_intermediate_events:
        for i in range(len(F)):
            for j in range(len(F)):
                if F[i][1:] == F[j][:-1]:
                    episode = F[i] + (F[j][-1],)
                    C.append(Episode(episode))
        return C

    F_block_start = list(range(len(F)))
    for k in range(1, len(F)):
        if F[k - 1][:-1] == F[k][:-1]:
            F_block_start[k] = F_block_start[k - 1]
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


def find_sequential_episodes(event_sequences, window_width, min_frequency, 
                                    only_full_windows=False, 
                                    allow_intermediate_events=True, 
                                    **kwargs):
    """Find frequent serial episodes in event sequences. The central 
    functionality of Winepi.
    
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
    allow_intermediate_events: bool
        default: True
        If True, all serial episodes are found.
        If False, only serial episodes with no intermediate events are found.
    event_types: list of hashable
        The event types that are searched for. 
        If not given, generated from event_sequences
    
    Returns
    -------
    list of Episode
        List of episodes that have at least min_frequency.
    """

    if isinstance(event_sequences, EventSequence):
        event_sequences = [event_sequences]

    episodes = kwargs.get('episodes')
    
    event_types = kwargs.get('event_types')
    collection_of_episodes = None
    if event_types == None and episodes == None:
        event_types = set([event.event_type 
                           for event_sequence in event_sequences 
                           for event in event_sequence.sequence_of_events])
        collection_of_episodes = [Episode((event_type,)) for event_type in event_types]

    number_of_windows = (window_width - 1) * len(event_sequences)
    if only_full_windows:
        number_of_windows = -number_of_windows
    for event_sequence in event_sequences:
        number_of_windows += event_sequence.end - event_sequence.start
        if only_full_windows and event_sequence.end - event_sequence.start < window_width:
            print('Winepi: Event sequence shorter than window width.')

    frequent_episodes = []
    if collection_of_episodes != None:
        while len(collection_of_episodes) > 0:
            for event_sequence in event_sequences:
                episode_frequences(event_sequence, collection_of_episodes, window_width, only_full_windows, allow_intermediate_events)
    
            new_frequent_episodes = []
            for episode in collection_of_episodes:
                episode.rel_support = episode.abs_support / number_of_windows
                if episode.rel_support >= min_frequency:
                    episode.allow_intermediate_events = allow_intermediate_events
                    new_frequent_episodes.append(episode)
            collection_of_episodes = candidate_serial_episodes(new_frequent_episodes, allow_intermediate_events)
            frequent_episodes += new_frequent_episodes
    else:
        for event_sequence in event_sequences:
            episode_frequences(event_sequence, episodes, window_width, only_full_windows, allow_intermediate_events)
        for episode in episodes:
            episode.rel_support = episode.abs_support / number_of_windows
            if episode.rel_support >= min_frequency:
                frequent_episodes.append(episode)
    return frequent_episodes



def _support(event_sequences, episodes, window_width,
             support_type, 
             only_full_windows, 
             allow_intermediate_events):
    """Find absolute Winepi frequency for an episode
    
    Parameters
    ----------
    event_sequences: EventSequence, list of EventSequence
        One or more ``EventSequence`` to search for frequent episodes
    episode: Episode
        The episode for which absolute or relative support is found.
    window_width: int
        Width of Winepi window
    support_type: str
        Support type 'abs' or 'rel'.
    only_full_windows: bool
        If True, the start of the first window is at the start of the sequence of events
        and the end of the last window is at the end of the sequence of events.
        If False, the end of the first window is at the start of the sequence of events
        and the start of the last window is at the end of the sequence of events.
    allow_intermediate_events: bool
        default: True
        If True, all serial episodes are found.
        If False, only serial episodes with no intermediate events are found.
    
    Returns
    -------
    int or float
        Absolute frequency of the episode if support_type=='abs'.
        Relative frequency of the episode if support_type=='rel'.
    """
    
    if support_type not in ('abs', 'rel'):
        raise ValueError("unknown support type '%s'." % support_type)

    if isinstance(episodes, Episode):
        episodes = [episodes]
    for episode in episodes:
        episode.reset_support()
        episode.allow_intermediate_events = allow_intermediate_events

    episodes = find_sequential_episodes(event_sequences, window_width, 0, 
                                        only_full_windows, 
                                        allow_intermediate_events,
                                        episodes=episodes)
    if support_type == 'rel':
        return [episode.rel_support for episode in episodes]
    elif support_type == 'abs':
        return [episode.abs_support for episode in episodes]

def abs_support(event_sequences, episodes, window_width, only_full_windows=False, 
                allow_intermediate_events=True):
    """Find absolute Winepi frequency for an episode.
    
    Parameters
    ----------
    event_sequences: EventSequence, list of EventSequence
        One or more ``EventSequence`` to search for frequent episodes
    episode: Episode
        The episode for which absolute support is found.
    window_width: int
        Width of Winepi window
    only_full_windows: bool
        If True, the start of the first window is at the start of the sequence of events
        and the end of the last window is at the end of the sequence of events.
        If False, the end of the first window is at the start of the sequence of events
        and the start of the last window is at the end of the sequence of events.
    allow_intermediate_events: bool
        default: True
        If True, all serial episodes are found.
        If False, only serial episodes with no intermediate events are found.
    
    Returns
    -------
    int
        Absolute frequencies of the episodes.
    """
    
    return _support(event_sequences, episodes, window_width, 'abs', only_full_windows, allow_intermediate_events)


def rel_support(event_sequences, episodes, window_width, only_full_windows=False, 
                allow_intermediate_events=True):
    """Find absolute Winepi frequency for an episode
    
    Parameters
    ----------
    event_sequences: EventSequence, list of EventSequence
        One or more ``EventSequence`` to search for frequent episodest
    episodes: Episode, list of Episode
        the episode for which relative support is found.
    window_width: int
        Width of Winepi window
    only_full_windows: bool
        If True, the start of the first window is at the start of the sequence of events
        and the end of the last window is at the end of the sequence of events.
        If False, the end of the first window is at the start of the sequence of events
        and the start of the last window is at the end of the sequence of events.
    allow_intermediate_events: bool
        default: True
        If True, all serial episodes are found.
        If False, only serial episodes with no intermediate events are found.
    
    Returns
    -------
    list of float
        Relative frequencies of the episodes.
    """
    return _support(event_sequences, episodes, window_width, 'rel', only_full_windows, allow_intermediate_events)

