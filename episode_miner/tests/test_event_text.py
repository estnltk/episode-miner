import unittest

from episode_miner import EventText
from estnltk.taggers import EventTagger

class EventTextTest(unittest.TestCase):
    
    def test_events(self):
        class TestTagger():
            def tag(self, text):
                return 'events layer'
            
        tagger = TestTagger()
        event_text = EventText('Üks kaks.', event_tagger=tagger)
        
        self.assertEqual('events layer', event_text.events)
        
    def test_events_(self):
        event_vocabulary = [{'term': 'üks'}, 
                            {'term': 'kaks'}]
        
        event_tagger = EventTagger(event_vocabulary,
                                   return_layer=True)

        event_text = EventText('üks kaks kolm neli', event_tagger=event_tagger)
        
        self.assertEqual('üks kaks kolm neli', event_text.text)
        
        expected = [
                {'term': 'üks',  'start': 0, 'end': 3, 'wstart_raw': 0, 'wend_raw': 1, 'cstart': 0, 'wstart': 0, }, 
                {'term': 'kaks', 'start': 4, 'end': 8, 'wstart_raw': 1, 'wend_raw': 2, 'cstart': 2, 'wstart': 1}]
        self.assertListEqual(expected, event_text.events)
