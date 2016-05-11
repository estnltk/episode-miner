import unittest

from episode_miner import EventTagger
from estnltk import Text
from estnltk.names import START, END

class EventTaggerTest(unittest.TestCase):
    
    def test_resolve_conflicts_MAX(self):
        event_tagger = EventTagger([], 'naive', 'MAX')
        # empty list
        events = []
        result = event_tagger.resolve_conflicts(events)
        expected = []
        self.assertListEqual(expected, result)

        # one event
        events = [{START: 1, END:  4}]
        result = event_tagger.resolve_conflicts(events)
        expected = [{START: 1, END:  4}]
        self.assertListEqual(expected, result)

        # equal events
        events = [{START: 1, END:  4},
                  {START: 1, END:  4}]
        result = event_tagger.resolve_conflicts(events)
        expected = [{START: 1, END:  4}]
        self.assertListEqual(expected, result)

        # common start
        events = [{START: 1, END:  4},
                  {START: 1, END:  6}]
        result = event_tagger.resolve_conflicts(events)
        expected = [{START: 1, END:  6}]
        self.assertListEqual(expected, result)

        # common end
        events = [{START: 3, END:  6},
                  {START: 1, END:  6}]
        result = event_tagger.resolve_conflicts(events)
        expected = [{START: 1, END:  6}]
        self.assertListEqual(expected, result)

        # complex
        events = [{START: 1, END:  8},
                  {START: 2, END:  4},
                  {START: 3, END:  6}]
        result = event_tagger.resolve_conflicts(events)
        expected = [{START: 1, END:  8}]
        self.assertListEqual(expected, result)        

    def test_resolve_conflicts_MIN(self):
        event_tagger = EventTagger([], 'naive', 'MIN')
        # empty list
        events = []
        result = event_tagger.resolve_conflicts(events)
        expected = []
        self.assertListEqual(expected, result)

        # one event
        events = [{START: 1, END:  4}]
        result = event_tagger.resolve_conflicts(events)
        expected = [{START: 1, END:  4}]
        self.assertListEqual(expected, result)

        # equal events
        events = [{START: 1, END:  4},
                  {START: 1, END:  4}]
        result = event_tagger.resolve_conflicts(events)
        expected = [{START: 1, END:  4}]
        self.assertListEqual(expected, result)

        # common start
        events = [{START: 1, END:  4},
                  {START: 1, END:  6}]
        result = event_tagger.resolve_conflicts(events)
        expected = [{START: 1, END:  4}]
        self.assertListEqual(expected, result)

        # common end
        events = [{START: 3, END:  6},
                  {START: 1, END:  6}]
        result = event_tagger.resolve_conflicts(events)
        expected = [{START: 3, END:  6}]
        self.assertListEqual(expected, result)

        # complex
        events = [{START: 1, END:  8},
                  {START: 2, END:  4},
                  {START: 3, END:  6}]
        result = event_tagger.resolve_conflicts(events)
        expected = [{START: 2, END:  4},
                    {START: 3, END:  6}]
        self.assertListEqual(expected, result)        

    def test_resolve_conflicts_ALL(self):
        event_tagger = EventTagger([], 'naive', 'ALL')
        # complex
        events = [{START: 1, END:  8},
                  {START: 2, END:  4},
                  {START: 3, END:  6}]
        result = event_tagger.resolve_conflicts(events)
        expected = [{START: 1, END:  8},
                    {START: 2, END:  4},
                    {START: 3, END:  6}]
        self.assertListEqual(expected, result)        

    def test_event_tagger_tag_events(self):
        event_vocabulary = [{'term': 'Harv', 'type': 'sagedus'}, 
                            {'term': 'peavalu', 'type': 'sümptom'}]
        text = Text('Harva esineb peavalu.')
        event_tagger = EventTagger(event_vocabulary, 'naive', 'ALL')
        result = event_tagger.tag_events(text)
        expected = [{'cstart': 0, 'start': 0, 'end': 4, 'type': 'sagedus', 'wstart': 0, 'term': 'Harv'}, 
                    {'cstart': 10, 'start': 13, 'end': 20, 'type': 'sümptom', 'wstart': 2, 'term': 'peavalu'}]
        self.assertListEqual(expected, result)


    def test_event_tagger_sort_events(self): # TODO: kattuvate sündmuste cstart, wstart vajab lahendust
        event_vocabulary = [{'term': 'neli'}, 
                            {'term': 'kolm neli'},
                            {'term': 'kaks kolm'},
                            {'term': 'kaks kolm neli'}]
        text = Text('Üks kaks kolm neli.')
        event_tagger = EventTagger(event_vocabulary, 'naive', 'ALL')
        result = event_tagger.tag_events(text)
        expected = [{'cstart': 4, 'end': 13, 'start': 4, 'term': 'kaks kolm', 'wstart': 1},
                    {'cstart': -4, 'end': 18, 'start': 4, 'term': 'kaks kolm neli', 'wstart': 0},
                    {'cstart': -12, 'end': 18, 'start': 9, 'term': 'kolm neli', 'wstart': -1},
                    {'cstart': -15, 'end': 18, 'start': 14, 'term': 'neli', 'wstart': -1}]

        self.assertListEqual(expected, result)
