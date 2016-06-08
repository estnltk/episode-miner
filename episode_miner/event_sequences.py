import json
from cached_property import cached_property

from estnltk.names import TEXT, START, END
from estnltk import PrettyPrinter
from estnltk.prettyprinter import HEADER, MIDDLE, FOOTER
from episode_miner import TERM, WSTART, CSTART
import warnings

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
        self.allow_intermediate_events = None
        self.abs_support = 0
        self.rel_support = 0
        self.examples = None
        self = sequence_of_event_types

    def reset_initialized(self):
        self._initialized = [None] * len(self)

    def reset_support(self):
        self.abs_support = 0
        self.rel_support = 0

    @cached_property
    def _rules(self):
        colors = ('red', 'green', 'blue', 'cyan', 'magenta', 'yellow', 
          'pink','lime', 'peru', 'orange', 'lightgray', 'gray')
        rules = []
        i = 0
        for event_type in {event.event_type for event in self.sequence_of_events}:
            rules.append((event_type, colors[i]))
            i = (i + 1) % len(colors)
        return rules

    def examples_pretty_print(self):
        """Create html of episode examples"""
        
        return self.examples.pretty_print()


class Episodes(list):
    """List of episodes."""
    
    def __init__(self, episodes):
        if isinstance(episodes, Episode):
            episodes = [episodes]
        list.__init__(self, episodes)

    def to_json(self, file='episodes.txt'):
        """Write episodes to file.
        
        Creates file *file*.
                
        Each line of file contains episode serialized by json. The lines of the 
        files created by to_json() and examples_to_json() correspond to each 
        other. 
        
        Parameters
        ----------
        file: str (default: 'episodes.txt')
            Name for the file of episodes.
        """
        with open(file, mode='w') as f:
            for episode in self:
                json.dump({'sequence_of_events': episode, 
                           'abs_support': episode.abs_support, 
                           'rel_support': episode.rel_support, 
                           'allow_intermediate_events': episode.allow_intermediate_events},
                          fp=f,
                          ensure_ascii=False)
                f.write('\n')

    def examples_to_json(self, file='examples.txt'):        
        """Write episode exampls to file.
        
        Creates file *file*.
                
        Each line of file contains episode examples serialized by json. The 
        lines of the files created by to_json() and examples_to_json() 
        correspond to each other. 
        
        Parameters
        ----------
        file: str (default: 'examples.txt')
            Name for the file of episode examples.
        """
        with open(file, mode='w') as f:
            for episode in self:
                f.write(episode.examples.to_json())
                f.write('\n')
    
    def abs_support(self):
        """Creates the list of absolute supports of episodes.

        Returns
        -------
        list
        """

        abs_support = []
        for episode in self:
            abs_support.append(episode.abs_support)
        return abs_support

    def rel_support(self):
        """Creates the list of relative supports of episodes.

        Returns
        -------
        list
        """
        rel_support = []
        for episode in self:
            rel_support.append(episode.rel_support)
        return rel_support


class Event(object):
    """An event is a pair of event type and event time."""
    
    def __init__(self, event_type, event_time):
        """Initialize a new Event.
        
        Parameters
        ----------
        event_type: hashable
            Type of event
        event_time: int
            Time of event
        """
        self.event_type = event_type
        self.event_time = event_time
    
    def __str__(self, *args, **kwargs):
        return '(' + str(self.event_type) + ', ' + str(self.event_time) + ')'
    
    def __repr__(self, *args, **kwargs):
        return self.__str__()
        
    def __eq__(self, event):
        if not isinstance(event, Event):
            return False
        return self.event_type == event.event_type and self.event_time == event.event_time

    def __lt__(self, episode):
        return self.event_time < episode.event_time

    def shift(self, shift):
        """Change time of event.
        
        Parameters
        ----------
        shift: int
            Shifts the time of event by *shift*.

        Returns
        -------
        Event
        """
        self.event_time += shift
        return self


class EventSequence(object):
    """An event sequence is a triple of sequence of events, start and end."""

    def __init__(self, **kwargs):
        """Initialize a new EventSequence
        
        Parameters
        ----------
        sequence_of_events: list of Event
            Sequence of events
        start: int
            Start of sequence of events.
        end: int
            End of sequence of events. If start > end, **ValueError** is raised.
        event_text: EventText
            event_text is used to create event sequence if *cassificator* and
            *time_scale* are given.
        classificator: str
            Keyword of *event_text*'s 'events' layer that points to the event 
            type under the interest.
        time_scale: 'start', 'end', 'cstart', 'wstart' 
            Strategy to determine the time of event.
        """
        self.sequence_of_events = kwargs.get('sequence_of_events')
        self.start = kwargs.get('start')
        self.end = kwargs.get('end')
        
        self.event_text = kwargs.get('event_text')
        time_scale = kwargs.get('time_scale')
        classificator = kwargs.get('classificator')
        if self.event_text != None and classificator != None and time_scale != None:
            self._extract_event_sequence_from_event_text(self.event_text, time_scale, classificator)

        if self.start != None and self.end != None:
            self.sequence_of_events = [event for event in self.sequence_of_events 
                                       if self.start <= event.event_time < self.end]
        self.sequence_of_events.sort()

    def __eq__(self, event_sequence):
        if not isinstance(event_sequence, EventSequence):
            return False
        if len(self.sequence_of_events) != len(event_sequence.sequence_of_events): 
            return False
        if self.start != event_sequence.start:
            return False
        if self.end != event_sequence.end:
            return False
        for e1, e2 in zip(self.sequence_of_events, event_sequence.sequence_of_events):
            if e1 != e2: return False
        return True

    def __str__(self, *args, **kwargs):
        return '(' + str(self.sequence_of_events) + ", start: " + str(self.start) + ", end: " + str(self.end) + ')'
    
    def __repr__(self, *args, **kwargs):
        return self.__str__()
    
        
    def _extract_event_sequence_from_event_text(self, event_text, time_scale=START, classificator=TERM):
        if self.start == None:
            self.start = 0
        if self.end == None: 
            if time_scale in [START, END]:
                self.end = len(event_text.text)
            elif time_scale == CSTART:
                if len(event_text.events) > 0:
                    self.end = event_text.events[-1][CSTART] + len(event_text.text) - event_text.events[-1][END] + 1
                else:
                    self.end = len(event_text.text)
            elif time_scale == WSTART:
                if len(event_text.events) > 0:
                    end_of_last_event = event_text.events[-1][END]
                    for i in range(len(event_text.words)-1, -1, -1):
                        if end_of_last_event >= event_text.words[i][END]:
                            break
                    self.end = len(event_text.words) - i + event_text.events[-1][WSTART]
                else:
                    self.end = len(event_text.words)
            else: 
                raise ValueError("time_scale must be either %s, %s, %s or %s" %START %END %CSTART %WSTART)
        if self.start > self.end:
            raise ValueError("start > end")

        self.sequence_of_events = []
        for textevent in event_text.events:
            if self.start <= textevent[time_scale] < self.end:
                event = Event(textevent[classificator], textevent[time_scale])
                event.text = event_text
                event.start = textevent[START]
                event.end = textevent[END]
                self.sequence_of_events.append(event)

    def _find_episode_examples_intermediate_events_allowed(self, episode, start, window_width, depth):
        if len(episode) == 0: return        
        if window_width < 1: return
        sequence = self.sequence_of_events
        if depth == 0:
            yield []
            return
        for i in range(start, len(sequence)):
            if sequence[i].event_type != episode[-depth]:
                continue
            interval = 0
            if depth != len(episode):
                interval = sequence[i].event_time - sequence[start-1].event_time
                if interval == 0: continue
            for cc in self._find_episode_examples_intermediate_events_allowed(episode, i+1, window_width-interval, depth-1):
                yield [sequence[i]] + cc

    def _find_episode_examples_no_intermediate_events(self, episode, window_width):
        if len(episode) == 0: return        
        sequence = self.sequence_of_events
        for i in range(len(sequence)-len(episode)+1):
            if sequence[i].event_type == episode[0]:
                example = [sequence[i]]
                if len(episode) == 1: 
                    yield example
                    continue
                for j in range(i+1, len(sequence)):
                    if sequence[j].event_time == example[-1].event_time:
                        continue
                    if sequence[j].event_time - example[0].event_time >= window_width:
                        break
                    if sequence[j].event_type == episode[len(example)]:
                        example.append(sequence[j])
                    elif j+1==len(sequence) or sequence[j].event_time < sequence[j+1].event_time:
                        break
                    if len(example) == len(episode):
                        yield example
                        break

    def find_episode_examples(self, episode, window_width, allow_intermediate_events=None):
        """Find episode examples.
        
        Parameters
        ----------
        episode: Episode
            Winepi episode.
        window_width: int
            Width of Winepi window.
        allow_intermediate_events: bool (default: episode.allow_intermediate_events)
            If True, all serial episodes are found.

            If False, only serial episodes with no intermediate events are found.

        Returns
        -------
        generator
            Generator for examples. 
        """
        if allow_intermediate_events == None: 
            allow_intermediate_events = episode.allow_intermediate_events
        if allow_intermediate_events == None: 
            raise TypeError("no positional argument 'allow_intermediate_events' and no attribute 'episode.allow_intermediate_events'")
        if allow_intermediate_events:
            episode_examples = self._find_episode_examples_intermediate_events_allowed(episode, 0, window_width, len(episode))
        else:
            episode_examples = self._find_episode_examples_no_intermediate_events(episode, window_width)
        for example in episode_examples:
            yield EventSequence(sequence_of_events=example, event_text=self.event_text)


    def episode_frequences(self, episodes, 
                           window_width, only_full_windows, 
                           allow_intermediate_events):
        """Find support for episodes in event sequence using Winepi.
                
        Parameters
        ----------
        
        episodes: Episodes
            The episodes for which the abs_support and rel_support is calculated.
        window_width: int
            Width of Winepi window.
        only_full_windows: bool
            If True, the start of the first window is at the start of the sequence of events
            and the end of the last window is at the end of the sequence of events.

            If False, the end of the first window is at the start of the sequence of events
            and the start of the last window is at the end of the sequence of events.

        allow_intermediate_events: bool (default: episode.allow_intermediate_events)
            If True, all serial episodes are found.

            If False, only serial episodes with no intermediate events are found.

        Returns
        -------
        Episodes
            Episodes are equipped with abs_support and rel_support attributes.
        """
        if len(self.sequence_of_events) == 0: 
            return episodes
        waits = {}
        for episode in episodes:
            episode.reset_initialized()
            waits.setdefault(episode[0], []).append((episode, 0))
        waits_init = {}
        for key in waits:
            waits_init[key] = waits[key].copy()          
    
        beginsat = {} 
                
        event_dict = {}
        for event in self.sequence_of_events:
            event_dict.setdefault(event.event_time, []).append(event)
                
        for start in range(self.start-window_width+1, self.end+1):
            beginsat[start+window_width-1] = []
            if start + window_width - 1 < self.end:
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
                        if only_full_windows and start + window_width > self.end:
                            episode.abs_support -= start + window_width - self.end
                        episode._inwindow = None
                        episode._initialized[-1] = None
            if start in beginsat:
                del beginsat[start]
    
        return episodes
                
                
class EventSequences(list):
    """List of EventSequence.
    """

    def __init__(self, **kwargs):
        """Initialize new EventSequences.
        
        Parameters
        ----------
        event_sequences: list of EventSequence, EventSequence
            List of event sequences or an event sequence.
            
            If None, then *sequence_of_events*, *start* and *end* are used to 
            construct *EventSequence*.
        event_texts: list of EventText
            If given, then the parameters *classsificator* and 
            *time_scale* must also be given.
        classificator: str
            Keyword of *event_text*'s 'events' layer that points to the event 
            type under interest.
        time_scale: 'start', 'end', 'cstart', 'wstart' 
            Strategy to determine the time of event.
        sequence_of_events: list of Event
            Sequence of events. Used if *event_sequneces==None*.
        start: int
            Start of sequence of events. Used if *event_sequneces==None*
        end: int
            End of sequence of events. If start > end, **ValueError** is raised.
            Used if *event_sequneces==None*
        """
        event_sequences = kwargs.get('event_sequences')
        if event_sequences == None:
            sequence_of_events = kwargs.get('sequence_of_events')
            if sequence_of_events != None:
                start = kwargs.get('start')
                end = kwargs.get('end')
                event_sequences = EventSequence(sequence_of_events=sequence_of_events, 
                                                start=start, 
                                                end=end)
        if isinstance(event_sequences, EventSequence):
            event_sequences = [event_sequences]

        event_texts = kwargs.get('event_texts')
        time_scale = kwargs.get('time_scale')
        classificator = kwargs.get('classificator')
        if event_texts != None:
            if classificator != None and time_scale != None:
                if event_sequences != None:
                    warnings.warn('Discarding event_sequences parameter. Creating event_sequences from event_texts.')
                event_sequences = []
                for event_text in event_texts:
                    event_sequence = EventSequence(event_text=event_text, 
                                                   time_scale=time_scale, 
                                                   classificator=classificator)
                    event_sequences.append(event_sequence)
            else:
                raise ValueError('event_texts without classificator or time_scale parameter.')
        list.__init__(self, event_sequences)

    def __eq__(self, event_sequences):
        if not isinstance(event_sequences, EventSequences):
            return False
        if len(self) != len(event_sequences): return False
        for e1, e2 in zip(self, event_sequences):
            if e1 != e2: return False
        return True

    def find_episode_examples(self, episodes, window_width, 
                              allow_intermediate_events=None, 
                              number_of_examples='ALL'):
        """Find episode examples.
        
        Parameters
        ----------
        episodes: Episodes
            Winepi episodes.
        window_width: int
            Width of Winepi window.
        allow_intermediate_events: bool
            If True, all serial episodes are found.

            If False, only serial episodes with no intermediate events are found.
        number_of_examples: int, 'ALL' (default: 'ALL')
            Maximum number of examples to find.
        """
        for episode in episodes:
            examples = []
            k = 1
            for event_sequence in self:
                for example in event_sequence.find_episode_examples(episode, 
                                                                    window_width, 
                                                                    allow_intermediate_events):
                    if number_of_examples != 'ALL' and k > number_of_examples:
                        break
                    examples.append(example)
                    k += 1
            episode.examples = EventSequences(event_sequences=examples)
            
        
    def _find_candidate_episodes(self, F, allow_intermediate_events):
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


    def episode_frequences(self, episodes, 
                           window_width, only_full_windows, 
                           allow_intermediate_events):
        """Find support for episodes in event sequences using Winepi.
        
        Parameters
        ----------
        
        episodes: Episodes
            The episodes for which the abs_support and rel_support is calculated.
        window_width: int
            Width of Winepi window.
        only_full_windows: bool
            If True, the start of the first window is at the start of the sequence of events
            and the end of the last window is at the end of the sequence of events.

            If False, the end of the first window is at the start of the sequence of events
            and the start of the last window is at the end of the sequence of events.

        allow_intermediate_events: bool (default: episode.allow_intermediate_events)
            If True, all serial episodes are found.

            If False, only serial episodes with no intermediate events are found.

        Returns
        -------
        Episodes
            Episodes are equipped with abs_support and rel_support attributes.
        """
        for event_sequence in self:
            event_sequence.episode_frequences(episodes, 
                                              window_width, 
                                              only_full_windows, 
                                              allow_intermediate_events)
        return episodes

    
    def find_serial_episodes(self, window_width, min_frequency, 
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
        Episodes
            Episodes that have rel_support >= min_frequency.
        """
        
        episodes = kwargs.get('episodes')
        
        event_types = kwargs.get('event_types')
        collection_of_episodes = None
        if event_types == None and episodes == None:
            event_types = set([event.event_type 
                               for event_sequence in self 
                               for event in event_sequence.sequence_of_events])
            collection_of_episodes = [Episode((event_type,)) for event_type in event_types]
    
        number_of_windows = (window_width - 1) * len(self)
        if only_full_windows:
            number_of_windows = -number_of_windows
        for event_sequence in self:
            number_of_windows += event_sequence.end - event_sequence.start
            if only_full_windows and event_sequence.end - event_sequence.start < window_width:
                warnings.warn('Event sequence shorter than window width.')
    
        frequent_episodes = []
        if collection_of_episodes != None:
            while len(collection_of_episodes) > 0:
                self.episode_frequences(collection_of_episodes, 
                                        window_width, 
                                        only_full_windows, 
                                        allow_intermediate_events)        
                new_frequent_episodes = []
                for episode in collection_of_episodes:
                    episode.rel_support = episode.abs_support / number_of_windows
                    if episode.rel_support >= min_frequency:
                        episode.allow_intermediate_events = allow_intermediate_events
                        new_frequent_episodes.append(episode)
                collection_of_episodes = self._find_candidate_episodes(new_frequent_episodes, 
                                                                       allow_intermediate_events)
                frequent_episodes += new_frequent_episodes
        else:
            self.episode_frequences(episodes, 
                                    window_width, 
                                    only_full_windows, 
                                    allow_intermediate_events)
            for episode in episodes:
                episode.rel_support = episode.abs_support / number_of_windows
                if episode.rel_support >= min_frequency:
                    frequent_episodes.append(episode)
        return Episodes(frequent_episodes)
    
    
    
    def support(self, episodes, window_width,
                 only_full_windows=False, 
                 allow_intermediate_events=None):
        """Find Winepi abs_support and rel_support for every episode in episodes.
        
        Parameters
        ----------
        episodes: Episodes, Episode
            The episode for which absolute or relative support is found.
        window_width: int
            Width of Winepi window
        only_full_windows: bool (default: False)
            If True, the start of the first window is at the start of the sequence of events
            and the end of the last window is at the end of the sequence of events.

            If False, the end of the first window is at the start of the sequence of events
            and the start of the last window is at the end of the sequence of events.
        allow_intermediate_events: bool (default: episodes[0].allow_intermediate_events)
            If True, all serial episodes are found.

            If False, only serial episodes with no intermediate events are found.
        
        Returns
        -------
        Episodes
            Episodes equipped with rel_support and abs_support attributes.
        """
            
        if isinstance(episodes, Episode):
            episodes = Episodes(episodes)
        if allow_intermediate_events == None:
            allow_intermediate_events = episodes[0].allow_intermediate_events
        for episode in episodes:
            episode.reset_support()
            episode.allow_intermediate_events = allow_intermediate_events
    
        episodes = self.find_serial_episodes(window_width, 0, 
                                             only_full_windows, 
                                             allow_intermediate_events,
                                             episodes=episodes)
        return episodes
    
    @cached_property
    def _rules(self):
        colors = ('red', 'green', 'blue', 'cyan', 'magenta', 'yellow', 
          'pink','lime', 'peru', 'orange', 'lightgray', 'gray')
        rules = []
        i = 0
        for event_type in {event.event_type for event_sequence in self 
                                            for event in event_sequence.sequence_of_events}:
            rules.append((event_type, colors[i]))
            i = (i + 1) % len(colors)
        return rules

    
    def pretty_print(self, **kwargs):
        """Pretty prints self. 
        
        Only works if every event sequence in *self* has an *event_text* attribute. 
        
        Returns
        -------
        str
            html document of *self*.
        """
        html = ''
        for event_sequence in self:
            def event_tags(_):
                return ({TEXT: event.event_type, START: event.start, END: event.end} 
                        for event in event_sequence.sequence_of_events)
                
            pp = PrettyPrinter(background=event_tags, background_value=self._rules)
            html += '\t\t<p>' + pp.render(event_sequence.event_text, False) + '</p>\n'

        html = '\n'.join([HEADER, pp.css, MIDDLE, html, FOOTER])
        return html

        
    def to_json(self):
        """Serializes event sequences using json.
        
        Returns
        -------
        str
            json serialization of self. 
        """
        class EventEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, Event):
                    return [obj.event_type, obj.event_time]
                if isinstance(obj, EventSequence):
                    return obj.sequence_of_events
                return json.JSONEncoder.default(self, obj)
        
        return json.dumps(self, ensure_ascii=False, cls=EventEncoder)

