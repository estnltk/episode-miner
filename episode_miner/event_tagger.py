from __future__ import unicode_literals

import unicodecsv as csv
import ahocorasick
from estnltk.names import START, END, TEXT

TERM = 'term'
WSTART = 'wstart'
WEND = 'wend'
CSTART = 'cstart'

class EventTagger():
    
    def __init__(self, event_vocabulary_file, method):
        self.event_vocabulary = self.read_event_vocabulary(event_vocabulary_file)
        self.method = method
        self.ahocorasick_automaton = None
    
    def read_event_vocabulary(self, event_vocabulary_file):
        event_vocabulary = []
        with open(event_vocabulary_file, 'rb') as file:
            reader = csv.DictReader(file)
            if (START in reader.fieldnames or 
                END in reader.fieldnames or
                WSTART in reader.fieldnames or
                WEND in reader.fieldnames or
                CSTART in reader.fieldnames):
                raise Exception('Invalid column heading in event vocabulary file.')
            if TERM not in reader.fieldnames:
                raise Exception("No column with heading '" + TERM + "' in event vocabulary file.")
            for row in reader:
                event_vocabulary.append(row)
        return event_vocabulary

    def find_events_naive(self, text):
        events = []
        for entry in self.event_vocabulary:
            start = text.find(entry[TERM])
            while start > -1:
                events.append(entry.copy())
                events[-1].update({START: start, END: start+len(entry[TERM])})
                start = text.find(entry[TERM], start+1)
        return events

    def find_events_ahocorasick(self, text):
        events = []
        if self.ahocorasick_automaton == None:
            self.ahocorasick_automaton = ahocorasick.Automaton()
            for entry in self.event_vocabulary:
                self.ahocorasick_automaton.add_word(entry[TERM], entry)
            self.ahocorasick_automaton.make_automaton()
        for item in self.ahocorasick_automaton.iter(text):
            events.append(item[1].copy())
            events[-1].update({START: item[0]+1-len(item[1][TERM]), END: item[0]+1})
        return events
    
    def event_intervals(self, events, text):
#         events.sort(key=lambda event: event[START])
        events.sort(key=lambda event: event[END])
#         for i in range(len(events)-1, -1, -1):
#             if events[i][END] == events[i-1][END] and events[i][START] >= events[i-1][START]:
#                 del events[i]
        events.sort(key=lambda event: event[START])
#         no_super_events = []
#         for i in range(len(events)-1):
#             if events[i][START] != events[i+1][START] or events[i][END] > events[i+1][END]:
#                 no_super_events.append(events[i])        
#         events = no_super_events
                
        bookmark = 0
        for event in events:
            event[WSTART] = len(text.word_spans)
            event[WEND] = 0
            for i in range(bookmark, len(text.word_spans)-1):
                if text.word_spans[i][0] <= event[START] < text.word_spans[i+1][0]:
                    event[WSTART] = i
                    bookmark = i
                if text.word_spans[i][0] < event[END] <= text.word_spans[i+1][0]:
                    event[WEND] = i + 1
                    break

        w_shift = 0
        c_shift = 0
        for event in events:
            event[WSTART] -= w_shift
            event[WEND] -= w_shift
            w_shift += event[WEND] - event[WSTART] - 1
            del event[WEND]

            event[CSTART] = event[START] - c_shift
            c_shift += event[END] - event[START] - 1
        return events

    def tag_events(self, text):
        if self.method == 'ahocorasick':
            events = self.find_events_ahocorasick(text[TEXT])
        elif self.method == 'naive':
            events = self.find_events_naive(text[TEXT])
        else:
            raise Exception('Invalid method.')
        self.event_intervals(events, text)
        return events
