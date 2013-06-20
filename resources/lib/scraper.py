#!/usr/bin/python
# -*- coding: UTF-8 -*-
#
## Scraper module

from unicodedata import normalize
from urllib import quote_plus
import StringIO
import gzip
import os
import re
import urllib2
import xbmc
import xbmcgui
import xbmcvfs

# needs to be global as song and prefetched_song are two instances
artist_aliases = dict()


class InvalidLyrics(Exception):
    pass


class Scraper(object):
    """
        Scrapes lyrics from internet sites using JSON based scrapers.
    """

    def __init__(self, *args, **kwargs):
        # get scraper info
        self._get_scraper_info()
        # get artist aliases, only need to grab it once
        if (not self.prefetch):
            self._alias_file()
        # set regex's
        self.__set_regex()

    def fetch_lyrics(self, songlist):
        # log message
        xbmc.log(u"Scraper::fetch_lyrics             (artist={artist!r}, title={title!r}, prefetch={prefetch!r}, songlist={songlist!r})".format(artist=self.m_song.artist, title=self.m_song.title, prefetch=self.prefetch, songlist=songlist), xbmc.LOGDEBUG)
        # variable to hold a new artist alias
        self.new_alias = dict()
        # variable to hold successful return of song list
        self.skip_alias = list()
        # fetch lyrics
        self.m_song.lyrics, self.m_song.message, self.m_song.website, self.m_song.status = self._fetch_lyrics_from_internet(self.m_song.artist, self.m_song.title, songlist)

    def __set_regex(self):
        # regex's
        self.regex_song_clean = re.compile("[\[\(]+.+?[\]\)]+")  # FIXME: do we really want to strip inside ()? (mixed results)
        self.regex_song_format_titlecase = re.compile("(?P<word1>[a-zA-Z'])(?P<word2>[A-Z\(\[])")
        self.regex_lyrics_format_breaks = re.compile("<br[ ]*[/]*>[\s]*", re.IGNORECASE)
        self.regex_lyrics_clean_lrc = re.compile("(^\[[0-9]+:[^\]]+\]\s)*(\[(ti|ar|al|re|ve|we):[^\]]+\]\s)*(\[[0-9]+:[^\]]+\]$)*")
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
                return self._fetch_lyrics_from_internet(self.new_alias[self.m_song.artist], title)
        # we failed all trys
        return self.m_addon.getLocalizedString(30851).format(msg=message), self.m_addon.getLocalizedString(30851).format(msg=message), "", False

    def _fetch_lyrics(self, artist, title="", scraper=0):
        try:
            # log message
            xbmc.log(u"  {heading} Scraper::_fetch_lyrics       (scraper={scraper!r})".format(heading=["{count}.".format(count=scraper + 1), "  "][artist.startswith("http://")], scraper=self.SCRAPERS[scraper]["title"]), xbmc.LOGDEBUG)
            # format url based on scraper if artist is not a url
            url = self._format_url(artist, title, scraper)
            # fetch source
            source = self._fetch_source(url, self.SCRAPERS[scraper]["url"]["useragent"]["string"], self.SCRAPERS[scraper]["source"]["encoding"], self.SCRAPERS[scraper]["source"]["compress"])
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
            return lyrics, self.m_addon.getLocalizedString(30860), self.SCRAPERS[scraper]["title"], True

    def _scrape_lyrics(self, source, scraper):
        # scrape lyrics
        lyrics = self.SCRAPERS[scraper]["source"]["lyrics"]["regex"].search(source).group(1)
        # sometimes the lyrics are not human readable or poorly formatted
        lyrics = self.regex_lyrics_format_breaks.sub("\n", lyrics).strip()
        lyrics = self.regex_lyrics_normalize.sub(lambda m: unichr(int(m.group(1))), lyrics).encode("UTF-8", "replace").decode("UTF-8")
        lyrics = u"\n".join([lyric.strip() for lyric in lyrics.splitlines()])
        # clean lyrics
        if (self.SCRAPERS[scraper]["source"]["lyrics"]["clean"] is not None):
            lyrics = self.SCRAPERS[scraper]["source"]["lyrics"]["clean"].sub("", lyrics).strip()
        # clean first and last blank lines for LRC lyrics
        if (self.SCRAPERS[scraper]["source"]["lyrics"]["lrc"]):
            lyrics = self.regex_lyrics_clean_lrc.sub("", lyrics).strip()
        # are these valid lyrics
        if (self.SCRAPERS[scraper]["source"]["lyrics"]["invalid"] is not None and self.SCRAPERS[scraper]["source"]["lyrics"]["invalid"].search(lyrics) is not None):
            raise InvalidLyrics(u"Invalid Lyrics! {lyrics}".format(lyrics=self.SCRAPERS[scraper]["source"]["lyrics"]["invalid"].search(lyrics).group(1)))
        # log message
        xbmc.log(u"     Scraper::_scrape_lyrics      (scraper={scraper!r}, Lyrics=Found!)".format(scraper=self.SCRAPERS[scraper]["title"]), xbmc.LOGDEBUG)

        return lyrics

    def _fetch_song_list(self, artist, scraper=0, usetitle=False):
        try:
            # log message
            xbmc.log(u"  {count}. Scraper::_fetch_song_list    (scraper={scraper!r}, autoselect={auto!r})".format(count=scraper + 1, scraper=self.SCRAPERS[scraper]["title"], auto=self.SCRAPERS[scraper]["source"]["songlist"]["autoselect"]), xbmc.LOGDEBUG)
            # do we want to include title
            title = ["", self.m_song.title][usetitle]
            # format url based on scraper
            url = self._format_url(artist, title, scraper)
            # fetch source
            source = self._fetch_source(url, self.SCRAPERS[scraper]["url"]["useragent"]["string"], self.SCRAPERS[scraper]["source"]["encoding"], self.SCRAPERS[scraper]["source"]["compress"])
            # scrape song list
            songs = self.SCRAPERS[scraper]["source"]["songlist"]["regex"].findall(source)
            # raise an error if no songs found
            if (not len(songs)): raise
            # get user selection
            url = self._get_song_selection(songs, self.SCRAPERS[scraper]["title"], self.SCRAPERS[scraper]["source"]["songlist"]["format"], self.SCRAPERS[scraper]["source"]["songlist"]["autoselect"], not usetitle)
            # add scraper to our skip alias list FIXME: we need a place that doesn't affect songlist always scrapers
            if (not usetitle):
                self.skip_alias += [scraper]
            # if selection, format url
            if (url is not None):
                url = u"{address}{head}{url}".format(address=self.SCRAPERS[scraper]["url"]["address"], head=self.SCRAPERS[scraper]["url"]["song"]["title"]["head"], url=url)
        # an error occurred, should only happen if artist was not found
        except Exception as error:
            # no artist found
            return None, str(error)
        else:
            # success
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
                key = " - ".join([self.m_song.title, self.new_alias.get(self.m_song.artist, self.artist_aliases.get(self.m_song.artist, self.m_song.artist))]).lower()
            else:
                key = self.m_song.title.lower()
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
        choice = xbmcgui.Dialog().select(u"{title} ({new})".format(title=self.m_song.title, new=title), titles, autoclose)
        # return selection
        if (choice >= 0):
            return dupes[titles[choice]]
        # log message only if no selection
        xbmc.log("     Scraper::_get_song_selection (message='No selection made')", xbmc.LOGDEBUG)
        # no selection return None
        return None

    def _sort_songs(self, songs, format_):
        """ Returns a sorted list with duplicates removed """
        # loop thru eliminating duplicates
        if (format_.startswith("Url | Title")):
            dupes = dict([[" - ".join(song[1 :]), song[0]] for song in songs])
        else:
            dupes = dict([[" - ".join(song[0 :-1]), song[-1]] for song in songs])
        # we want the keys, this holds song title
        titles = dupes.keys()
        # sort list
        titles.sort()

        return titles, dupes

    def _get_artist_alias(self, artist):
        # initialize alias
        alias = dict()
        # set the time to auto close in msec, 80% of time remaining is plenty of time and gives prefetch some time
        autoclose = int((xbmc.Player().getTotalTime() - xbmc.Player().getTime()) * 1000 * 0.80)
        # get keyboard object
        keyboard = xbmc.Keyboard(artist, self.m_addon.getLocalizedString(30810).format(artist=self.m_song.artist))
        # show keyboard
        keyboard.doModal(autoclose)
        # set new alias from user input
        if (keyboard.isConfirmed()):
            alias = {self.m_song.artist: unicode(keyboard.getText(), "UTF-8")}
        # log message
        xbmc.log(u"     Scraper::_get_artist_alias   (artist={artist!r}, new={alias!r})".format(artist=self.m_song.artist, alias=alias.get(self.m_song.artist, None)), xbmc.LOGDEBUG)

        return alias

    def _format_url(self, artist, title, scraper):
        # if we already have a url return it
        if (artist.startswith("http://")): return artist
        # log message
        xbmc.log(u"     Scraper::_format_url         (artist={artist!r}, alias={alias!r}, title={title!r})".format(artist=artist, alias=self.artist_aliases.get(artist, self.new_alias.get(self.m_song.artist, None)), title=title), xbmc.LOGDEBUG)
        # get alias if there is one
        artist = self.artist_aliases.get(artist, self.new_alias.get(self.m_song.artist, artist))
        # format artist, we now format artist aliases also
        artist = self._format_item(artist, scraper)
        # set head and format title if title exists
        if (title):
            title = u"{title}{tail}".format(title=self._format_item(title, scraper), tail=self.SCRAPERS[scraper]["url"]["song"]["title"]["tail"])
            head = self.SCRAPERS[scraper]["url"]["song"]["title"]["head"]
        else:
            head = self.SCRAPERS[scraper]["url"]["song"]["artist"]["head"]
        # set any groupby options
        groupby = self._set_group_by(artist, title, scraper)
        # format artist
        artist = u"{artist}{tail}".format(artist=artist, tail=["", self.SCRAPERS[scraper]["url"]["song"]["artist"]["tail"]][title == ""])
        # join items together
        param = [artist, self.SCRAPERS[scraper]["url"]["song"]["join"].join([artist, title])][title != ""]

        # return formatted url
        return u"{url}{head}{search}{groupby}{param}".format(url=self.SCRAPERS[scraper]["url"]["address"], head=head, search=self.SCRAPERS[scraper]["url"]["song"]["search"], groupby=groupby, param=param)

    def _set_group_by(self, artist, title, scraper):
        # initialize group
        groupby = ""
        # group artist by numbers "Artist [0-9]", "Artist [first letter]", "Artist [0-9] | [first letter]"]
        if ("Artist [0-9]" in self.SCRAPERS[scraper]["url"]["song"]["groupby"] and artist[0].isdigit()):
            groupby = "0-9/"
        # group artist by letters FIXME: probably not necessary
        elif ("Artist [A-Z]" in self.SCRAPERS[scraper]["url"]["song"]["groupby"] and artist[0].isalpha()):
            groupby = self._case_text("A-Z/", scraper)
        # group artist by first letter
        elif (("Artist [first letter]" in self.SCRAPERS[scraper]["url"]["song"]["groupby"] or "Artist [0-9] | [first letter]" in self.SCRAPERS[scraper]["url"]["song"]["groupby"]) and artist[0].isalpha()):
            groupby = u"{letter}/".format(letter=artist[0])

        return groupby

    def _format_item(self, text, scraper):
        # escape any characters TODO: verify this is the right place to do this
        for escape_char in self.SCRAPERS[scraper]["url"]["song"]["escape"]:
            text = text.replace(escape_char, escape_char * 2)
        # clean text
        if (self.SCRAPERS[scraper]["url"]["song"]["clean"]):
            # strip anything inside () or []
            text = self.regex_song_clean.sub("", text).strip()
            # normalize text
            text = normalize("NFKD", text).encode("ascii", "replace")
            # remove bad characters
            text = "".join([char for char in text if char.isalnum() or char.isspace() or char == "/"])
        # case text
        text = self._case_text(text, scraper)
        # urlencode item
        if (self.SCRAPERS[scraper]["url"]["song"]["urlencode"]):
            text = quote_plus(text.encode("UTF-8"))
        # replace url characters with separator
        for char in " /":
            text = text.replace(char, self.SCRAPERS[scraper]["url"]["song"]["space"])

        return text

    def _case_text(self, text, scraper):
        # properly case text
        if (self.SCRAPERS[scraper]["url"]["song"]["case"] == "lower"):
            text = text.lower()
        elif (self.SCRAPERS[scraper]["url"]["song"]["case"] == "UPPER"):
            text = text.upper()
        elif (self.SCRAPERS[scraper]["url"]["song"]["case"] == "Title"):
            text = " ".join([[self.regex_song_format_titlecase.sub(lambda m: m.group(1) + m.group(2).lower(), word.title()).encode("UTF-8", "replace").decode("UTF-8") , word][word.isupper()] for word in text.split()])

        return text

    def _fetch_source(self, url, useragent, encoding="UTF-8", compress=""):
        # log message
        xbmc.log(u"     Scraper::_fetch_source       (url={url!r})".format(url=url), xbmc.LOGDEBUG)
        # add headers
        headers = {
            "User-Agent": useragent,
            "Accept": "text/html; charset={encoding}".format(encoding=["", encoding][encoding != self.m_addon.getLocalizedString(30992)]),
            "Accept-Encoding": ["", compress][compress != self.m_addon.getLocalizedString(30991) and compress != "None"]
        }
        # request url
        request = urllib2.Request(url, headers=headers)
        # get response
        response = urllib2.urlopen(request)
        # read source
        source = response.read()
        # if gzipped, we need to unzip the source
        if (response.info().getheader("Content-Encoding") == "gzip"):
            source = gzip.GzipFile(fileobj=StringIO.StringIO(source)).read()
        # simple check for UTF-8 FIXME: verify this works correctly, "Ã" seems to be right, but "â" may not be right â€™
        if (source.find("Ã") >= 0 or source.find("â") >= 0):
            encoding = "UTF-8"

        return unicode(source, encoding, "replace")

    def _alias_file(self, alias=dict(), scraper=None):
        try:
            # needs to be global as song and prefetched_song are two instances
            global artist_aliases
            # create path to alias file
            _path = os.path.join(xbmc.translatePath(self.m_addon.getAddonInfo("Profile")).decode("UTF-8"), u"artist_aliases.txt")
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
        except IOError:
            # log message
            xbmc.log(u"Scraper::_alias_file              (message='Missing alias file!', path={path!r})".format(path=_path), xbmc.LOGDEBUG)
            # reset aliases
            artist_aliases = dict()

    def _get_scraper_info(self):
        # initialize our scrapers list
        self.SCRAPERS = list()
        # set scraper path
        _scraper_path = os.path.join(self.m_addon.getAddonInfo("Path"), "resources", "scrapers")
        # get list of available scrapers
        scraper_list = os.listdir(_scraper_path)
        # initialize our temp scraper list
        scrapers = list()
        # loop thru and add users preferred scrapers in proper order
        for c in range(1, 6):
            if (u"{scraper}.xpr".format(scraper=self.m_addon.getSetting("scraper_{order}".format(order=c))) not in scraper_list):
                break
            else:
                scrapers += [self.m_addon.getSetting("scraper_{order}".format(order=c))]
        # regex flags
        flags = {self.m_addon.getLocalizedString(30991): 0, "None": 0, "dotall": re.DOTALL, "ignorecase": re.IGNORECASE, "multiline": re.MULTILINE}
        # loop thru and set our info
        for scraper in scrapers:
            # set full path to file
            _path = os.path.join(_scraper_path, u"{scraper}.xpr".format(scraper=scraper))
            # skip any malformed scrapers
            try:
                # eval scraper
                tmp_scraper = eval(unicode(xbmcvfs.File(_path, "r").read(), "UTF-8"))
                #tmp_scraper = eval(unicode(open(_path, "r").read(), "UTF-8"))
                # lyrics regex
                tmp_scraper["scraper"]["source"]["lyrics"]["regex"] = re.compile(tmp_scraper["scraper"]["source"]["lyrics"]["regex"]["exp"], sum([flags[flag] for flag in tmp_scraper["scraper"]["source"]["lyrics"]["regex"]["flags"].split(" | ")]))
                # invalid regex
                if (tmp_scraper["scraper"]["source"]["lyrics"]["invalid"]["exp"]):
                    tmp_scraper["scraper"]["source"]["lyrics"]["invalid"] = re.compile(tmp_scraper["scraper"]["source"]["lyrics"]["invalid"]["exp"], sum([flags[flag] for flag in tmp_scraper["scraper"]["source"]["lyrics"]["invalid"]["flags"].split(" | ")]))
                else:
                    tmp_scraper["scraper"]["source"]["lyrics"]["invalid"] = None
                # clean regex
                if (tmp_scraper["scraper"]["source"]["lyrics"]["clean"]["exp"]):
                    tmp_scraper["scraper"]["source"]["lyrics"]["clean"] = re.compile(tmp_scraper["scraper"]["source"]["lyrics"]["clean"]["exp"], sum([flags[flag] for flag in tmp_scraper["scraper"]["source"]["lyrics"]["clean"]["flags"].split(" | ")]))
                else:
                    tmp_scraper["scraper"]["source"]["lyrics"]["clean"] = None
                # song list regex
                tmp_scraper["scraper"]["source"]["songlist"]["regex"] = re.compile(tmp_scraper["scraper"]["source"]["songlist"]["regex"]["exp"], sum([flags[flag] for flag in tmp_scraper["scraper"]["source"]["songlist"]["regex"]["flags"].split(" | ")]))
                # invalid regex
                if (tmp_scraper["scraper"]["source"]["songlist"]["invalid"]["exp"]):
                    tmp_scraper["scraper"]["source"]["songlist"]["invalid"] = re.compile(tmp_scraper["scraper"]["source"]["songlist"]["invalid"]["exp"], sum([flags[flag] for flag in tmp_scraper["scraper"]["source"]["songlist"]["invalid"]["flags"].split(" | ")]))
                else:
                    tmp_scraper["scraper"]["source"]["songlist"]["invalid"] = None
            except (IOError, AttributeError) as error:
                # an invalid scraper file, skip it, but log it
                xbmc.log(u"Invalid scraper file! - {scraper!r} ({error})".format(scraper=scraper, error=str(error)), xbmc.LOGERROR)
            else:
                # valid scraper file, add it
                self.SCRAPERS.append(tmp_scraper["scraper"])
