'''
Created on 05.04.2016

@author: paul
'''
import pandas

from EventText.EventText import EventText, EventTagger
from Winepi.Winepi import collection_of_frequent_episodes_new
import json

with open('/home/paul/workspace/MyTestProject/data/korvalmojud_lyhendatud.html', 'r') as f:
    html = f.read()
html = html.replace('<br/>', ' ')
dfs = pandas.read_html(html)

event_vocabulary_file = '/home/paul/workspace/MyTestProject/data/event vocabulary.csv'

event_tagger = EventTagger(event_vocabulary_file)

event_sequences = []
for string in dfs[0][5]:
    event_text = EventText(string, event_tagger = event_tagger)
    event_text.events()
    event_sequence = event_text.event_sequence(count_event_time_by='word', classificator='type')
    event_sequences.append(event_sequence)

window_width = 900
min_frequency = 0.3
number_of_examples = 10

frequent_episodes, examples = collection_of_frequent_episodes_new(event_sequences, window_width, min_frequency, only_full_windows=False, gaps_skipping=True, number_of_examples = number_of_examples)

frequent_episodes_to_file = []
examples_to_file = []
for episode in frequent_episodes:
    frequent_episodes_to_file.append([episode.relative_frequency, episode])
    
    examples_to_file.append([])
    for example in examples[episode]:
        example_text = example[0].text['text']
        event_spans = []
        for event in example:
            event_spans.append([event.start, event.end])
        examples_to_file[-1].append([example_text, event_spans])
with open('/home/paul/workspace/MyTestProject/data/frequent_episodes.json', 'w') as f:
    json.dump(frequent_episodes_to_file, f)            
with open('/home/paul/workspace/MyTestProject/data/examples_of_frequent_episodes.json', 'w') as f:
    json.dump(examples_to_file, f)
