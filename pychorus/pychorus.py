import requests
import json
import os
import shutil
import pprint

# Gdown functions:
import re
import warnings

from six.moves import urllib_parse


def parse_url(url, warning=True):
    """Parse URLs especially for Google Drive links.

    file_id: ID of file on Google Drive.
    is_download_link: Flag if it is download link of Google Drive.
    """
    parsed = urllib_parse.urlparse(url)
    query = urllib_parse.parse_qs(parsed.query)
    is_gdrive = parsed.hostname == "drive.google.com"
    is_download_link = parsed.path.endswith("/uc")

    file_id = None
    if is_gdrive and "id" in query:
        file_ids = query["id"]
        if len(file_ids) == 1:
            file_id = file_ids[0]
    match = re.match(r"^/file/d/(.*?)/view$", parsed.path)
    if match:
        file_id = match.groups()[0]

    if is_gdrive and not is_download_link:
        warnings.warn(
            "You specified Google Drive Link but it is not the correct link "
            "to download the file. Maybe you should try: {url}".format(
                url="https://drive.google.com/uc?id={}".format(file_id)
            )
        )

    return file_id, is_download_link


import json
import os
import os.path as osp
import re
import shutil
import sys
import tempfile
import textwrap
import time

import requests
import six
import tqdm


CHUNK_SIZE = 512 * 1024  # 512KB
home = osp.expanduser("~")


if hasattr(textwrap, "indent"):
    indent_func = textwrap.indent
else:

    def indent_func(text, prefix):
        def prefixed_lines():
            for line in text.splitlines(True):
                yield (prefix + line if line.strip() else line)

        return "".join(prefixed_lines())


def get_url_from_gdrive_confirmation(contents):
    url = ""
    for line in contents.splitlines():
        m = re.search(r'href="(\/uc\?export=download[^"]+)', line)
        if m:
            url = "https://docs.google.com" + m.groups()[0]
            url = url.replace("&amp;", "&")
            return url
        m = re.search("confirm=([^;&]+)", line)
        if m:
            confirm = m.groups()[0]
            url = re.sub(
                r"confirm=([^;&]+)", r"confirm={}".format(confirm), url
            )
            return url
        m = re.search('"downloadUrl":"([^"]+)', line)
        if m:
            url = m.groups()[0]
            url = url.replace("\\u003d", "=")
            url = url.replace("\\u0026", "&")
            return url
        m = re.search('<p class="uc-error-subcaption">(.*)</p>', line)
        if m:
            error = m.groups()[0]
            raise RuntimeError(error)


def gdown_download(
    url, output=None, quiet=False, proxy=None, speed=None, use_cookies=True
):
    """Download file from URL.

    Parameters
    ----------
    url: str
        URL. Google Drive URL is also supported.
    output: str, optional
        Output filename. Default is basename of URL.
    quiet: bool
        Suppress terminal output. Default is False.
    proxy: str
        Proxy.
    speed: float
        Download byte size per second (e.g., 256KB/s = 256 * 1024).
    use_cookies: bool
        Flag to use cookies. Default is True.

    Returns
    -------
    output: str
        Output filename.
    """
    url_origin = url
    sess = requests.session()

    # Load cookies
    cache_dir = osp.join(home, ".cache", "gdown")
    if not osp.exists(cache_dir):
        os.makedirs(cache_dir)
    cookies_file = osp.join(cache_dir, "cookies.json")
    if osp.exists(cookies_file) and use_cookies:
        with open(cookies_file) as f:
            cookies = json.load(f)
        for k, v in cookies:
            sess.cookies[k] = v

    if proxy is not None:
        sess.proxies = {"http": proxy, "https": proxy}
        print("Using proxy:", proxy, file=sys.stderr)

    file_id, is_download_link = parse_url(url)

    while True:

        try:
            res = sess.get(url, stream=True)
        except requests.exceptions.ProxyError as e:
            print("An error has occurred using proxy:", proxy, file=sys.stderr)
            print(e, file=sys.stderr)
            return

        # Save cookies
        with open(cookies_file, "w") as f:
            cookies = [
                (k, v)
                for k, v in sess.cookies.items()
                if not k.startswith("download_warning_")
            ]
            json.dump(cookies, f, indent=2)

        if "Content-Disposition" in res.headers:
            # This is the file
            break
        if not (file_id and is_download_link):
            break

        # Need to redirect with confirmation
        try:
            url = get_url_from_gdrive_confirmation(res.text)
        except RuntimeError as e:
            print("Access denied with the following error:")
            error = "\n".join(textwrap.wrap(str(e)))
            error = indent_func(error, "\t")
            print("\n", error, "\n", file=sys.stderr)
            print(
                "You may still be able to access the file from the browser:",
                file=sys.stderr,
            )
            print("\n\t", url_origin, "\n", file=sys.stderr)
            return

        if url is None:
            print("Permission denied:", url_origin, file=sys.stderr)
            print(
                "Maybe you need to change permission over "
                "'Anyone with the link'?",
                file=sys.stderr,
            )
            return

    if file_id and is_download_link:
        m = re.search('filename="(.*)"', res.headers["Content-Disposition"])
        filename_from_url = m.groups()[0]
    else:
        filename_from_url = osp.basename(url)

    if output is None:
        output = filename_from_url

    output_is_path = isinstance(output, six.string_types)
    if output_is_path and output.endswith(osp.sep):
        if not osp.exists(output):
            os.makedirs(output)
        output = osp.join(output, filename_from_url)

    if not quiet:
        print("Downloading...", file=sys.stderr)
        print("From:", url_origin, file=sys.stderr)
        print(
            "To:",
            osp.abspath(output) if output_is_path else output,
            file=sys.stderr,
        )

    if output_is_path:
        tmp_file = tempfile.mktemp(
            suffix=tempfile.template,
            prefix=osp.basename(output),
            dir=osp.dirname(output),
        )
        f = open(tmp_file, "wb")
    else:
        tmp_file = None
        f = output

    try:
        total = res.headers.get("Content-Length")
        if total is not None:
            total = int(total)
        if not quiet:
            pbar = tqdm.tqdm(total=total, unit="B", unit_scale=True)
        t_start = time.time()
        for chunk in res.iter_content(chunk_size=CHUNK_SIZE):
            f.write(chunk)
            if not quiet:
                pbar.update(len(chunk))
            if speed is not None:
                elapsed_time_expected = 1.0 * pbar.n / speed
                elapsed_time = time.time() - t_start
                if elapsed_time < elapsed_time_expected:
                    time.sleep(elapsed_time_expected - elapsed_time)
        if not quiet:
            pbar.close()
        if tmp_file:
            f.close()
            shutil.move(tmp_file, output)
    except IOError as e:
        print(e, file=sys.stderr)
        return
    finally:
        sess.close()
        try:
            if tmp_file:
                os.remove(tmp_file)
        except OSError:
            pass

    return output

def get_archive_name(
    url, output=None, quiet=False, proxy=None, speed=None, use_cookies=True
):
    """Download file from URL.

    Parameters
    ----------
    url: str
        URL. Google Drive URL is also supported.
    output: str, optional
        Output filename. Default is basename of URL.
    quiet: bool
        Suppress terminal output. Default is False.
    proxy: str
        Proxy.
    speed: float
        Download byte size per second (e.g., 256KB/s = 256 * 1024).
    use_cookies: bool
        Flag to use cookies. Default is True.

    Returns
    -------
    output: str
        Output filename.
    """
    url_origin = url
    sess = requests.session()

    # Load cookies
    cache_dir = osp.join(home, ".cache", "gdown")
    if not osp.exists(cache_dir):
        os.makedirs(cache_dir)
    cookies_file = osp.join(cache_dir, "cookies.json")
    if osp.exists(cookies_file) and use_cookies:
        with open(cookies_file) as f:
            cookies = json.load(f)
        for k, v in cookies:
            sess.cookies[k] = v

    if proxy is not None:
        sess.proxies = {"http": proxy, "https": proxy}
        print("Using proxy:", proxy, file=sys.stderr)

    file_id, is_download_link = parse_url(url)

    while True:

        try:
            res = sess.get(url, stream=True)
        except requests.exceptions.ProxyError as e:
            print("An error has occurred using proxy:", proxy, file=sys.stderr)
            print(e, file=sys.stderr)
            return

        # Save cookies
        with open(cookies_file, "w") as f:
            cookies = [
                (k, v)
                for k, v in sess.cookies.items()
                if not k.startswith("download_warning_")
            ]
            json.dump(cookies, f, indent=2)

        if "Content-Disposition" in res.headers:
            # This is the file
            break
        if not (file_id and is_download_link):
            break

        # Need to redirect with confirmation
        try:
            url = get_url_from_gdrive_confirmation(res.text)
        except RuntimeError as e:
            print("Access denied with the following error:")
            error = "\n".join(textwrap.wrap(str(e)))
            error = indent_func(error, "\t")
            print("\n", error, "\n", file=sys.stderr)
            print(
                "You may still be able to access the file from the browser:",
                file=sys.stderr,
            )
            print("\n\t", url_origin, "\n", file=sys.stderr)
            return

        if url is None:
            print("Permission denied:", url_origin, file=sys.stderr)
            print(
                "Maybe you need to change permission over "
                "'Anyone with the link'?",
                file=sys.stderr,
            )
            return

    if file_id and is_download_link:
        m = re.search('filename="(.*)"', res.headers["Content-Disposition"])
        filename_from_url = m.groups()[0]
    else:
        filename_from_url = osp.basename(url)

    if output is None:
        output = filename_from_url

    output_is_path = isinstance(output, six.string_types)
    if output_is_path and output.endswith(osp.sep):
        if not osp.exists(output):
            os.makedirs(output)
        output = osp.join(output, filename_from_url)

    return output

#####

def remove_bad_path_chars(string):
    return string.replace(":", "").replace("<", "").replace(">", "").replace("*", "").replace("\"", "").replace("|", "").replace("/", "").replace("?", "").replace(".", "")

class PageNotFoundError(Exception):
    pass

class SongNotFoundError(Exception):
    pass

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
            output_filename_ext = os.path.splitext(get_archive_name(self.directLinks["archive"]))[1]
            filename = gdown_download(self.directLinks["archive"], output = remove_bad_path_chars(self.name) + output_filename_ext, quiet = True)
            print(f"poop: {filename}")
            return filename
        
        else:
            # Yes i know this is badly coded
            files = []

            base_dir = os.getcwd()
            print(remove_bad_path_chars(self.name))
            folder_dir1 = f"{base_dir}\\{remove_bad_path_chars(self.name)}"
            folder_dir2 = f"{base_dir}\\{remove_bad_path_chars(self.name)}\\{remove_bad_path_chars(self.name)}"
            
            try: # remove folder if it already exists
                shutil.rmtree(folder_dir1)

            except FileNotFoundError:
                pass
            
            os.mkdir(remove_bad_path_chars(self.name))
            os.chdir(remove_bad_path_chars(self.name))
            os.mkdir(remove_bad_path_chars(self.name))
            os.chdir(remove_bad_path_chars(self.name))
            
            for directLink in self.directLinks:
                filename = gdown_download(self.directLinks[directLink], quiet = True)
                files.append(filename)

            
            os.chdir(base_dir)
            shutil.make_archive(remove_bad_path_chars(self.name) if name == None else name, "zip", folder_dir1)

            shutil.rmtree(folder_dir1)
            return remove_bad_path_chars(self.name) + ".zip"
        
def search(generic = "", page = None, **kwargs):
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

    offset = page

    if (generic):
        url += generic

    elif (kwargs):
        for kw in kwargs:
            url += kw + "=" + '"' + kwargs[kw] + '" ' # adding the keyword and keyword value to the URL
            
    else:
        raise Exception("pychorus.search() expects atleast one argument")

    if (offset != None):
        url += f"&from={offset * 20}"

    request = requests.get(url)
    
    for song in request.json()["songs"]:
        songs.append(Song(song))

    if (len(songs) == 0):
        if (offset == None):
            raise SongNotFoundError(f'No charts for the song "{kwargs["name"]}" exist.')
        
        raise PageNotFoundError(f"Page {offset} does not exist for the given query.")
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

