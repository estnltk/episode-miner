from estnltk.text import Text
from winepi import Event, EventSequence

class EventText(Text):
        
    def __init__(self, *args, **kwargs):
        super(EventText, self).__init__(*args, **kwargs)
        if 'event_vocabulary' in kwargs:
            pass
        else:
            pass
        if 'event_tagger' in kwargs:
            self.event_tagger = kwargs['event_tagger']
        else:
            pass
                
    def events(self):
        if not self.is_tagged('events'): #kas nii on hästi?
            self['events'] = self.event_tagger.events(self)
        return self['events']
        
    def event_sequence(self, count_event_time_by, classificator): #kus on selle funktsiooni õige koht?
        if count_event_time_by == 'char':
            sequence_of_events = [Event(event[classificator], event['cstart'], self, event['start'], event['end']) for event in self['events']]
            start = self['events'][0]['cstart'] 
            end = self['events'][-1]['cend']
        elif count_event_time_by == 'word':
            sequence_of_events = [Event(event[classificator], event['wstart'], self, event['start'], event['end']) for event in self['events']]
            start = self['events'][0]['wstart'] 
            end = self['events'][-1]['wend']
        else: 
            sequence_of_events = []
            start = 0
            end = 1
#        if 'words' in self.keys(): #ümber teha, nii et chariga ka töötab
#            end = len(self['words'])
        return EventSequence(sequence_of_events, start, end)
