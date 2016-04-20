'''
Created on 05.04.2016

@author: paul
'''
from Winepi.Winepi import EventSequence,\
    frequent_serial_episodes_in_event_timetable

#event_sequence = 'mingi pikk jutt maast ja ilmast, milles on korduvaid kombinatsioone'
#collection_of_serial_episodes = ['ai', 'ma', 'mi', 'na', 'no']
#window_width = 20
#min_frequency = 0.1


#print(frequent_serial_episodes(event_sequence, collection_of_serial_episodes, window_width, .5))
#print(frequent_serial_episodes('kkpkr', ['kkr'],3, .5))

#print(frequent_serial_episodes('aa', ['a'], 2, .5))

#print(frequent_serial_episodes('aa', [('a', 'a')], 2, 0.1))


event_sequence = EventSequence([('yks', 1), ('kaks', 2), ('kolm', 4), ('yks', 7)], 0, 8)
print(event_sequence.sequence_of_events)
print(frequent_serial_episodes_in_event_timetable(event_sequence, [['yks', 'kaks'], ['yks','yks']], 7, 0.04))

#print(candidate_serial_episodes( [['tere', 'mina'], ['mina', 'mina']]))
#print(candidate_serial_episodes( [['tere'], ['mina']]))


#C = collection_of_frequent_episodes(['nagu', 'vaid', 'nagu', 'seega', 'vaid', 'nagu'], [['vaid'],['seega']], 4, .1)
#for a in C:
#    for b in a:
#        print(' '.join(b), end = ', ')
#    print()

#event_types = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'õ', 'ä', 'ö', 'ü', 'x', 'y', 'z']
#C = collection_of_frequent_episodes(event_sequence, event_types, 5, .1)
#for a in C:
#    for b in a:
#        print(''.join(b), end = ', ')
#    print()
