
# episode-miner

Provides methods to find events from text based on user defined vocabulary. Stores the result in ```'events'``` layer of ```EventText``` object. Uses Winepi algorithm to find frequent serial episodes in event sequence.

## Installation
```bash
git clone https://github.com/estnltk/episode-miner.git
cd episode-miner
python setup.py install

# or pre-install requieremets separately: 
pip install -r requirements.txt
```
## Usage
For details see the [docs](docs).
### Quick example
Find frequent episodes from text.


```python
from estnltk.taggers import EventTagger
from episode_miner import EventText, EventSequences, Episode, Episodes

event_vocabulary = [{'term': 'üks'}, 
                    {'term': 'kaks'}]    
event_tagger = EventTagger(event_vocabulary, case_sensitive=False, return_layer=True)
event_text = EventText('Üks kaks kolm neli kolm. Kaks üks kaks kolm neli kolm üks kaks.', event_tagger=event_tagger)
event_sequences = EventSequences(event_texts=[event_text], 
                                 classificator='term', 
                                 time_scale='start')
frequent_episodes = event_sequences.find_serial_episodes(window_width=31, 
                                                         min_frequency=0.3, 
                                                         only_full_windows=False, 
                                                         allow_intermediate_events=True)
frequent_episodes
```




    [('üks'),
     ('kaks'),
     ('üks', 'kaks'),
     ('kaks', 'üks'),
     ('kaks', 'kaks'),
     ('kaks', 'üks', 'kaks')]


