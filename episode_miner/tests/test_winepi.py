import unittest
from episode_miner import Episode, Event, EventSequence
from episode_miner.winepi import episode_frequences,\
    find_sequential_episodes, abs_support, rel_support


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


class WinepiTest(unittest.TestCase):

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
        event_sequence = EventSequence(sequence_of_events=sequence_of_events, start=0, end=8)
        e1 = Episode(('a'))
        e2 = Episode(('a', 'b'))
        e3 = Episode(('b', 'b'))
        e4 = Episode(('b'))
        collection_of_serial_episodes = (e1, e2, e3, e4)
        episode_frequences(event_sequence, collection_of_serial_episodes, 5, False, True)
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
        event_sequence = EventSequence(sequence_of_events=sequence_of_events, start=0, end=8)
        e1 = Episode(('a'))
        e2 = Episode(('a', 'b'))
        e3 = Episode(('b', 'b'))
        e4 = Episode(('b'))
        collection_of_serial_episodes = (e1, e2, e3, e4)
        episode_frequences(event_sequence, collection_of_serial_episodes, 5, True, True)
        self.assertEqual(e1.abs_support, 2)
        self.assertEqual(e2.abs_support, 2)
        self.assertEqual(e3.abs_support, 3)
        self.assertEqual(e4.abs_support, 4)

        # empty sequence_of_events
        sequence_of_events = []
        event_sequence = EventSequence(sequence_of_events=sequence_of_events, start=0, end=8)
        e1 = Episode(('a'))
        collection_of_serial_episodes = (e1,)
        episode_frequences(event_sequence, collection_of_serial_episodes, 3, False, True)
        self.assertEqual(e1.abs_support, 0)
        
        # empty collection_of_serial_episodes
        sequence_of_events = [
                      Event('a', 1),
                      Event('b', 3),
                      Event('c', 6)
                      ]
        event_sequence = EventSequence(sequence_of_events=sequence_of_events, start=0, end=8)
        collection_of_serial_episodes = []
        result = episode_frequences(event_sequence, collection_of_serial_episodes, 3, False, True)
        self.assertListEqual(result, [])


        # allow_intermediate_events==False
        sequence_of_events = [
                      Event('a', 1),
                      Event('b', 3),
                      Event('c', 3),
                      Event('d', 5)
                      ]
        event_sequence = EventSequence(sequence_of_events=sequence_of_events, start=0, end=6)
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
        episode_frequences(event_sequence, collection_of_serial_episodes, 5, False, False)
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
        event_sequence = EventSequence(sequence_of_events=sequence_of_events, start=0, end=6)
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
        episode_frequences(event_sequence, collection_of_serial_episodes, 5, False, True)
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

    def test_collection_of_frequent_episodes(self):
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
        event_sequences=(event_sequence_1, event_sequence_2)
        result = find_sequential_episodes(event_sequence_1, 3, 0.1, False, False)
        self.assertTrue(Episode(('a',)) in result)
        self.assertTrue(Episode(('b',)) in result)
        self.assertTrue(Episode(('a', 'b')) in result)

        result = find_sequential_episodes(event_sequences, 3, 0.083, False, False)
        self.assertEqual(len(result), 4)
        result = find_sequential_episodes(event_sequences, 3, 0.166, False, False)
        self.assertEqual(len(result), 3)
        result = find_sequential_episodes(event_sequences, 3, 0.5, False, False)
        self.assertEqual(len(result), 2)
        result = find_sequential_episodes(event_sequences, 3, 0.51, False, False)
        self.assertListEqual(result, [])

        
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
        event_sequences=(event_sequence_1, event_sequence_2)

        result = abs_support(event_sequence_1, Episode(('a',)), 3, False, False)
        self.assertEqual(result, [3])
        result = abs_support(event_sequences, Episode(('a',)), 3, False, False)
        self.assertEqual(result, [6])
        result = abs_support(event_sequences, Episode(('a','b')), 3, False, False)
        self.assertEqual(result, [1])
        result = abs_support(event_sequences, Episode(('a','a')), 3, False, False)
        self.assertEqual(result, [0])
        
        result = rel_support(event_sequence_1, Episode(('a',)), 3, False, False)
        self.assertAlmostEqual(result[0], 3/6, 5)
        result = rel_support(event_sequences, Episode(('a',)), 3, False, False)
        self.assertAlmostEqual(result[0], 6/12, 5)

        result = rel_support(event_sequences, 
                             (Episode(('a',)), Episode(('a','b')), Episode(('a','a'))), 
                             3, False, False)
        self.assertListEqual(result, [6/12, 1/12, 0])
        result = rel_support(event_sequences, Episode(('a','a')), 3, False, False)
        self.assertEqual(result[0], 0)

        
