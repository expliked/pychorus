import requests
import json
import gdown
import os
import shutil
import pprint

class Song(object):
    """
    A song object

    Contains all info of a song, including name, artist, genre, etc.

    Methods:
        Song.download():
            Downloads the song (as a zip, rar, 7z, etc.) to the current directory.
    """
    
    def __init__(self, my_dict): 
        for key in my_dict: 
            setattr(self, key, my_dict[key])
            
    def info(self):
        """
        Returns basic info about the song such as name and artist.
        """
        
        return f'''
"Song": {{
    "id": {self.id},
    "name": "{self.name}",
    "artist": "{self.artist}",
    "album": "{self.album}",
    "genre": "{self.genre}",
    "year": "{self.year}",
    "charter": "{self.charter}",
    "link": "{self.link}"
}}'''

    def all_info(self):
        """
        Returns ALL info about the song.
        """
        
        return pprint.pformat(self.__dict__, indent = 4)
    
    def download(self, name = None):
        """
        Downloads the song (as a zip, rar, 7z, etc.) to the current directory.

        Parameters:
            (optional) name:
                sets the name of the archive file that will be downloaded.
        """
        
        if (len(self.directLinks) == 1 and "archive" in self.directLinks):
            gdown.download(self.directLinks["archive"], quiet = True)
            
        else:
            # Yes i know this is badly coded
            files = []

            base_dir = os.getcwd()
            folder_dir1 = f"{base_dir}\\{self.name}"
            folder_dir2 = f"{base_dir}\\{self.name}\\{self.name}"
            
            try: # remove folder if it already exists
                shutil.rmtree(folder_dir1)

            except FileNotFoundError:
                pass
            
            os.mkdir(self.name)
            os.chdir(self.name)
            os.mkdir(self.name)
            os.chdir(self.name)
            
            for directLink in self.directLinks:
                filename = gdown.download(self.directLinks[directLink], quiet = True)
                files.append(filename)

            
            os.chdir(base_dir)
            shutil.make_archive(self.name if name == None else name, "zip", folder_dir1)

            shutil.rmtree(folder_dir1)

def search(generic = "", **kwargs):
    """
    Searches chorus.fightthe.pw for songs.

    You can use the following parameters for a more focused search:
        name (str)
        artist (str)
        album (str)
        genre (str)
        year (str)
        charter (str)
        
    Or, you can just provide a generic string and it will search from that.
    If the generic string exists in the arguments, the function will ignore all keyworded arguments.

    Using the page argument, you can get the next page of 10 songs.

    Returns the top 10 results from the search as pychorus.Song objects.
    """
    
    url = r'https://chorus.fightthe.pw/api/search?query='
    songs = []

    offset = kwargs["page"] if "page" in kwargs else None
    del kwargs["page"]
    
    if (generic):
        url += generic

    elif (kwargs):
        for kw in kwargs:
            url += kw + "=" + '"' + kwargs[kw] + '" ' # adding the keyword and keyword value to the URL

        if (offset != None):
            url += f"&from={offset * 10}"
            
    else:
        raise Exception("pychorus.search() expects atleast one argument")

    request = requests.get(url)
    
    for song in request.json()["songs"]:
        songs.append(Song(song))

    if (len(songs) == 0):
        raise Exception(f"Page {offset} does not exist for the given query.")
    
    return songs

def latest():
    """
    Returns the 20 latest songs added to chorus.fightthe.pw as pychorus.Song objects.
    """
    
    songs = []

    for song in requests.get(r'https://chorus.fightthe.pw/api/latest').json()["songs"]:
        songs.append(Song(song))

    return songs

def random():
    """
    Returns 20 random songs from chorus.fightthe.pw as pychorus.Song objects.
    """
    
    songs = []

    for song in requests.get(r'https://chorus.fightthe.pw/api/random').json()["songs"]:
        songs.append(Song(song))

    return songs

def count():
    """
    Returns the number of songs on chorus.fightthe.pw
    """
    
    return requests.get(r'https://chorus.fightthe.pw/api/count')

