'''
Created on 03.2016

@author: paul
'''

class Event():
    def __init__(self, event_type, event_time, text=None, start=None, end=None):
        self.event_type = event_type
        self.event_time = event_time
        self.text = text
        self.start = start
        self.end = end
        self = (event_type, event_time)
    
    def shift(self, shift):
        self.event_time += shift
        return self # kas nii on Pythonis kombeks?

class Episode(tuple):
    def __init__(self, sequence_of_event_types):
        self.initialized = [None] * len(sequence_of_event_types)
        self.freq_count = 0
        self.relative_frequency = 0
        self.inwindow = None
        self = sequence_of_event_types
        
class EventSequence(object):
    def __init__(self, sequence_of_events, start, end):
        self.sequence_of_events = sequence_of_events
        self.start = start
        self.end = end


def find_episode(episode, first_event, event_sequence):
    bookmark = event_sequence.sequence_of_events.index(first_event)
    events = []
    for event_type in episode:
        while event_sequence.sequence_of_events[bookmark].event_type != event_type:
            bookmark += 1
        events.append(event_sequence.sequence_of_events[bookmark])
        bookmark += 1
    return events
        

'''Algorithm 5
T_s = 0, T_e = event_sequence.end
'''
def frequent_serial_episodes(event_sequence, collection_of_serial_episodes, window_width, min_frequency, number_of_examples):
    C = list(map(Episode, collection_of_serial_episodes))
    episode_examples = {}
    waits = {}
    for episode in event_sequence.sequence_of_events:
        waits[episode.event_type] = []
    for episode in C:
        for b in episode:
            waits[b] = []
    for episode in C: 
        waits[episode[0]].append((episode, 0))
        episode_examples[episode] = []

    beginsat = {} 
    for t in range(-window_width + 1, 0):
        beginsat[t] = []
        
    
    for start in range(-window_width + 1, event_sequence.end + 1):
        beginsat[start + window_width - 1] = []
        if start + window_width - 1 < event_sequence.end:
            removes = []
            appends = []
            for event in event_sequence.sequence_of_events: 
                if event.event_time != start + window_width - 1: continue #seda saab optimiseerida 
                waits[event.event_type].sort(key = lambda pair: pair[1], reverse = True)
                for episode, j in waits[event.event_type]: 
                    if j == 0:
                        episode.initialized[0] = event
                        if len(episode) == 1:
                            beginsat[episode.initialized[0].event_time].append(episode)
                            if episode.inwindow == None:
                                episode.inwindow = start
                        else:
                            appends.append((episode, 1))                    
                    elif j < len(episode) - 1: 
                        episode.initialized[j] = None
                        if episode.initialized[j - 1] != None and episode.initialized[j - 1].event_time > start: # seda saab täpsustada
                            episode.initialized[j] = episode.initialized[j - 1]
                            appends.append((episode, j + 1))
                        removes.append((episode, j))
                    elif j == len(episode) - 1:
                        if episode.initialized[j] == None and episode.initialized[j - 1] != None and episode.initialized[j - 1].event_time >= start:
                            episode.inwindow = start
                        if episode.initialized[j - 1] != None and episode.initialized[j - 1].event_time >= start:
                            episode.initialized[j] = episode.initialized[j - 1]
                            beginsat[episode.initialized[j].event_time].append(episode)
                        removes.append((episode, j))
                for episode, j in removes:
                    waits[episode[j]].remove((episode, j))            
                for episode, j in appends:
                    waits[episode[j]].append((episode, j))
        
        if start >= 0:
            for episode in beginsat[start]:
                if episode.initialized[-1] != None and episode.initialized[-1].event_time == start:
                    episode.freq_count += episode.initialized[-1].event_time - episode.inwindow + 1
                    if len(episode_examples[episode]) < number_of_examples:
                        episode_examples[episode].append(find_episode(episode, episode.initialized[-1], event_sequence))
                    episode.inwindow = None
                    episode.initialized[-1] = None
        del beginsat[start]
            
    for episode in C:
        episode.relative_frequency = episode.freq_count / (event_sequence.end - event_sequence.start + window_width - 1)
    frequent_episodes = list(filter(lambda episode: episode.relative_frequency >= min_frequency , C))
    frequent_episode_examples = {}
    for episode in frequent_episodes:
        frequent_episode_examples[episode] = episode_examples[episode]
    return frequent_episodes, frequent_episode_examples

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
            episode  = F[i][:l] + F[j][l - 1:]
            
            next_event = True
            for y in range(l - 1):
                b = episode[:y] + episode[y + 1:]
                if b not in F:
                    next_event = False
                    continue
            if next_event:
                k += 1
                C += [episode]
                C_block_start += [current_block_start]
            j += 1
    return C

'''Algorithm 2
'''
def collection_of_frequent_episodes(event_sequence, event_types, window_width, min_frequency, number_of_examples=0):
    if isinstance(event_sequence, list):
        concatenation_of_sequences_of_events = []
        shift = 0
        for es in event_sequence:
            if len(es.sequence_of_events) == 0: continue
            for event in es.sequence_of_events:
                if es.start <= event.event_time < es.end:
                    concatenation_of_sequences_of_events.append(event.shift(-es.start+shift)) 
            shift += es.end - es.start + window_width  #kontrollida +-1
        event_sequence = EventSequence(concatenation_of_sequences_of_events, 0, shift-window_width) 
    if event_types == 'default':
        event_types = set([event.event_type for event in event_sequence.sequence_of_events])
        event_types = [[event_type] for event_type in event_types]
    C = []
    F = []
    episode_examples = {}
    C[len(C):] = [event_types] #TODO: ilusamaks
    while len(C[-1]) > 0:
        frequent_episodes, examples = frequent_serial_episodes(event_sequence, C[-1], window_width, min_frequency, number_of_examples)
        F += frequent_episodes
        episode_examples.update(examples)
        C.append(candidate_serial_episodes(frequent_episodes))
    return F, episode_examples

