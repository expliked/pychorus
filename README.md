# pychorus
A simple Python API wrapper library for the Clone Hero chart searching tool Chorus.

# Requirements
pychorus requires `gdown`, a Google Drive download library, and `requests`.<br>
Install them both by running these commands<br>
`pip install gdown`<br>
`pip install requests`<br>

# Functions
| Function | Arguments | What it does |
| :---:    | :---:     | :---:        |
| ` pychorus.search()` -> `list[pychorus.Song]` | `generic` (optional),<br> `name` (optional keyword),<br> `artist` (optional keyword),<br> `album `(optional keyword),<br> `genre` (optional keyword),<br> `year` (optional keyword),<br> `charter` (optional keyword),<br> `year` (optional keyword) | Returns the top 10 charts that best match your query. |
| `pychorus.latest()` -> `list[pychorus.Song]` | None | Returns 20 of the latest charts added to Chorus |
| `pychorus.random()` -> `list[pychorus.Song]` | None | Returns 20 random charts from Chorus |
| `pychorus.count()` -> `int` | None | Returns the number of songs hosted on Chorus |

# Objects
`pychorus.Song`
- `pychorus.Song.info()` -> `str`: Returns basic info about the song such as name or artist.
- `pychorus.Song.all_info()` -> `str`: Returns all info of the song.
- `pychorus.Song.download()` -> `None`: Downloads the song from Google Drive to the current directory. (as a zip, rar, 7z, etc).

# Some examples
```python
import pychorus

# Get the top result for songs with the name "Raining Blood" and with artist name "Slayer"
song = pychorus.search(name = "Raining Blood", artist = "Slayer")[0]

# The output archive file will be named "Slayer - Raining Blood.zip"
song.download(name = "Slayer - Raining Blood")

# Gets the top charts by ExileLord
songs = pychorus.search(charter = "ExileLord")

for song in songs:
    print(song.info())

```

# Known limitations
- Occasionally, Chorus will have a song/setlist that links to a YouTube link, and currently this library won't be able to download those.

# Why did I make this module?
I find navigating the website a little clunky, and downloading from the Google Drive is a slow pain with the "preparing" and "zipping" that Google does behind the scenes when downloading. This module downloads much, much faster than using a browser. And also, I'm just a hobbyist and thought it'd be fun to make a module for my favorite rhythm game :)

# Wrapping up
You can use this module for any project you please.

If you get any issues please report them to the issues page and I'll try to fix them right away.
