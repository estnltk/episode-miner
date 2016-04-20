#from Winepi.Winepi import collection_of_frequent_episodes
from Winepi import collection_of_frequent_episodes

#collection_of_frequent_episodes()


C = collection_of_frequent_episodes(['nagu', 'vaid', 'nagu', 'seega', 'vaid', 'nagu'], [['vaid'],['seega']], 4, .1)
for episode in C:
    for b in episode:
        print(' '.join(b), end = ', ')
    print()

#event_types = ['episode', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'õ', 'ä', 'ö', 'ü', 'x', 'y', 'z']
#C = collection_of_frequent_episodes(event_sequence, event_types, 5, .1)
#for episode in C:
#    for b in episode:
#        print(''.join(b), end = ', ')
#    print()
