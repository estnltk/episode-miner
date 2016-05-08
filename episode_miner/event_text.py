from estnltk import Text
from cached_property import cached_property

EVENTS = 'events'

event_tagger = None

class EventText(Text):
    """Subclass of Estnltk's Text. Introduces ``events`` layer.
    """

    def __init__(self, *args, **kwargs):
        """Initialize new EventText instance.

        Parameters
        ----------
        event_tagger: episode-miner.EventTagger
            Tagger for annotaitng events.
        """
        super(EventText, self).__init__(*args, **kwargs)
        self.__event_tagger = kwargs.get('event_tagger', event_tagger)
        if self.__event_tagger == None:
            raise Exception('No event tagger given.') # default_event_tagger peaks hoopis olema
        

    @cached_property
    def events(self):    
        """The list of events representing ``events`` layer elements."""
        if not self.is_tagged(EVENTS):
            self.tag_events()
        return self[EVENTS]

    def tag_events(self):
        """Tags events in this Text instance. Creates ``events`` layer."""
        self[EVENTS] = self.__event_tagger.tag_events(self)
        return self 
