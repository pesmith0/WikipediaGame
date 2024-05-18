# WikipediaGame

This README is a modified version of the original WikipediaGame README, and contains some redundant information originally from WGIP.md.

## Installation

(these instructions should work under GNU/Linux and Macos and WSL)

Prerequisites: Python 3.11, termcolor (note: setup.sh should install these automatically)

Installing termcolor manually:
```
pip install termcolor
```

Installing WikipediaGame:

```
git clone https://github.com/pesmith0/WikipediaGame
cd WikipediaGame/server
source setup.sh
```

Starting the server:

```
python server.py
```

Play the game on [`localhost:5000`](http://127.0.0.1:5000/) (this link will only work after you started the server on your machine (watch the console in case the port number changed to eg `5001`)).

The console output is bright green, cyan, and dark green respectively for the three separate searches (explained in Description).

## Limitations

- The UI works as expected only for chrome-based browsers (Chrome, Brave, ...).
- The target page must be the real URL, not a redirection URL (for example, United_States will work, but not United_states or USA)
- If the above point is violated, the search will run indefinitely, and the cyan output will have a lot of red error messages stating that a backlink to the target URL cannot be found (because it is not the real URL).
- Implemented via HTTP requests (no websocket connection between client and server).
- Users are identified by IP address (no cookies or sessions).
- Only works for Wikipedia, as it relies on various design specifications of Wikipedia to be fast

## Parameters

- `RATELIMIT` in `server.py`.
- `TIMEOUT` in `crawler.py`.

## How it works

[This file](https://github.com/pesmith0/WikipediaGame/blob/main/contributions.md) contains information on how the algorithm works and how it was tested. The total search time (added from all three phases) is displayed on the webpage after the search is completed.

## Future work

- more fallbacks if the assumptions fail; for example, category pages can contain multiple subpages of subcategories, which the algorithm currently doesn't know how to search through
- multi-threading in which some of the three steps in the design could work simultaneously; this would require some thought as the current design depends on the 3 steps happening in sequence, but the benefits would be large as the main bottleneck is the time it takes to request a page from Wikipedia
- options to prioritize a shorter path length over the time spent to calculate it; could use other Wikipedia Game optimization strategies for this end, or to continue performing searches in the hope of finding a shorter path
- using the Wikipedia API might allow faster speed, though one of the impressive points of this optimization is that it reaches such efficiency without needing to use the API