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
Show each chart from a search individually and ask to download that chart:
```python
import pychorus

song_name = input("What song do you want to search for? : ")
page_num = 0

while (True):
    try:
        songs = pychorus.search(name = song_name, page = page_num)
        
    except pychorus.PageNotFoundError:
        break
    
    for song in songs:
        print(song.info())
        prompt = input("Do you want to download this song? [y/n] : ")
        
        if (prompt == "y"):
            song.download()
    
    page_num += 1
```

Get the names of charters for a song:
```python
import pychorus

songs = pychorus.search(name = "Miserlou")

for song in songs:
    print(song.author)
```
