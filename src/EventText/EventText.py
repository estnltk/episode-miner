'''
Created on 05.04.2016

@author: paul
'''
from estnltk import Text
import csv
from Winepi.Winepi import EventSequence, Event
import ahocorasick


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


class EventTagger():
    
    def __init__(self, event_vocabulary_file, consider_gaps=False):
        self.event_vocabulary = self.read_event_vocabulary(event_vocabulary_file)
        self.consider_gaps = consider_gaps
    
    def read_event_vocabulary(self, event_vocabulary_file):
        event_vocabulary = []
        with open(event_vocabulary_file) as file:
            reader = csv.DictReader(file)
            for row in reader:
                event_vocabulary.append(row)
        return event_vocabulary

    def events_old(self, text): #does not need ahocorasick
        events = []
        for entry in self.event_vocabulary:
            if entry['term'] == '*gap*':
                gaps_entry = entry.copy()
                continue
            start = text['text'].find(entry['term'])
            while start > -1:
                events.append(entry.copy())
                events[-1].update({'start': start, 'end': start+len(entry['term'])})
                start = text['text'].find(entry['term'], start+1)
        events.sort(key=lambda event: event['start']) # mis teha kui mitu 'event'i kattuvad?
        bookmark = 0
        for event in events:
            event['wstart'] = len(text.word_spans)
            event['wend'] = 0
            for i in range(bookmark, len(text.word_spans)-1):
                if text.word_spans[i][0] <= event['start'] < text.word_spans[i+1][0]:
                    event['wstart'] = i
                    bookmark = i
                if text.word_spans[i][0] < event['end'] <= text.word_spans[i+1][0]:
                    event['wend'] = i + 1
                    break
        w_shift = 0
        c_shift = 0
        for event in events:
            event['wstart'] -= w_shift
            event['wend'] -=  w_shift
            w_shift += event['wend'] - event['wstart'] - 1
            event['wend']= event['wstart'] + 1

            event['cstart'] = event['start'] - c_shift
            c_shift += event['end'] - event['start'] - 1
            event['cend'] = event['cstart'] + 1
        if self.consider_gaps:
            last_event_end = 0
            update_events = []
            for i in range(len(events)-1):
                if events[i]['wend'] < events[i+1]['wstart']: 
                    update_events.append(gaps_entry.copy())
                    update_events[-1].update({ 'start': events[i]['end'],   'end': events[i+1]['start'], 
                                              'wstart': events[i]['wend'], 'wend': events[i+1]['wstart'],
                                              'cstart': events[i]['cend'], 'cend': events[i+1]['cstart']})
                last_event_end = event['end'] 
            if last_event_end < text.word_spans[-1][1]:
                update_events.append(gaps_entry)
                if len(events) == 0:
                    update_events[-1].update({ 'start': last_event_end, 'end': text.word_spans[-1][1], 
                                              'wstart': 0, 'wend': len(text.word_spans),
                                              'cstart': 0, 'cend': len(text['text'])})
                else:
                    update_events[-1].update({'start': last_event_end, 'end': text.word_spans[-1][1], 
                                              'wstart': events[-1]['wend'], 'wend': len(text.word_spans)-0,                    
                                              'cstart': events[-1]['cend'], 'cend': len(text['text'])-0})                    
            events += update_events
            events.sort(key=lambda event: event['start']) 
        return events 

    def events(self, text):
        events = []
        ac = ahocorasick.Automaton()
        for entry in self.event_vocabulary:
            if entry['term'] == '*gap*':
                gaps_entry = entry.copy()
                continue
            ac.add_word(entry['term'], entry)
        ac.make_automaton()
        for item in ac.iter(text['text']):
            events.append(item[1].copy())
            events[-1].update({'start': item[0]+1-len(item[1]['term']), 'end': item[0]+1})

        events.sort(key=lambda event: event['start']) # mis teha kui mitu 'event'i kattuvad?
        bookmark = 0
        for event in events:
            event['wstart'] = len(text.word_spans)
            event['wend'] = 0
            for i in range(bookmark, len(text.word_spans)-1):
                if text.word_spans[i][0] <= event['start'] < text.word_spans[i+1][0]:
                    event['wstart'] = i
                    bookmark = i
                if text.word_spans[i][0] < event['end'] <= text.word_spans[i+1][0]:
                    event['wend'] = i + 1
                    break
        if self.consider_gaps:
            last_event_end = 0
            update_events = []
            for i in range(len(events)-1):
                if events[i]['wend'] < events[i+1]['wstart']: 
                    update_events.append(gaps_entry.copy())
                    update_events[-1].update({ 'start': events[i]['end'],   'end': events[i+1]['start'], 
                                              'wstart': events[i]['wend'], 'wend': events[i+1]['wstart']})
                last_event_end = event['end'] 
            if last_event_end < text.word_spans[-1][1]:
                update_events.append(gaps_entry)
                if len(events) == 0:
                    update_events[-1].update({ 'start': last_event_end, 'end': text.word_spans[-1][1], 
                                              'wstart': 0, 'wend': len(text.word_spans)})
                else:
                    update_events[-1].update({'start': last_event_end, 'end': text.word_spans[-1][1], 
                                              'wstart': events[-1]['wend'], 'wend': len(text.word_spans)})                    
            events += update_events
            events.sort(key=lambda event: event['start']) 

        w_shift = 0
        c_shift = 0
        for event in events:
            event['wstart'] -= w_shift
            event['wend'] -=  w_shift
            if event['term'] != '*gap*': 
                w_shift += event['wend'] - event['wstart'] - 1
                event['wend']= event['wstart'] + 1

            event['cstart'] = event['start'] - c_shift
            if event['term'] != '*gap*': 
                c_shift += event['end'] - event['start'] - 1
                event['cend'] = event['cstart'] + 1
            else:
                event['cend'] = event['end'] - c_shift
        return events 

