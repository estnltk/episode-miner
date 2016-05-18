import unittest

from episode_miner import EventTagger
from estnltk import Text
from estnltk.names import START, END

class EventTaggerTest(unittest.TestCase):
    
    def test_resolve_conflicts_MAX(self):
        event_tagger = EventTagger([], 'naive', 'MAX')
        # empty list
        events = []
        print(dir(event_tagger))
        result = event_tagger._EventTagger__resolve_conflicts(events)
        expected = []
        self.assertListEqual(expected, result)

        # one event
        events = [{START: 1, END:  4}]
        result = event_tagger._EventTagger__resolve_conflicts(events)
        expected = [{START: 1, END:  4}]
        self.assertListEqual(expected, result)

        # equal events
        events = [{START: 1, END:  4},
                  {START: 1, END:  4}]
        result = event_tagger._EventTagger__resolve_conflicts(events)
        expected = [{START: 1, END:  4}]
        self.assertListEqual(expected, result)

        # common start
        events = [{START: 1, END:  4},
                  {START: 1, END:  6}]
        result = event_tagger._EventTagger__resolve_conflicts(events)
        expected = [{START: 1, END:  6}]
        self.assertListEqual(expected, result)

        # common end
        events = [{START: 3, END:  6},
                  {START: 1, END:  6}]
        result = event_tagger._EventTagger__resolve_conflicts(events)
        expected = [{START: 1, END:  6}]
        self.assertListEqual(expected, result)

        # complex
        events = [{START: 1, END:  8},
                  {START: 2, END:  4},
                  {START: 3, END:  6}]
        result = event_tagger._EventTagger__resolve_conflicts(events)
        expected = [{START: 1, END:  8}]
        self.assertListEqual(expected, result)        

    def test_resolve_conflicts_MIN(self):
        event_tagger = EventTagger([], 'naive', 'MIN')
        # empty list
        events = []
        result = event_tagger._EventTagger__resolve_conflicts(events)
        expected = []
        self.assertListEqual(expected, result)

        # one event
        events = [{START: 1, END:  4}]
        result = event_tagger._EventTagger__resolve_conflicts(events)
        expected = [{START: 1, END:  4}]
        self.assertListEqual(expected, result)

        # equal events
        events = [{START: 1, END:  4},
                  {START: 1, END:  4}]
        result = event_tagger._EventTagger__resolve_conflicts(events)
        expected = [{START: 1, END:  4}]
        self.assertListEqual(expected, result)

        # common start
        events = [{START: 1, END:  4},
                  {START: 1, END:  6}]
        result = event_tagger._EventTagger__resolve_conflicts(events)
        expected = [{START: 1, END:  4}]
        self.assertListEqual(expected, result)

        # common end
        events = [{START: 3, END:  6},
                  {START: 1, END:  6}]
        result = event_tagger._EventTagger__resolve_conflicts(events)
        expected = [{START: 3, END:  6}]
        self.assertListEqual(expected, result)

        # complex
        events = [{START: 1, END:  8},
                  {START: 2, END:  4},
                  {START: 3, END:  6}]
        result = event_tagger._EventTagger__resolve_conflicts(events)
        expected = [{START: 2, END:  4},
                    {START: 3, END:  6}]
        self.assertListEqual(expected, result)        

    def test_resolve_conflicts_ALL(self):
        event_tagger = EventTagger([], 'naive', 'ALL')
        # complex
        events = [{START: 1, END:  8},
                  {START: 2, END:  4},
                  {START: 3, END:  6}]
        result = event_tagger._EventTagger__resolve_conflicts(events)
        expected = [{START: 1, END:  8},
                    {START: 2, END:  4},
                    {START: 3, END:  6}]
        self.assertListEqual(expected, result)        

    def test_event_tagger_tag_events(self):
        event_vocabulary = [{'term': 'Harv', 'type': 'sagedus'}, 
                            {'term': 'peavalu', 'type': 'sümptom'}]
        text = Text('Harva esineb peavalu.')
        event_tagger = EventTagger(event_vocabulary, 'naive', 'ALL', return_layer=True)
        result = event_tagger.tag(text)
        expected = [{'term':    'Harv', 'type': 'sagedus', 'start':  0, 'end':  4, 'wstart_raw': 0, 'wend_raw': 1, 'cstart':  0, 'wstart': 0}, 
                    {'term': 'peavalu', 'type': 'sümptom', 'start': 13, 'end': 20, 'wstart_raw': 2, 'wend_raw': 3, 'cstart': 10, 'wstart': 2}]
        self.assertListEqual(expected, result)


    def test_event_tagger_sort_events(self): # TODO: kattuvate sündmuste cstart, wstart vajab lahendust
        event_vocabulary = [{'term': 'neli'}, 
                            {'term': 'kolm neli'},
                            {'term': 'kaks kolm'},
                            {'term': 'kaks kolm neli'}]
        text = Text('Üks kaks kolm neli.')
        event_tagger = EventTagger(event_vocabulary, 'naive', 'ALL', return_layer=True)
        result = event_tagger.tag(text)
        expected = [{'term': 'kaks kolm',      'start':  4, 'end': 13, 'wstart_raw': 1, 'wend_raw': 3},
                    {'term': 'kaks kolm neli', 'start':  4, 'end': 18, 'wstart_raw': 1, 'wend_raw': 4},
                    {'term': 'kolm neli',      'start':  9, 'end': 18, 'wstart_raw': 2, 'wend_raw': 4},
                    {'term': 'neli',           'start': 14, 'end': 18, 'wstart_raw': 3, 'wend_raw': 4}]
        self.assertListEqual(expected, result)
