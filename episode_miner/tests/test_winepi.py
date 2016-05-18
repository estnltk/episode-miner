import unittest
from episode_miner import Episode, Event, EventSequence
from episode_miner.winepi import episode_frequences,\
    collection_of_frequent_episodes


class EpisodeTest(unittest.TestCase):
        
    episode = Episode(['üks', 'kaks', 'kolm'])

    def test_initialization(self):
        episode = Episode(['üks', 'kaks', 'kolm'])
        self.assertListEqual(episode.initialized, [None, None, None])
        self.assertEqual(episode.freq_count, 0)
        self.assertEqual(episode.relative_frequency, 0)
        self.assertTupleEqual(episode, ('üks', 'kaks', 'kolm'))

    def test_reset_initialized(self):
        episode = Episode(['üks', 'kaks', 'kolm'])
        episode.initialized = [4, 6, 8]
        self.assertListEqual(episode.initialized, [4, 6, 8])
        episode.reset_initialized()
        self.assertListEqual(episode.initialized, [None, None, None])


class WinepiTest(unittest.TestCase):

    def test_episode_frequences(self):
        # general use case, only full windows==False
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
        self.assertEqual(e1.freq_count, 5)
        self.assertEqual(e2.freq_count, 3)
        self.assertEqual(e3.freq_count, 3)
        self.assertEqual(e4.freq_count, 7)

        # general use case, only full windows==True
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
        self.assertEqual(e1.freq_count, 2)
        self.assertEqual(e2.freq_count, 2)
        self.assertEqual(e3.freq_count, 3)
        self.assertEqual(e4.freq_count, 4)

        # empty sequence_of_events
        sequence_of_events = []
        event_sequence = EventSequence(sequence_of_events=sequence_of_events, start=0, end=8)
        e1 = Episode(('a'))
        collection_of_serial_episodes = (e1,)
        episode_frequences(event_sequence, collection_of_serial_episodes, 3, False, True)
        self.assertEqual(e1.freq_count, 0)
        
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

        # gap_skip==False
        sequence_of_events = [
                      Event('a', 1),
                      Event('b', 3)
                      ]
        event_sequence = EventSequence(sequence_of_events=sequence_of_events, start=0, end=4)
        e3 = Episode(('a', 'b'))
        collection_of_serial_episodes = (e3,)
        episode_frequences(event_sequence, collection_of_serial_episodes, 5, False, False)
        self.assertEqual(e3.freq_count, 0)

        # gap_skip==False
        sequence_of_events = [
                      Event('a', 1),
                      Event('c', 2),
                      Event('b', 2)
                      ]
        event_sequence = EventSequence(sequence_of_events=sequence_of_events, start=0, end=4)
        e3 = Episode(('a', 'b'))
        collection_of_serial_episodes = (e3,)
        episode_frequences(event_sequence, collection_of_serial_episodes, 3, False, False)
        self.assertEqual(e3.freq_count, 2)

    def test_collection_of_frequent_episodes(self):
        sequence_of_events = [
                      Event('a', 1),
                      Event('b', 3)
                      ]
        event_sequence = EventSequence(sequence_of_events=sequence_of_events, start=0, end=4)
        e4 = Episode(('a', 'b'))
        e6 = Episode(('b',))
        collection_of_serial_episodes = ((e4, e6))
        result = episode_frequences(event_sequence, collection_of_serial_episodes, 3, False, False)
        #print(result)
        #Expected = (Episode(('a','b')), Episode(('b',)))
        #print(expected)
        #self.assertTupleEqual(result, expected)
