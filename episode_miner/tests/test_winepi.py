import unittest
from episode_miner import Episode


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
    pass #TODO: 
