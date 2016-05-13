from estnltk.names import START, END
from episode_miner import TERM, WSTART, CSTART

class Event(object):
    
    def __init__(self, event_type, event_time):
        """Initialize a new Event
        
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
        self.event_time += shift
        return self


class EventSequence(object):

    def __init__(self, **kwargs):
        """Initialize a new EventSequence
        
        Parameters
        ----------
        sequence_of_events: list of Event
            Sequence of events
        start: int
            Start of sequence of events.
        end: int
            End of sequence of events. If start > end, ValueError is raised.
        event_text: EventText
            If given, then the parameters ``classsificator`` and 
            ``time_scale`` must also be given.
        classificator: str
            Keyword of event_text 'events' layer that points to event type.
        time_scale: 'start', 'end', 'cstart', 'wstart', 
            Strategy to determine time of event.
        """
        self.sequence_of_events = kwargs.get('sequence_of_events')
        self.start = kwargs.get('start')
        self.end = kwargs.get('end')
        
        event_text = kwargs.get('event_text')
        time_scale = kwargs.get('time_scale')
        classificator = kwargs.get('classificator')
        if event_text != None:
            if classificator != None and time_scale != None:
                self.extract_event_sequence_from_event_text(event_text, time_scale, classificator)
            else:
                raise ValueError('event_text without classificator or time_scale parameter.')
        self.sequence_of_events = [event for event in self.sequence_of_events 
                                   if self.start <= event.event_time < self.end]
        self.sequence_of_events.sort()

    def extract_event_sequence_from_event_text(self, event_text, time_scale=START, classificator=TERM):
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
