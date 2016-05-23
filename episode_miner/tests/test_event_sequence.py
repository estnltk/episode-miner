import unittest
from episode_miner import Event, EventSequence, EventText, EventTagger

class EventTest(unittest.TestCase):
    
    def test_initialization(self):
        event = Event('midagi', 23)
        self.assertEqual(event.event_type, 'midagi')
        self.assertEqual(event.event_time, 23)

    def test_lt(self):
        self.assertTrue(Event(2, 2) < Event(1, 3))
        self.assertFalse(Event(1, 2) < Event(2, 2))
        self.assertFalse(Event(1, 4) < Event(2, 3))

    def test_eq(self):
        self.assertTrue(Event(1, 2) == Event(1, 2))
        self.assertFalse(Event(None, None) == None)
        self.assertFalse(Event(1, 2) == Event(2, 2))
        self.assertFalse(Event(1, 4) == Event(1, 3))

    def test_shift(self):
        event = Event('midagi', 23)
        event.shift(7)
        self.assertEqual(event.event_time, 30)
        

class EventSequenceTest(unittest.TestCase):
    
    def test_simple_initialization(self):
        sequence_of_events = [
                              Event('kuus', 15),
                              Event('seitse', 16),
                              Event('kaks', 9), 
                              Event('kolm', 13),
                              Event('üks', 5), 
                              Event('viis', 14),
                              Event('neli', 13)
                              ]
        event_sequence = EventSequence(sequence_of_events=sequence_of_events, start=9, end=15)
        sequence_of_events_result = [
                              Event('kaks', 9), 
                              Event('kolm', 13),
                              Event('neli', 13),
                              Event('viis', 14)
                              ]
        
        self.assertEqual(event_sequence.start, 9)
        self.assertEqual(event_sequence.end, 15)
        self.assertListEqual(event_sequence.sequence_of_events, sequence_of_events_result)


    
    def test_initialization_by_EventText(self):
        event_vocabulary = [{'term': 'kakskümmend viis'}, 
                            {'term': 'seitse'}]    
        event_tagger = EventTagger(event_vocabulary, search_method='naive', conflict_resolving_strategy='ALL', return_layer=True)
        event_text = EventText('Arv kakskümmend viis on suurem kui seitse.', event_tagger=event_tagger)

        event_sequence = EventSequence(event_text=event_text, classificator='term', time_scale='start')
        self.assertEqual(event_sequence.end, 42)
        self.assertEqual(event_sequence.start, 0)
        self.assertListEqual(event_sequence.sequence_of_events, 
                             [Event('kakskümmend viis', 4), Event('seitse', 35)])

        event_sequence = EventSequence(event_text=event_text, classificator='term', time_scale='start', 
                                       start=3, end=35)
        self.assertEqual(event_sequence.end, 35)
        self.assertEqual(event_sequence.start, 3)
        self.assertListEqual(event_sequence.sequence_of_events, 
                             [Event('kakskümmend viis', 4)])

        event_sequence = EventSequence(event_text=event_text, classificator='term', time_scale='cstart')
        self.assertEqual(event_sequence.end, 22)
        self.assertEqual(event_sequence.start, 0)
        self.assertListEqual(event_sequence.sequence_of_events, 
                             [Event('kakskümmend viis', 4), Event('seitse', 20)])

        event_sequence = EventSequence(event_text=event_text, classificator='term', time_scale='wstart')
        self.assertEqual(event_sequence.start, 0)
        self.assertEqual(event_sequence.end, 7)
        self.assertListEqual(event_sequence.sequence_of_events, 
                             [Event('kakskümmend viis', 1), Event('seitse', 5)])

        event_text = EventText('Sündmusteta tekst.', event_tagger=event_tagger)

        event_sequence = EventSequence(event_text=event_text, classificator='term', time_scale='cstart')
        self.assertEqual(event_sequence.start, 0)
        self.assertEqual(event_sequence.end, 18)
        self.assertEqual(len(event_sequence.sequence_of_events), 0)

        event_sequence = EventSequence(event_text=event_text, classificator='term', time_scale='wstart')
        self.assertEqual(event_sequence.start, 0)
        self.assertEqual(event_sequence.end, 3)
        self.assertEqual(len(event_sequence.sequence_of_events), 0)

    def test_find_examples(self):
        sequence_of_events = [
                              Event('a', 1),
                              Event('b', 2),
                              Event('b', 3), 
                              Event('a', 4),
                              Event('c', 5),
                              Event('b', 6), 
                              Event('c', 6)
                              ]
        event_sequence = EventSequence(sequence_of_events=sequence_of_events, start=0, end=7)
        result = event_sequence.find_episode_examples(('a', 'b'), 3)
        result = tuple(result)
        expected = ([Event('a', 1), Event('b', 2)], 
                    [Event('a', 1), Event('b', 3)], 
                    [Event('a', 4), Event('b', 6)])
        self.assertTupleEqual(result, expected)
