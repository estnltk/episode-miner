
# episode-miner

Provides methods to find events from text based on user defined vocabulary. Stores the result in ```'events'``` layer of ```EventText``` object. Uses Winepi algorithm to find frequent serial episodes in event sequence.

## Installation
```
git clone https://github.com/estnltk/episode-miner.git
cd episode-miner
pip install . -r requirements.txt
```
## Usage


```python
from episode_miner import EventTagger, EventText, EventSequence, collection_of_frequent_episodes
from pprint import pprint
from IPython.display import HTML
```

In this example we find from the text


```python
event_vocabulary = [{'term': 'üks'}, 
                    {'term': 'kaks'}]    
event_tagger = EventTagger(event_vocabulary)
event_text = EventText('üks kaks kolm neli kolm kaks üks kaks kolm neli kolm üks kaks', event_tagger=event_tagger)
event_sequence = EventSequence(event_text=event_text, classificator='term', time_scale='start')
html = event_sequence.pretty_print()
HTML(html)
```




<!DOCTYPE html>
<html>
    <head>
        <link rel="stylesheet" type="text/css" href="prettyprinter.css">
        <meta charset="utf-8">
        <title>PrettyPrinter</title>
    </head>
    <style>


		mark {
			background:none;
		}
		mark.background_0 {
			background-color: red;
		}
		mark.background_1 {
			background-color: green;
		}

    </style>
    <body>

		<p><mark class="background_0">üks</mark> <mark class="background_1">kaks</mark> kolm neli kolm <mark class="background_1">kaks</mark> <mark class="background_0">üks</mark> <mark class="background_1">kaks</mark> kolm neli kolm <mark class="background_0">üks</mark> <mark class="background_1">kaks</mark></p>

	</body>
</html>



frequent serial episodes which consist of words ```üks``` and ```kaks```. Let the width of the Winepi search window be 30 characters and minimal relative frequency of serial episodes be 20%.


```python
frequent_episodes = collection_of_frequent_episodes(event_sequence, 30, 0.3, False, True)
pprint(frequent_episodes)
```

    [83 ('üks',),
     83 ('kaks',),
     76 ('üks', 'kaks'),
     34 ('kaks', 'üks'),
     36 ('kaks', 'kaks'),
     27 ('kaks', 'üks', 'kaks')]


It turns out that the episode ```('kaks', 'üks', 'kaks')``` appears in 27 Winepi windows. Since the length of the text is 61 characters, the relative frequency of this episode is 27 / (61 + 30 - 1) = 30%. Find all instances of that episode.


```python
examples = event_sequence.find_episode_examples(('kaks','üks', 'kaks'), 30)
html = event_sequence.pretty_print(sequence_of_events_generator=examples)
HTML(html)
```




<!DOCTYPE html>
<html>
    <head>
        <link rel="stylesheet" type="text/css" href="prettyprinter.css">
        <meta charset="utf-8">
        <title>PrettyPrinter</title>
    </head>
    <style>


		mark {
			background:none;
		}
		mark.background_0 {
			background-color: red;
		}
		mark.background_1 {
			background-color: green;
		}

    </style>
    <body>

		<p>üks <mark class="background_1">kaks</mark> kolm neli kolm kaks <mark class="background_0">üks</mark> <mark class="background_1">kaks</mark> kolm neli kolm üks kaks</p>
		<p>üks kaks kolm neli kolm <mark class="background_1">kaks</mark> <mark class="background_0">üks</mark> <mark class="background_1">kaks</mark> kolm neli kolm üks kaks</p>
		<p>üks kaks kolm neli kolm kaks üks <mark class="background_1">kaks</mark> kolm neli kolm <mark class="background_0">üks</mark> <mark class="background_1">kaks</mark></p>

	</body>
</html>



For futher details see [docs](docs).
