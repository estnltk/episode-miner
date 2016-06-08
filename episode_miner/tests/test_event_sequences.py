import unittest
from os.path import exists as file_exists
from os import remove as file_remove

from episode_miner import Event, EventSequence, EventSequences, EventText,\
                          EventTagger, Episode, Episodes

class EpisodeTest(unittest.TestCase):
        
    episode = Episode(['üks', 'kaks', 'kolm'])

    def test_initialization(self):
        episode = Episode(['üks', 'kaks', 'kolm'])
        self.assertListEqual(episode._initialized, [None, None, None])
        self.assertEqual(episode.abs_support, 0)
        self.assertEqual(episode.rel_support, 0)
        self.assertTupleEqual(episode, ('üks', 'kaks', 'kolm'))

    def test_reset_initialized(self):
        episode = Episode(['üks', 'kaks', 'kolm'])
        episode._initialized = [4, 6, 8]
        self.assertListEqual(episode._initialized, [4, 6, 8])
        episode.reset_initialized()
        self.assertListEqual(episode._initialized, [None, None, None])


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
                              Event('a', 2),
                              Event('b', 2),
                              Event('b', 3), 
                              Event('a', 4),
                              Event('c', 5),
                              Event('b', 6), 
                              Event('c', 6),
                              Event('a', 7), 
                              Event('c', 8)
                              ]
        event_sequences = EventSequences(sequence_of_events=sequence_of_events, start=1, end=9)
        episodes = Episodes(Episode(('a', 'b')))
        event_sequences.find_episode_examples(episodes=episodes, 
                                              window_width=3, 
                                              allow_intermediate_events=True,
                                              number_of_examples='ALL')
        result = episodes[0].examples
        expected = EventSequences(event_sequences=(EventSequence(sequence_of_events=[Event('a', 1), Event('b', 2)]), 
                                                   EventSequence(sequence_of_events=[Event('a', 1), Event('b', 3)]), 
                                                   EventSequence(sequence_of_events=[Event('a', 2), Event('b', 3)]), 
                                                   EventSequence(sequence_of_events=[Event('a', 4), Event('b', 6)])))
        self.assertTrue(result == expected)

        event_sequences.find_episode_examples(episodes=episodes, 
                                              window_width=3, 
                                              allow_intermediate_events=False,
                                              number_of_examples='ALL')
        result = episodes[0].examples
        expected = EventSequences(event_sequences=(EventSequence(sequence_of_events=[Event('a', 1), Event('b', 2)]), 
                                                   EventSequence(sequence_of_events=[Event('a', 2), Event('b', 3)])))
        self.assertTrue(result == expected)

        sequence_of_events = [
                              Event('b', 1),
                              Event('a', 2),
                              Event('b', 3),
                              Event('a', 4),
                              Event('b', 5)
                             ]
        event_sequences = EventSequences(sequence_of_events=sequence_of_events, start=1, end=6)
        episodes = Episodes(Episode(('b', 'a', 'b')))
        event_sequences.find_episode_examples(episodes=episodes, 
                                              window_width=6, 
                                              allow_intermediate_events=True,
                                              number_of_examples='ALL')
        result = episodes[0].examples
        expected = EventSequences(event_sequences=(EventSequence(sequence_of_events=[Event('b', 1), Event('a', 2), Event('b', 3)]), 
                                                   EventSequence(sequence_of_events=[Event('b', 1), Event('a', 2), Event('b', 5)]), 
                                                   EventSequence(sequence_of_events=[Event('b', 1), Event('a', 4), Event('b', 5)]), 
                                                   EventSequence(sequence_of_events=[Event('b', 3), Event('a', 4), Event('b', 5)])))
        self.assertTrue(result == expected)


        
        episodes = Episodes(Episode(('b', 'a', 'b')))
        event_sequences.find_episode_examples(episodes=episodes, 
                                              window_width=6, 
                                              allow_intermediate_events=False,
                                              number_of_examples='ALL')
        result = episodes[0].examples
        expected = EventSequences(event_sequences=(EventSequence(sequence_of_events=[Event('b', 1), Event('a', 2), Event('b', 3)]), 
                                                   EventSequence(sequence_of_events=[Event('b', 3), Event('a', 4), Event('b', 5)])))
        self.assertTrue(result == expected)
        



        episodes = Episodes(Episode(('b',)))
        event_sequences.find_episode_examples(episodes=episodes, 
                                              window_width=6, 
                                              allow_intermediate_events=True,
                                              number_of_examples='ALL')
        result = episodes[0].examples
        expected = EventSequences(event_sequences=(EventSequence(sequence_of_events=[Event('b', 1)]), 
                                                   EventSequence(sequence_of_events=[Event('b', 3)]), 
                                                   EventSequence(sequence_of_events=[Event('b', 5)])))
        self.assertTrue(result == expected)


        episodes = Episodes(Episode(('b',)))
        event_sequences.find_episode_examples(episodes=episodes, 
                                              window_width=6, 
                                              allow_intermediate_events=False,
                                              number_of_examples='ALL')
        result = episodes[0].examples
        expected = EventSequences(event_sequences=(EventSequence(sequence_of_events=[Event('b', 1)]), 
                                                   EventSequence(sequence_of_events=[Event('b', 3)]), 
                                                   EventSequence(sequence_of_events=[Event('b', 5)])))
        self.assertTrue(result == expected)



    def test_to_json(self):
        sequence_of_events_1 = [
                              Event('a', 1),
                              Event('a', 2),
                              ]
        sequence_of_events_2 = [
                              Event('c', 5),
                              Event('b', 6), 
                              Event('c', 6),
                              Event('a', 7), 
                              Event('c', 8)
                              ]
        event_sequence_1 = EventSequences(sequence_of_events=sequence_of_events_1, start=1, end=4)
        event_sequence_2 = EventSequences(sequence_of_events=sequence_of_events_2, start=3, end=9)
        event_sequences = EventSequences(event_sequences=(event_sequence_1, event_sequence_2))

        result = event_sequences.to_json()
        expected='''[[[["a", 1], ["a", 2]]], [[["c", 5], ["b", 6], ["c", 6], ["a", 7], ["c", 8]]]]'''
        self.assertEqual(expected, result)

    def test_episode_frequences(self):
        # general case, only_full_windows==False
        sequence_of_events = [
                      Event('a',-1),
                      Event('a', 1),
                      Event('b', 3),
                      Event('c', 4),
                      Event('b', 5),
                      Event('a', 8)
                      ]
        event_sequences = EventSequences(sequence_of_events=sequence_of_events, start=0, end=8)
        e1 = Episode(('a'))
        e2 = Episode(('a', 'b'))
        e3 = Episode(('b', 'b'))
        e4 = Episode(('b'))
        episodes = Episodes((e1, e2, e3, e4))
        event_sequences.episode_frequences(episodes, 5, False, True)
        self.assertEqual(e1.abs_support, 5)
        self.assertEqual(e2.abs_support, 3)
        self.assertEqual(e3.abs_support, 3)
        self.assertEqual(e4.abs_support, 7)
 
        # general case, only_full_windows==True
        sequence_of_events = [
                      Event('a', 1),
                      Event('b', 3),
                      Event('c', 4),
                      Event('b', 5),
                      Event('a', 8)
                      ]
        event_sequences = EventSequences(sequence_of_events=sequence_of_events, start=0, end=8)
        e1 = Episode(('a'))
        e2 = Episode(('a', 'b'))
        e3 = Episode(('b', 'b'))
        e4 = Episode(('b'))
        collection_of_serial_episodes = (e1, e2, e3, e4)
        event_sequences.episode_frequences(collection_of_serial_episodes, 5, True, True)
        self.assertEqual(e1.abs_support, 2)
        self.assertEqual(e2.abs_support, 2)
        self.assertEqual(e3.abs_support, 3)
        self.assertEqual(e4.abs_support, 4)
 
        # empty sequence_of_events
        sequence_of_events = []
        event_sequences = EventSequences(sequence_of_events=sequence_of_events, start=0, end=8)
        e1 = Episode(('a'))
        collection_of_serial_episodes = (e1,)
        event_sequences.episode_frequences(collection_of_serial_episodes, 3, False, True)
        self.assertEqual(e1.abs_support, 0)
         
        # empty collection_of_serial_episodes
        sequence_of_events = [
                      Event('a', 1),
                      Event('b', 3),
                      Event('c', 6)
                      ]
        event_sequences = EventSequences(sequence_of_events=sequence_of_events, start=0, end=8)
        collection_of_serial_episodes = []
        result = event_sequences.episode_frequences(collection_of_serial_episodes, 3, False, True)
        self.assertListEqual(result, [])
 
 
        # allow_intermediate_events==False
        sequence_of_events = [
                      Event('a', 1),
                      Event('b', 3),
                      Event('c', 3),
                      Event('d', 5)
                      ]
        event_sequences = EventSequences(sequence_of_events=sequence_of_events, start=0, end=6)
        e0 = Episode(('a', 'b'))
        e1 = Episode(('a', 'c'))
        e2 = Episode(('b', 'd'))
        e3 = Episode(('c', 'd'))
        e4 = Episode(('a', 'd'))
        e4p= Episode(('d', 'd'))        
        e5 = Episode(('a', 'b', 'd'))
        e6 = Episode(('a', 'c', 'd'))
        e7 = Episode(('a', 'b', 'b'))
        e8 = Episode(('b', 'c', 'd'))
        e9 = Episode(('a', 'b', 'c', 'd'))
        collection_of_serial_episodes = (e0, e1, e2, e3, e4, e4p, e5, e6, e7, e8, e9)
        event_sequences.episode_frequences(collection_of_serial_episodes, 5, False, False)
        self.assertEqual(e0.abs_support, 3)
        self.assertEqual(e1.abs_support, 3)
        self.assertEqual(e2.abs_support, 3)
        self.assertEqual(e3.abs_support, 3)
        self.assertEqual(e4.abs_support, 0)
        self.assertEqual(e5.abs_support, 1)
        self.assertEqual(e6.abs_support, 1)
        self.assertEqual(e7.abs_support, 0)
        self.assertEqual(e8.abs_support, 0)
        self.assertEqual(e9.abs_support, 0)
 
        # allow_intermediate_events==True
        sequence_of_events = [
                      Event('a', 1),
                      Event('b', 3),
                      Event('c', 3),
                      Event('d', 5)
                      ]
        event_sequences = EventSequences(sequence_of_events=sequence_of_events, start=0, end=6)
        e0 = Episode(('a', 'b'))
        e1 = Episode(('a', 'c'))
        e2 = Episode(('b', 'd'))
        e3 = Episode(('c', 'd'))
        e4 = Episode(('a', 'd'))
        e5 = Episode(('a', 'b', 'd'))
        e6 = Episode(('a', 'c', 'd'))
        e7 = Episode(('a', 'b', 'b'))
        e8 = Episode(('b', 'c', 'd'))
        e9 = Episode(('a', 'b', 'c', 'd'))
        collection_of_serial_episodes = (e0, e1, e2, e3, e4, e5, e6, e7, e8, e9)
        event_sequences.episode_frequences(collection_of_serial_episodes, 5, False, True)
        self.assertEqual(e0.abs_support, 3)
        self.assertEqual(e1.abs_support, 3)
        self.assertEqual(e2.abs_support, 3)
        self.assertEqual(e3.abs_support, 3)
        self.assertEqual(e4.abs_support, 1)
        self.assertEqual(e5.abs_support, 1)
        self.assertEqual(e6.abs_support, 1)
        self.assertEqual(e7.abs_support, 0)
        self.assertEqual(e8.abs_support, 0)
        self.assertEqual(e9.abs_support, 0)



 
    def test_find_serial_episodes(self):
        sequence_of_events_1 = [
                      Event('a', 1),
                      Event('b', 3)
                      ]
        event_sequence_1 = EventSequence(sequence_of_events=sequence_of_events_1, start=0, end=4)
        sequence_of_events_2 = [
                      Event('b', 2),
                      Event('a', 3)
                      ]
        event_sequence_2 = EventSequence(sequence_of_events=sequence_of_events_2, start=0, end=4)
        event_sequences=EventSequences(event_sequences=[event_sequence_1, event_sequence_2])
        result = EventSequences(event_sequences=event_sequence_1).find_serial_episodes(3, 0.1, False, False)
        self.assertTrue(Episode(('a',)) in result)
        self.assertTrue(Episode(('b',)) in result)
        self.assertTrue(Episode(('a', 'b')) in result)
 
        result = event_sequences.find_serial_episodes(3, 0.083, False, False)
        self.assertEqual(len(result), 4)
        result = event_sequences.find_serial_episodes(3, 0.166, False, False)
        self.assertEqual(len(result), 3)
        result = event_sequences.find_serial_episodes(3, 0.5, False, False)
        self.assertEqual(len(result), 2)
        result = event_sequences.find_serial_episodes(3, 0.51, False, False)
        self.assertListEqual(result, [])
 
class TestEpisodes(unittest.TestCase):
    
    def test_support(self):
        sequence_of_events_1 = [
                      Event('a', 1),
                      Event('b', 3)
                      ]
        event_sequence_1 = EventSequence(sequence_of_events=sequence_of_events_1, start=0, end=4)
        sequence_of_events_2 = [
                      Event('b', 2),
                      Event('a', 3)
                      ]
        event_sequence_2 = EventSequence(sequence_of_events=sequence_of_events_2, start=0, end=4)
        event_sequences=EventSequences(event_sequences=[event_sequence_1, event_sequence_2])
 
 
        episodes = Episodes((Episode(('a',)), Episode(('a','b')), Episode(('a','a'))))
        event_sequences.support(episodes, 3, only_full_windows=False, allow_intermediate_events=False)
        self.assertListEqual([6, 1, 0], episodes.abs_support())
        self.assertListEqual([6/12, 1/12, 0], episodes.rel_support())
        
    def test_episodes_and_examples_to_json(self):
        episode_1 = Episode(('a', 'b'))
        episode_2 = Episode(('b',))
        examples_1 = EventSequences(event_sequences=(EventSequence(sequence_of_events=[Event('a', 1), Event('b', 2)]), 
                                                     EventSequence(sequence_of_events=[Event('a', 2), Event('b', 3)])))
        examples_2 = EventSequences(event_sequences=(EventSequence(sequence_of_events=[Event('b', 2)]), 
                                                     EventSequence(sequence_of_events=[Event('b', 3)])))
        episode_1.examples = examples_1
        episode_2.examples = examples_2
        episodes = Episodes((episode_1, episode_2))
        
        episodes.examples_to_json('examples.txt')
        episodes.to_json('episodes.txt')
        
        with open('examples.txt') as f:
            result = f.read()
        expected='''[[["a", 1], ["b", 2]], [["a", 2], ["b", 3]]]\n[[["b", 2]], [["b", 3]]]\n'''
        # TODO: test 'episodes.txt'
        self.assertEqual(expected, result)
        self.assertTrue(file_exists('episodes.txt'))
        self.assertTrue(file_exists('examples.txt'))
        file_remove('episodes.txt')
        file_remove('examples.txt')
