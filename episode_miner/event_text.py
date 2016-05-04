from estnltk import Text
from episode_miner.winepi import Event, EventSequence
from episode_miner.event_tagger import START, END, WSTART, CSTART

class EventText(Text):
        
    def __init__(self, *args, **kwargs):
        super(EventText, self).__init__(*args, **kwargs)
        if 'event_tagger' in kwargs:
            self.event_tagger = kwargs['event_tagger']
        else:
            raise Exception('No event_tagger given.')

    def events(self):
        if not self.is_tagged('events'):
            self['events'] = self.event_tagger.tag_events(self)
        return self['events']
        
    def get_event_sequence(self, count_event_time_by, classificator):
        if count_event_time_by == 'char':
            sequence_of_events = [Event(event[classificator], event[CSTART], self, event[START], event[END]) for event in self['events']]
            start = self['events'][0][CSTART] 
            end = self['events'][-1][CSTART] + 1 # kas arvutada nii või keerulisemalt? 
        elif count_event_time_by == 'word':
            sequence_of_events = [Event(event[classificator], event[WSTART], self, event[START], event[END]) for event in self['events']]
            start = self['events'][0][WSTART] 
            end = self['events'][-1][WSTART] + 1 # kas arvutada nii või keerulisemalt? 
        else: 
            sequence_of_events = []
            start = 0
            end = 1
        return EventSequence(sequence_of_events, start, end)
