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
| ` pychorus.search()` | `generic` (optional),<br> `name` (optional keyword),<br> `artist` (optional keyword),<br> `album `(optional keyword),<br> `genre` (optional keyword),<br> `year` (optional keyword),<br> `charter` (optional keyword),<br> `year` (optional keyword) | Returns the top 10 charts that best match your query. |
| `pychorus.latest()` | None | Returns 20 of the latest charts added to Chorus |
| `pychorus.random()` | None | Returns 20 random charts from Chorus |
| `pychorus.count()` | None | Returns the number of songs hosted on Chorus |

# Song object
`pychorus.Song` contains all information about the chart.<br>
`pychours.Song.download()` downloads that chart from Google Drive to the current directory (as a zip, rar, 7z, etc).<br><br>
`pychours.Song.download()` can take `name` parameter, changing the name of the archive file.<br>

# Some examples
```python
import pychorus

# Get the top result for songs with the name "Raining Blood" and with artist name "Slayer"
song = pychorus.search(name = "Raining Blood", artist = "Slayer")[0]

# The output archive file will be named "Slayer - Raining Blood.zip"
song.download(name = "Slayer - Raining Blood")


songs = pychorus.search(charter = "ExileLord")
print(songs) # Prints top results for charts by ExileLord
```

# Why did I make this module?
I find navigating the website a little clunky, and downloading from the Google Drive is a slow pain with the "preparing" and "zipping" that Google does behind the scenes when downloading. This module downloads much, much faster than using a browser. And also, I'm just a hobbyist and thought it'd be fun to make a module for my favorite rhythm game :)

# Wrapping up
You can use this module for any project you please.

If you get any issues please report them to the issues page and I'll try to fix them right away.
