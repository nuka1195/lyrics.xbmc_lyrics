## Scraper module
# -*- coding: UTF-8 -*-

from unicodedata import normalize
from urllib import quote_plus
import StringIO
import gzip
import os
import re
import urllib2

try:
    import xbmc
    import xbmcgui
except:
    # get dummy xbmc modules (Debugging)
    from debug import *
    xbmc = XBMC()
    xbmcgui = XBMCGUI()


# needs to be global as song and prefetched_song are two instances
artist_aliases = dict()


class InvalidLyrics(Exception):
    pass

class Scraper:
    """
        Scrapes lyrics from internet sites using xml based scrapers.
    """

    def __init__(self, *args, **kwargs):
        # set our Addon class
        self.Addon = kwargs["addon"]
        # our we prefetching
        self.prefetch = kwargs["prefetch"]
        # get scraper info
        self._get_scraper_info()
        # get artist aliases, only need to grab it once
        if (not self.prefetch):
            self._alias_file()
        # set regex's
        self._set_regex()

    def fetch_lyrics(self, song, songlist):
        # log message
        xbmc.log("Scraper::fetch_lyrics             (artist={artist!r}, title={title!r}, prefetch={prefetch!r}, songlist={songlist!r})".format(artist=song.artist, title=song.title, prefetch=self.prefetch, songlist=songlist), xbmc.LOGNOTICE)
        # sometimes you don't have internet
        if (not xbmc.getCondVisibility("System.InternetState")):
            song.lyrics = self.Addon.getLocalizedString(30851).format(msg="No Internet connection!")
            song.message = self.Addon.getLocalizedString(30851).format(msg="No Internet connection!")
            song.status = False
            song.website = ""
            return
        # variable to hold a new artist alias
        self.new_alias = dict()
        # variable to hold successful return of song list
        self.skip_alias = list()
        # used for aliases and song selection
        self.artist = song.artist
        self.title = song.title
        # fetch lyrics
        song.lyrics, song.message, song.website, song.status = self._fetch_lyrics_from_internet(self.artist, self.title, songlist)

    def _set_regex(self):
        # regex's
        self.regex_song_clean = re.compile("[\[\(]+.+?[\]\)]+")# FIXME: do we really want to strip inside ()? (mixed results)
        self.regex_song_format_titlecase = re.compile("(?P<word1>[a-zA-Z'])(?P<word2>[A-Z\(\[])")
        self.regex_lyrics_clean = re.compile("<.+?>")
        self.regex_lyrics_clean_lrc = re.compile("(^\[[0-9]+:[^\]]+\]\s)*(\[(ti|ar|al|re|ve|we):[^\]]+\]\s)*(\[[0-9]+:[^\]]+\]$)*")
        self.regex_lyrics_format_breaks = re.compile("<br[ ]*[/]*>[\s]*", re.IGNORECASE)
        self.regex_lyrics_normalize = re.compile("&#[x]*(?P<name>[0-9]+);*")

    def _fetch_lyrics_from_internet(self, artist, title, songlist=False):
        # initialize our variables
        scraper = 0
        lyrics = None
        message = website = ""
        status = False
        # loop until we have success or run out of scrapers
        while not status and scraper < len(self.SCRAPERS):
            # skip artist alias if we got a song list, this works as it's not filled until we try song list
            if (scraper not in self.skip_alias):
                # get current scrapers artist aliases
                self.artist_aliases = artist_aliases.get(self.SCRAPERS[scraper]["title"], dict())
                # fetch list if scraper only returns a list first or we found no lyrics
                if (self.SCRAPERS[scraper]["source"]["songlist"]["always"] or songlist):
                    # initialize to None, so we don't try and fetch lyrics if we are prefetching and we get a song list
                    url = None
                    # do not interrupt user if prefetching
                    if ((not self.prefetch or self.SCRAPERS[scraper]["source"]["songlist"]["autoselect"])):
                        url, message = self._fetch_song_list(artist, scraper=scraper, usetitle=not songlist)
                else:
                    url = artist
                # fetch lyrics
                if (url is not None):
                    lyrics, message, website, status = self._fetch_lyrics(url, title, scraper=scraper)
            # increment scraper
            scraper += 1
        # if we succeeded or we are prefetching return results
        if (status or self.prefetch):
            return lyrics, message, website, status
        # we failed, try to fetch a songlist if we haven't already
        elif (not songlist):
            return self._fetch_lyrics_from_internet(artist, title, songlist=True)
        # no artist was found, so get an alias
        else:
            # get artist alias
            self.new_alias = self._get_artist_alias(artist)
            # if user entered alias, try all over again
            if (self.new_alias):
                return self._fetch_lyrics_from_internet(self.new_alias[self.artist], title)
        # we failed all trys
        return self.Addon.getLocalizedString(30851).format(msg=message), self.Addon.getLocalizedString(30851).format(msg=message), "", False

    def _fetch_lyrics(self, artist, title="", scraper=0):
        try:
            # log message
            xbmc.log("  {heading} Scraper::_fetch_lyrics       (scraper={scraper!r})".format(heading=["{count}.".format(count=scraper + 1), "  "][artist.startswith("http://")], scraper=self.SCRAPERS[scraper]["title"]), xbmc.LOGNOTICE)
            # format url based on scraper if artist is not a url
            url = self._format_url(artist, title, scraper)
            # fetch source
            source = self._fetch_source(url, self.SCRAPERS[scraper]["url"]["useragent"], self.SCRAPERS[scraper]["source"]["encoding"], self.SCRAPERS[scraper]["source"]["compress"])
            # scrape and clean lyrics
            lyrics = self._scrape_lyrics(source, scraper)
            # save alias if we have one
            if (self.new_alias):
                self._alias_file(alias=self.new_alias, scraper=self.SCRAPERS[scraper]["title"])
        except Exception as error:
            # failure return None
            return None, str(error), self.SCRAPERS[scraper]["title"], False
        else:
            # success return results
            return lyrics, self.Addon.getLocalizedString(30860), self.SCRAPERS[scraper]["title"], True

    def _scrape_lyrics(self, source, scraper):
        # scrape lyrics
        lyrics = self.SCRAPERS[scraper]["source"]["lyrics"]["regex"].search(source).group(1)
        # sometimes the lyrics are not human readable or poorly formatted
        if (self.SCRAPERS[scraper]["source"]["lyrics"]["clean"]):
            lyrics = self.regex_lyrics_format_breaks.sub("\n", lyrics).strip()
            lyrics = self.regex_lyrics_clean.sub("", lyrics).strip()
            lyrics = self.regex_lyrics_normalize.sub(lambda m: unichr(int(m.group(1))), lyrics).encode("UTF-8", "replace").decode("UTF-8")
            lyrics = u"\n".join([lyric.strip() for lyric in lyrics.splitlines()])
            # clean first and last blank lines for lrc lyrics
            if (self.SCRAPERS[scraper]["source"]["lyrics"]["type"] == "lrc"):
                lyrics = self.regex_lyrics_clean_lrc.sub("", lyrics).strip()
        # are these valid lyrics
        if (self.SCRAPERS[scraper]["source"]["lyrics"]["invalid"].search(lyrics) is not None):
            raise InvalidLyrics("Invalid Lyrics! {lyrics}".format(lyrics=self.SCRAPERS[scraper]["source"]["lyrics"]["invalid"].search(lyrics).group()))
        # log message
        xbmc.log("     Scraper::_scrape_lyrics      (scraper={scraper!r}, Lyrics=Found!)".format(scraper=self.SCRAPERS[scraper]["title"]), xbmc.LOGNOTICE)
        # return result
        return lyrics

    def _fetch_song_list(self, artist, scraper=0, usetitle=False):
        try:
            # log message
            xbmc.log("  {count}. Scraper::_fetch_song_list    (scraper={scraper!r}, autoselect={auto!r})".format(count=scraper + 1, scraper=self.SCRAPERS[scraper]["title"], auto=self.SCRAPERS[scraper]["source"]["songlist"]["autoselect"]), xbmc.LOGNOTICE)
            # do we want to include title
            title = ["", self.title][usetitle]
            # format url based on scraper
            url = self._format_url(artist, title, scraper)
            # fetch source
            source = self._fetch_source(url, self.SCRAPERS[scraper]["url"]["useragent"], self.SCRAPERS[scraper]["source"]["encoding"], self.SCRAPERS[scraper]["source"]["compress"])
            # scrape song list
            songs = self.SCRAPERS[scraper]["source"]["songlist"]["regex"].findall(source)
            # raise an error if no songs found
            if (not len(songs)): raise
            # get user selection
            url = self._get_song_selection(songs, self.SCRAPERS[scraper]["title"], self.SCRAPERS[scraper]["source"]["songlist"]["swap"], self.SCRAPERS[scraper]["source"]["songlist"]["autoselect"], not usetitle)
            # add scraper to our skip alias list FIXME: we need a place that doesn't affect songlist always scrapers
            if (not usetitle):
                self.skip_alias += [scraper]
            # if selection, format url
            if (url is not None):
                url = self.SCRAPERS[scraper]["url"]["address"] + self.SCRAPERS[scraper]["url"]["song"]["title"]["head"] + url
        # an error occurred, should only happen if artist was not found
        except Exception as error:
            # no artist found
            return None, str(error)
        else:
            # return result
            return url, ""

    def _get_song_selection(self, songs, title, swap, autoselect, songlist):
        """ Returns a user selected song's url from a list of supplied songs """
        # sort songs, removing duplicates
        titles, dupes = self._sort_songs(songs, swap)
        # if autoselect, try to find a match
        if (autoselect):
            # set key
            if (len(songs[0]) == 3):
                # we use an artist alias if one was entered
                key = " - ".join([self.title, self.new_alias.get(self.artist, self.artist_aliases.get(self.artist, self.artist))]).lower()
            else:
                key = self.title.lower()
            # loop thru and find a match FIXME: titles is sorted, so may not return best result?
            choice = [count for count, k in enumerate(titles) if (k.lower() == key)]
            # if we have a match return it
            if (choice):
                return dupes[titles[choice[0]]]
        # if we are prefetching or autoselecting when not songlist skip selection, we only go this far for autoselect scrapers
        if (self.prefetch or (autoselect and not songlist)):
            return None
        # set the time to auto close in msec, 80% of time remaining is plenty of time and gives prefetch some time
        autoclose = int((xbmc.Player().getTotalTime() - xbmc.Player().getTime()) * 1000 * 0.80)
        # get user selection
        choice = xbmcgui.Dialog().select("{title} ({new})".format(title=self.title, new=title), titles, autoclose)
        # return selection
        if (choice >= 0):
            return dupes[titles[choice]]
        # log message only if no selection
        xbmc.log("     Scraper::_get_song_selection (message='No selection made')", xbmc.LOGNOTICE)
        # no selection return None
        return None

    def _sort_songs(self, songs, swap):
        """ Returns a sorted list with duplicates removed """
        # loop thru eliminating duplicates
        if (swap):
            dupes = dict([[" - ".join(song[1 :]), song[0]] for song in songs])
        else:
            dupes = dict([[" - ".join(song[0 :-1]), song[-1]] for song in songs])
        # we want the keys, this holds song title
        titles = dupes.keys()
        # sort list
        titles.sort()
        # return list of songs
        return titles, dupes

    def _get_artist_alias(self, artist):
        # initialize alias
        alias = dict()
        # set the time to auto close in msec, 80% of time remaining is plenty of time and gives prefetch some time
        autoclose = int((xbmc.Player().getTotalTime() - xbmc.Player().getTime()) * 1000 * 0.80)
        # get keyboard object
        keyboard = xbmc.Keyboard(artist, self.Addon.getLocalizedString(30810).format(artist=self.artist))
        # show keyboard
        keyboard.doModal(autoclose)
        # set new alias from user input
        if (keyboard.isConfirmed()):
            alias = {self.artist: unicode(keyboard.getText(), "UTF-8")}
        # log message
        xbmc.log("     Scraper::_get_artist_alias   (artist={artist!r}, new={alias!r})".format(artist=self.artist, alias=alias.get(self.artist, None)), xbmc.LOGNOTICE)
        # return result
        return alias

    def _format_url(self, artist, title, scraper):
        # if we already have a url return it
        if (artist.startswith("http://")): return artist
        # log message
        xbmc.log("     Scraper::_format_url         (artist={artist!r}, alias={alias!r}, title={title!r})".format(artist=artist, alias=self.artist_aliases.get(artist, self.new_alias.get(self.artist, None)), title=title), xbmc.LOGNOTICE)
        # get alias if there is one
        artist = self.artist_aliases.get(artist, self.new_alias.get(self.artist, artist))
        # format artist, we now format artist aliases also
        artist = self._format_item(artist, scraper)
        # only need to format title if it exists
        if (title):
            title = self._format_item(title, scraper) + self.SCRAPERS[scraper]["url"]["song"]["title"]["tail"]
            head = self.SCRAPERS[scraper]["url"]["song"]["title"]["head"]
        # add artist tail if no title
        else:
            artist += self.SCRAPERS[scraper]["url"]["song"]["artist"]["tail"]
            head = self.SCRAPERS[scraper]["url"]["song"]["artist"]["head"].replace("$FIRST_LETTER", artist[0])
        # does the website subcategorize artists?
        if (self.SCRAPERS[scraper]["url"]["song"]["artist"]["group"] and title):
            # group numbers
            if ("0-9" in self.SCRAPERS[scraper]["url"]["song"]["artist"]["group"] and artist[0].isdigit()):
                sub = "0-9"
            # group letters FIXME: probably not necessary
            elif ("A-Z" in self.SCRAPERS[scraper]["url"]["song"]["artist"]["group"] and artist[0].isalpha()):
                sub = "A-Z"
            # group by first letter
            else:
                sub = artist[0]
            # join sub and artist
            artist = self.SCRAPERS[scraper]["url"]["song"]["join"].join([sub, artist])
        # join items together
        _search = [artist, self.SCRAPERS[scraper]["url"]["song"]["join"].join([artist, title])][title != ""]
        # return formatted url
        return self.SCRAPERS[scraper]["url"]["address"] + head + self.SCRAPERS[scraper]["url"]["song"]["search"] + _search

    def _format_item(self, text, scraper):
        # escape any characters TODO: verify this is the right place to do this
        for escape_char in self.SCRAPERS[scraper]["url"]["song"]["escape"]:
            text = text.replace(escape_char, escape_char + escape_char)
        # clean text
        if (self.SCRAPERS[scraper]["url"]["song"]["clean"]):
            # strip anything inside () or []
            text = self.regex_song_clean.sub("", text).strip()
            # normalize text
            text = normalize("NFKD", text).encode("ascii", "replace")
            # remove bad characters
            text = "".join([char for char in text if char.isalnum() or char.isspace() or char == "/"])
        # format text
        if (self.SCRAPERS[scraper]["url"]["song"]["case"] == "lower"):
            text = text.lower()
        elif (self.SCRAPERS[scraper]["url"]["song"]["case"] == "title"):
            text = " ".join([[self.regex_song_format_titlecase.sub(lambda m: m.group(1) + m.group(2).lower(), word.title()).encode("UTF-8", "replace").decode("UTF-8") , word][word.isupper()] for word in text.split()])
        # replace url characters with separator
        for char in " /":
            text = text.replace(char, self.SCRAPERS[scraper]["url"]["song"]["space"])
        # urlencode item
        if (self.SCRAPERS[scraper]["url"]["song"]["urlencode"]):
            text = quote_plus(text.encode("UTF-8"))
        # return result
        return text

    def _fetch_source(self, url, useragent, encoding="UTF-8", compress=""):
        # log message
        xbmc.log("     Scraper::_fetch_source       (url={url!r})".format(url=url), xbmc.LOGNOTICE)
        # add headers
        headers = {
            "User-Agent": useragent,
            "Accept": "text/html; charset={encoding}".format(encoding=encoding),
            "Accept-Encoding": compress
        }
        # request url
        request = urllib2.Request(url, headers=headers)
        # open requested url
        usock = urllib2.urlopen(request)
        # read source
        source = usock.read()
        # if gzipped, we need to unzip the source
        if (usock.info().getheader("Content-Encoding") == "gzip"):
            source = gzip.GzipFile(fileobj=StringIO.StringIO(source)).read()
        # close socket
        usock.close()
        # simple check for UTF-8 FIXME: verify this works correctly, "Ã" seems to be right, but "â" may not be right â€™
        if (source.find("Ã") >= 0 or source.find("â") >= 0):
            encoding = "UTF-8"
        # return a unicode object
        return unicode(source, encoding, "replace")

    def _alias_file(self, alias=dict(), scraper=None):
        try:
            # needs to be global as song and prefetched_song are two instances
            global artist_aliases
            # create path to alias file
            _path = os.path.join(xbmc.translatePath(self.Addon.getAddonInfo("Profile")).encode("UTF-8"), u"artist_aliases.txt")
            # read/write aliases file
            if (scraper is not None):
                # add key if necessary
                if (not artist_aliases.has_key(scraper)):
                    artist_aliases.update({scraper: dict()})
                # update aliases
                artist_aliases[scraper].update(alias)
                # save aliases
                open(_path, "w").write(repr(artist_aliases))
            else:
                # read aliases
                artist_aliases = eval(open(_path, "r").read())
        except:
            # log message
            xbmc.log("Scraper::_alias_file              (message='Missing or invalid alias file', path={path!r})".format(path=_path), xbmc.LOGNOTICE)
            # reset aliases
            artist_aliases = dict()

    def _get_scraper_info(self):
        # unescape "&amp;", "&lt;", "&gt;", &quot;" and "&apos;" in a string 
        def _unescape(text):
            # return unescaped text
            return text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", "\"").replace("&apos;", "'")
        # initialize our scrapers list
        self.SCRAPERS = list()
        # set scraper path
        _scraper_path = os.path.join(self.Addon.getAddonInfo("Path"), "resources", "scrapers")
        # get list of available scrapers
        scraper_list = os.listdir(_scraper_path)
        #scrapers = [f for f in os.listdir( _scraper_path ) if ( f != "None.xml" )]
        #scrapers = [self.Addon.getSetting(s) for s in ["scraper_{order}".format(order=c) for c in range(1, 11)] if (self.Addon.getSetting(s) != "None")]
        # initialize our scraper list
        scrapers = list()
        # loop thru and add users preferred scrapers in proper order
        for c in range(1, 6):
            if ("{scraper}.xml".format(scraper=self.Addon.getSetting("scraper_{order}".format(order=c))) not in scraper_list):
                break
            else:
                scrapers += [self.Addon.getSetting("scraper_{order}".format(order=c))]
        # scrapers regex
        regex_scraper = re.compile("<scraper.+?title=\"([^\"]+)\".*?>\s[^<]+<url.+?address=\"([^\"]+)\".*?useragent=\"([^\"]+)\".*?>\s[^<]+<song.*?join=\"([^\"]*)\".*?space=\"([^\"]*)\".*?escape=\"([^\"]*)\".*?clean=\"([^\"]*)\".*?case=\"([^\"]*)\".*?search=\"([^\"]*)\".*?urlencode=\"([^\"]*)\".*?>\s[^<]+<artist.+?group=\"([^\"]*)\".*?head=\"([^\"]*)\".*?tail=\"([^\"]*)\".*?/>\s[^<]+<title.+?head=\"([^\"]*)\".*?tail=\"([^\"]*)\".*?/>\s[^<]+</song>\s[^<]+</url>\s[^<]+<source.+?encoding=\"([^\"]*)\".+?compress=\"([^\"]*)\".*?>\s[^<]+<lyrics.+?type=\"([^\"]*)\".*?clean=\"([^\"]*)\".*?>\s[^<]+<regex.+?flags=\"([^\"]*)\".*?>([^<]+)</regex>\s[^<]+<invalid.+?flags=\"([^\"]*)\".*?>([^<]*)</invalid>\s[^<]+</lyrics>\s[^<]+<songlist.+?swap=\"([^\"]*)\".*?always=\"([^\"]*)\".*?select=\"([^\"]*)\".*?>\s[^<]+<regex.+?flags=\"([^\"]*)\".*?>([^<]+)</regex>\s[^<]+<invalid.+?flags=\"([^\"]*)\".*?>([^<]*)</invalid>\s[^<]+</songlist>", re.IGNORECASE)
        # regex flags
        flags = {"dotall": re.DOTALL, "ignorecase": re.IGNORECASE, "multiline": re.MULTILINE}
        # loop thru and set our info
        for scraper in scrapers:
            # set full path to file
            _path = os.path.join(_scraper_path, "{scraper}.xml".format(scraper=scraper))
            # skip any malformed scrapers
            try:
                # get scrapers xml source
                xmlSource = unicode(open(_path, "r").read(), "UTF-8")
                # get info
                info = regex_scraper.search(xmlSource).groups()
            # an invalid scraper file, skip it
            except Exception as error:
                # log error
                xbmc.log("Invalid scraper file! - {scraper!r} ({error})".format(scraper=scraper, error=error), xbmc.LOGERROR)
            # valid scraper file, add it
            else:
                # create scraper
                tmp_scraper = {
                    "title": info[0],
                    "url": {
                        "address": info[1],
                        "useragent": _unescape(info[2]),
                        "song": {
                            "join": info[3],
                            "space": info[4],
                            "escape": _unescape(info[5]),
                            "clean": info[6] == "true",
                            "case": info[7],
                            "search": _unescape(info[8]),
                            "urlencode": info[9] == "true",
                            "artist": {
                                "group": info[10],
                                "head": info[11],
                                "tail": info[12],
                            },
                            "title": {
                                "head": info[13],
                                "tail": info[14],
                            },
                        },
                    },
                    "source": {
                        "encoding": info[15],
                        "compress": info[16],
                        "lyrics": {
                            "type": info[17],
                            "clean": info[18] == "true",
                            "regex": re.compile(_unescape(info[20]), sum([flags[flag] for flag in info[19].split()])),
                            "invalid": re.compile(_unescape(info[22]), sum([flags[flag] for flag in info[21].split()])),
                        },
                        "songlist": {
                            "swap": info[23] == "true",
                            "always": info[24] == "true",
                            "autoselect": info[25] == "auto",
                            "regex": re.compile(_unescape(info[27]), sum([flags[flag] for flag in info[26].split()])),
                            "invalid": re.compile(_unescape(info[29]), sum([flags[flag] for flag in info[28].split()])),
                        },
                    },
                }
                # we want the primary scraper first
                if (scraper.replace(".xml", "") == self.Addon.getSetting("primary_scraper")):
                    self.SCRAPERS.insert(0, tmp_scraper)
                else:
                    self.SCRAPERS.append(tmp_scraper)


if (__name__ == "__main__"):
    TITLE = "LyrDb"

    scraper = eval(unicode(open("../scrapers/{title}.json".format(title=TITLE), "r").read(), "UTF-8"))
    print scraper
    print "--------------------"

    print repr(scraper["scraper"]["title"])
    print
    for key, value in scraper["scraper"]["url"].items():
        print "{key!r}: {value!r}".format(key=key, value=value)
    print "--------------------"
    songs = {
        0: (u"Wings", u"Live and let Die",),
        1: (u"The Guess Who", u"Proper Stranger",),
        2: (u"The Beatles", u"Back in the USSR",),
        3: (u"britney spears", u"(You Drive Me) Crazy",),
        4: (u".38 Special", u"Rockin' Into the Night",), #u"Wild-Eyed Southern Boys",), #
        5: (u"The babys", u"Isn't it time",),
        6: (u"4 Non Blondes", u"Dear Mr. President",),
        7: (u"ABBA", u"Gimme! Gimme! Gimme! (A Man After Midnight)",),
        8: (u"AC/DC", u"Have a Drink on Me",),
        9: (u"Blue Öyster Cult", u"Burning for you",),
        10: (u"The Rolling Stones (feat. Cheryl Crow)", u"Get off of my cloud",),
        11: (u".38 Special", u"Hold on Loosely",),
        12: (u"ABBA", u"Eagle",),
        13: (u"Enya", u"Aniron (I Desire)",),
        14: (u"Enya", u"Book of Days",),
        15: (u"*NSync", u"Bye Bye Bye",),
        16: (u"Enya", u"Orinoco Flow",),
        17: (u"ABBA", u"S.O.S.",),
        18: (u"Duffy", u"Warwick Avenue",),
        19: (u"Eminem", u"Not Afraid",),
        20: (u"Queen", u"I Want to Break Free",),
    }

    SONG_ID = 10

    #
    class SONG:
        artist, title = songs[SONG_ID]
    # grab our dummy song class
    _song = SONG()

    scraper = Scraper(addon=XBMCADDON().Addon("python.testing"), prefetch=True)
    scraper.fetch_lyrics(_song, False)
    # print result
    print
    print "Status for {title!r} by {artist!r}".format(title=_song.title, artist=_song.artist)
    print "site={website!r: <29}success={status!r: <10}messgae={msg!r}".format(website=_song.website, status=_song.status, msg=_song.message)
    if (_song.lyrics is not None):
        print
        print "Lyrics:"
        print "----------"
        for lyric in _song.lyrics.splitlines():
            print repr(lyric)
