
# episode-miner

Provides methods to find events from Estnltk's Text object based on user defined vocabulary. Stores the results in  'events' layer of Text object. Uses WinEpi algorithm to find frequent serial episodes in event sequence.

## Installation
```
git clone https://github.com/estnltk/episode-miner.git
cd episode-miner
pip install . -r requirements.txt
```
## Usage
...

## [EventText](docs/EventText.ipynb)

A subclass of **Text** containing 'events' layer.

## [EventTagger](docs/EventTagger.ipynb)

A class that provides a method for **EventText** to create 'events' layer.

## [Winepi](docs/Winepi.ipynb)

A partial implementation of Winepi algorithm described by Mannila, Toivonen and Verkamo in *Discovery of Frequent Episodes in Event Sequences*, 1997.
