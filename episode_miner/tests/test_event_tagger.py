import unittest

from episode_miner import EventTagger
from estnltk import Text
from estnltk.names import START, END

class EventTaggerTest(unittest.TestCase):
    
    def test_resolve_conflicts_MAX(self):
        event_tagger = EventTagger('data/event vocabulary.csv', 'naive', 'MAX')
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
        event_tagger = EventTagger('data/event vocabulary.csv', 'naive', 'MIN')
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
        event_tagger = EventTagger('data/event vocabulary.csv', 'naive', 'ALL')
        # complex
        events = [{START: 1, END:  8},
                  {START: 2, END:  4},
                  {START: 3, END:  6}]
        result = event_tagger.resolve_conflicts(events)
        expected = [{START: 1, END:  8},
                    {START: 2, END:  4},
                    {START: 3, END:  6}]
        self.assertListEqual(expected, result)        

    def test_event_tagger(self):
        text = Text('Väga sage kõhukinnisus. Sagedane sümptom on peavalu.')
        event_tagger = EventTagger('data/event vocabulary.csv', 'naive', 'ALL')
        event_tagger.tag_events(text)
