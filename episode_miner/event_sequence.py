import json

from estnltk.names import TEXT, START, END
from episode_miner import TERM, WSTART, CSTART
from estnltk import PrettyPrinter
from estnltk.prettyprinter import HEADER, MIDDLE, FOOTER
from cached_property import cached_property

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
            If given, then the parameters *classsificator* and 
            *time_scale* must also be given.
        classificator: str
            Keyword of *event_text*'s 'events' layer that points to the event 
            type under interest.
        time_scale: 'start', 'end', 'cstart', 'wstart' 
            Strategy to determine the time of event.
        """
        self.sequence_of_events = kwargs.get('sequence_of_events')
        self.start = kwargs.get('start')
        self.end = kwargs.get('end')
        
        self.event_text = kwargs.get('event_text')
        time_scale = kwargs.get('time_scale')
        classificator = kwargs.get('classificator')
        if self.event_text != None:
            if classificator != None and time_scale != None:
                self._extract_event_sequence_from_event_text(self.event_text, time_scale, classificator)
            else:
                raise ValueError('event_text without classificator or time_scale parameter.')
        self.sequence_of_events = [event for event in self.sequence_of_events 
                                   if self.start <= event.event_time < self.end]
        self.sequence_of_events.sort()

    def __str__(self, *args, **kwargs):
        return '(' + str(self.sequence_of_events) + ", start: " + str(self.start) + ", end: " + str(self.end) + ')'
    
    def __repr__(self, *args, **kwargs):
        return self.__str__()
    
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

    
    def pretty_print(self, **kwargs):
        sequence_of_events_generator = kwargs.get('sequence_of_events_generator', [self.sequence_of_events])
        html = ''
        for sequence_of_events in sequence_of_events_generator:
            def event_tags(_):
                return ({TEXT: event.event_type, START: event.start, END: event.end} 
                        for event in sequence_of_events)
            pp = PrettyPrinter(background=event_tags, background_value=self._rules)
            html += '\t\t<p>' + pp.render(self.event_text, False) + '</p>\n'

        html = '\n'.join([HEADER, pp.css, MIDDLE, html, FOOTER])
        return html
        
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
            yield example

    def episodes_and_examples_to_file(self, episodes, 
                                      window_width, 
                                      allow_intermediate_events, 
                                      number_of_examples='ALL',
                                      episodes_file='episodes.txt',
                                      episode_examples_file='episode_examples.txt'):
        """Write the list of episodes and episode examples to file.
        
        Creates files 'episodes.txt' and 'episode_examples.txt'.
        
        Each line of 'episodes.txt' contains one episode from `episodes` 
        serialized by json as a dict with keys 'sequence_of_events', 
        'abs_support', 'rel_support', 'allow_intermediate_events'. 
        
        Each line of 'episode_examples.txt' contains list of examples for the 
        corresponding episode serialised by json.
        
        Parameters
        ----------
        episodes: list of Episode
            The episodes written to the file
        window_width: int
            Width of the Winepi window.
        allow_intermediate_events: bool
            If True, all serial episodes are found.

            If False, only serial episodes with no intermediate events are found.            
        number_of_examples: int, 'ALL' (default: 'ALL')
            Maximum number of examples written to the file. 

            If number_of_examples is less than 1, 'episode_examples.txt' is not 
            created. 
            
            If number_of_examples=='ALL', all examples of episodes are written 
            to the file.
        episodes_file: str (default: 'episodes.txt')
            Name for the file of episodes.
        episode_examples_file: str (default: 'episode_examples.txt')
            Name for the file of episode examples.
        """
        with open(episodes_file, mode='w') as f:
            for episode in episodes:
                json.dump({'sequence_of_events': episode, 
                           'abs_support': episode.abs_support, 
                           'rel_support': episode.rel_support, 
                           'allow_intermediate_events': episode.allow_intermediate_events},
                          fp=f,
                          ensure_ascii=False)
                f.write('\n')

        if isinstance(number_of_examples, int):
            if number_of_examples < 1:
                return
        elif number_of_examples != 'ALL':
            return
        
        class EventEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, Event):
                    return [obj.event_type, obj.event_time]
                # Let the base class default method raise the TypeError
                return json.JSONEncoder.default(self, obj)
        
        with open(episode_examples_file, mode='w') as f:
            for episode in episodes:
                k = 1
                examples = []
                for example in self.find_episode_examples(episode, window_width, 
                                                          allow_intermediate_events):
                    examples.append(example)
                    k += 1
                    if number_of_examples != 'ALL' and k > number_of_examples:
                        break
                json.dump(examples, fp=f, ensure_ascii=False, cls=EventEncoder)
                f.write('\n')