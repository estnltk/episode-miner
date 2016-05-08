from __future__ import unicode_literals

import unicodecsv as csv
import ahocorasick
from estnltk.names import START, END
from pandas import DataFrame

TERM = 'term'
WSTART = 'wstart'
WEND = 'wend'
CSTART = 'cstart'

class EventTagger():
    
    def __init__(self, event_vocabulary, search_method, conflict_resolving_strategy):
        self.event_vocabulary = self.read_event_vocabulary(event_vocabulary)
        self.search_method = search_method
        self.ahocorasick_automaton = None
        self.conflict_resolving_strategy = conflict_resolving_strategy
    
    def read_event_vocabulary(self, event_vocabulary):
        if isinstance(event_vocabulary, list):
            event_vocabulary = event_vocabulary
        elif isinstance(event_vocabulary, DataFrame):
            event_vocabulary = event_vocabulary.to_dict('records')
        elif isinstance(event_vocabulary, str):
            with open(event_vocabulary, 'rb') as file:
                reader = csv.DictReader(file)
                event_vocabulary = []
                for row in reader:
                    event_vocabulary.append(row)
        else:
            raise TypeError("%s not supported as event_vocabulary" %type(event_vocabulary))
        if len(event_vocabulary) == 0:
            return []
        if (START  in event_vocabulary[0] or 
            END    in event_vocabulary[0] or
            WSTART in event_vocabulary[0] or
            WEND   in event_vocabulary[0] or
            CSTART in event_vocabulary[0]):
            raise KeyError('Illegal key in event vocabulary.')
        if TERM not in event_vocabulary[0]:
            raise KeyError("Missing key '" + TERM + "' in event vocabulary.")
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

    def resolve_conflicts(self, events):
        if self.conflict_resolving_strategy == 'ALL':
            return events
        elif self.conflict_resolving_strategy == 'MAX':
            if len(events) < 2:
                return events
            bookmark = 0
            while bookmark < len(events)-1 and events[0][START] == events[bookmark+1][START]:
                bookmark += 1
            new_events = [events[bookmark]]
            for i in range(bookmark+1, len(events)-1):
                if events[i][END] > new_events[-1][END] and events[i][START] != events[i+1][START]:
                    new_events.append(events[i])
            if events[-1][END] > new_events[-1][END]:
                new_events.append(events[-1])
            return new_events
        elif self.conflict_resolving_strategy == 'MIN':
            if len(events) < 2:
                return events
            while len(events) > 1 and events[-1][START] == events[-2][START]:
                del events[-1]
            for i in range(len(events)-2, 0, -1):
                if events[i][START] == events[i-1][START] or events[i][END] >= events[i+1][END]:
                    del events[i]
            if len(events) > 1 and events[0][END] >= events[1][END]:
                del events[0]
            return events
        else:
            raise Exception('Invalid conflict resolving strategy.')

    
    def event_intervals(self, events, text):                
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
        if self.search_method == 'ahocorasick':
            events = self.find_events_ahocorasick(text.text)
        elif self.search_method == 'naive':
            events = self.find_events_naive(text.text)
        else:
            raise Exception('Invalid method.')

        events.sort(key=lambda event: event[END])
        events.sort(key=lambda event: event[START])

        events = self.resolve_conflicts(events)

        self.event_intervals(events, text)
        return events
