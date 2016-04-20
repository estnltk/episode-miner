from pprint import pprint
from EventText.EventText import EventText, EventTagger
from Winepi.Winepi import collection_of_frequent_episodes


# event_types_and_classes = [('Väga sage', 'keyword'), 
#                            ('Sage', 'keyword'),
#                            ('Aeg-ajalt', 'keyword'),
#                            ('Harv', 'keyword'),
#                            ('Väga harv', 'keyword'),
#                            ('Teadmata', 'keyword'),
#                            ('Kõrvaltoimetest teavitamine', 'keyword'),
#                            ('Kui teil tekib ükskõik milline kõrvaltoime, pidage nõu oma arsti või apteekriga.', 'standard_text'),
#                            ('Kõrvaltoime võib olla ka selline, mida selles infolehes ei ole nimetatud.', 'standard_text'),
#                            ('Kõrvaltoimetest võite ka ise teavitada www.ravimiamet.ee kaudu.', 'standard_text'),
#                            ('Teavitades aitate saada rohkem infot ravimi ohutusest.', 'standard_text'),
#                            ('Nagu kõik ravimid, võib ka see ravim põhjustada kõrvaltoimeid, kuigi kõigil neid ei teki.', 'standard_text'),
#                            ('peavalu', 'symptom'),
#                            ('kõhukinnisus', 'symptom'),
#                            ('iiveldus', 'symptom')
#                            ]
# event_types = [event_type for event_type, event_class in event_types_and_classes
#                 if event_class == 'keyword' or event_class == 'symptom']



event_vocabulary_file = '/home/paul/workspace/MyTestProject/data/event vocabulary.csv'
text = 'Sage kõrvaltoime sellel ravimil on peavalu.'
window_width = 30
min_frequency = 0.2

event_tagger = EventTagger(event_vocabulary_file, consider_gaps=True)
event_text = EventText(text, event_tagger = event_tagger)
event_text.events()
pprint(event_text)
event_sequence = event_text.event_sequence(count_event_time_by='word', classificator='term')
print(event_sequence.sequence_of_events, event_sequence.start, event_sequence.end)
collection_of_frequent_episodes(event_sequence, 'default', window_width, min_frequency)
