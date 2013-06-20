#!/usr/bin/python
# -*- coding: UTF-8 -*-
#
## Lyrics module

from codecs import BOM_UTF8
from scraper import Scraper
import os
import re
import xbmc
import xbmcvfs

# needs to be global as song and prefetched_song are two instances
prefetched_lyrics = dict()


class Lyrics(Scraper):
    """Lyrics Class:

    Fetches, cleans and saves lyrics.

    """
    # infolabel constants
    # TODO: change to Player.* when/if XBMC supports Player.Offset
    INFOLABEL_LYRICS = "MusicPlayer.Offset({prefetch:d}).Lyrics"
    INFOLABEL_DURATION = "MusicPlayer.Offset({prefetch:d}).Duration"
    # lyrics header string
    LYRICS_INFO_HEADER = u"""[ti:{title}]
[ar:{artist}]
[al:{album}]
[re:{addon}]
[ve:{version}]
[we:{website}]
[offset:0]

{lyrics}"""

    def __init__(self, *args, **kwargs):
        # initialize our super classes
        Scraper.__init__(self)  #, prefetch=self.prefetch)
        # set regex's
        self.__set_regex()

    def __set_regex(self):
        # regex's
        self.regex_lyrics_clean_headers = re.compile("\[[a-z]+?:.*\]\s")
        self.regex_lyrics_lrc_split_timestamps = re.compile("\[([0-9]+):([0-9]+(?:\.[0-9]+)?)\](.*)")
        self.regex_lyrics_offset = re.compile("\[offset:([+-]*[0-9]+)\]")
        self.regex_lyrics_website = re.compile("\[we:(.+)\]")

    def get_lyrics(self, songlist):
        try:
            # needs to be global as song and prefetched_song are two instances
            global prefetched_lyrics
            # set key
            cachename = xbmc.getCacheThumbName(
                "".join([self.m_song.artist, self.m_song.album, self.m_song.title]))[:-4]
            # if prefetched lyrics are found set them
            if (prefetched_lyrics.has_key(cachename)):
                if (not self.prefetch):
                    # loop thru and set all attributes
                    for key, value in prefetched_lyrics[cachename].iteritems():
                        setattr(self.m_song, key, value)
                    # TODO: deleting them lose the prefetched song when skipping backwards
                    # delete prefetched lyrics as they should be cached now
                    del prefetched_lyrics[cachename]
                # prefetched lyrics are already cleaned
                return
            # if embedded lyrics are found set them
            elif (xbmc.getInfoLabel(self.INFOLABEL_LYRICS.format(prefetch=self.prefetch))):
                self.m_song.lyrics = unicode(xbmc.getInfoLabel(self.INFOLABEL_LYRICS.format(
                    prefetch=self.prefetch)), "UTF-8", "replace")
                self.m_song.message = self.m_addon.getLocalizedString(30861)
            # if cached lyrics are found set them
            else:
                # we work strictly with UTF-8, so strip BOM
                self.m_song.lyrics = unicode(xbmcvfs.File(
                    self.m_song.lyrics_path, "r").read().strip(BOM_UTF8), "UTF-8")
                # if no lyrics raise error
                if (not self.m_song.lyrics): raise IOError
                # set cached message
                self.m_song.message = self.m_addon.getLocalizedString(30862)
        except IOError:
            # no lyrics found, so fetch lyrics from internet
            self.fetch_lyrics(songlist)
            # if the search was successful save lyrics
            if (self.m_song.status):
                self.save_lyrics()

        # we need to clean lyrics in case they are LRC tagged
        self._clean_lyrics()
        # store lyrics only if prefetch, we only store for the fetched message.
        if (self.prefetch and self.m_song.status):
            prefetched_lyrics[cachename] = {
                "lrc_lyrics": self.m_song.lrc_lyrics,
                "lyrics": self.m_song.lyrics,
                "lyrics_tags": self.m_song.lyrics_tags,
                "message": self.m_song.message,
                "prefetched": self.prefetch,
                "status": self.m_song.status,
                "website": self.m_song.website,
            }

    def _clean_lyrics(self):
        # nothing to clean?
        # TODO: is "self.m_song.lyrics is None or " necessary
        if (self.m_song.lyrics is None or not self.m_song.status): return
        # default to lrc lyrics
        lrc_lyrics = True
        # get website
        if (self.m_song.website == ""):
            try:
                self.m_song.website = self.regex_lyrics_website.search(self.m_song.lyrics).group(1)
            except AttributeError:
                self.m_song.website = ""
        # eliminate info block
        self.m_song.lyrics = self.regex_lyrics_clean_headers.sub("", self.m_song.lyrics).strip()
        # separate lyrics and time stamps
        lyrics = self.regex_lyrics_lrc_split_timestamps.findall(self.m_song.lyrics)
        # auto tag lyrics if not tagged and user preference
        if (not lyrics and self.m_addon.getSetting("enable_karaoke_mode") and
                self.m_addon.getSetting("autoscroll_lyrics")):
            # split lines
            lines = self.m_song.lyrics.strip().splitlines()
            # get offset
            offset = self.m_addon.getSetting("autoscroll_lyrics_delay")
            # get total time
            total_time = int(xbmc.getInfoLabel(self.INFOLABEL_DURATION.format(
                prefetch=self.prefetch)).split(":")[0]) * 60 + int(xbmc.getInfoLabel(
                    self.INFOLABEL_DURATION.format(prefetch=self.prefetch)).split(":")[1]) - (offset * 2)
            # we set the same amount of time per lyric, what do you expect?
            lyric_time = float(total_time) / len(lines)
            # enumerate thru and set each tagged lyric
            lyrics = [divmod((count + 1) * lyric_time + offset, 60) + (lyric,)
                for count, lyric in enumerate(lines)]
            # these are non lrc lyrics
            lrc_lyrics = False
        # format lyrics
        if (lyrics):
            # set lyric type
            self.m_song.lrc_lyrics = lrc_lyrics
            # get any timestamp adjustment
            try:
                offset = float(self.regex_lyrics_offset.search(self.m_song.lyrics).group(1)) / 1000
            except AttributeError:
                offset = 0
            # reset lyrics
            self.m_song.lyrics = ""
            # loop thru and set our lyrics
            for lyric in lyrics:
                self.m_song.lyrics_tags.append(int(lyric[0]) * 60 + float(lyric[1]) + offset)
                self.m_song.lyrics += lyric[2].strip() + "\n"
            # we insert tag[0] time to skip blank line, then a tag for the title
            self.m_song.lyrics_tags.insert(0, self.m_song.lyrics_tags[0])
            self.m_song.lyrics_tags.insert(0, 0)
            # we add a title and a blank non lyric so the first lyric
            # isn't highlighted until it's time
            self.m_song.lyrics = u"[I] [{title}] [/I]\n\n{lyrics}".format(
                title=self.m_song.title, lyrics=self.m_song.lyrics)

    def save_lyrics(self):
        # format lyrics with song info header
        self.m_song.lyrics = self.LYRICS_INFO_HEADER.format(
            title=self.m_song.title,
            artist=self.m_song.artist,
            album=self.m_song.album,
            addon=self.m_addon.getAddonInfo("Name"),
            version=self.m_addon.getAddonInfo("Version"),
            website=self.m_song.website,
            lyrics=self.m_song.lyrics,
        )
        try:
            # create path
            if (not xbmcvfs.mkdirs(os.path.dirname(self.m_song.lyrics_path))):
                raise IOError(1, "Unable to make dir structure!",
                    os.path.dirname(self.m_song.lyrics_path) + os.pathsep)
            # save lyrics
            if (not xbmcvfs.File(self.m_song.lyrics_path, "w").write(
                    BOM_UTF8 + self.m_song.lyrics.encode("UTF-8", "replace"))):
                raise IOError(2, "Unable to save lyrics!", self.m_song.lyrics_path)
        except IOError as error:
            # log error
            xbmc.log(u"Lyrics::save_lyrics - {error} - {file})".format(
                error=error.strerror, file=error.filename), xbmc.LOGERROR)
            # set error message
            self.m_song.message = self.m_addon.getLocalizedString(30852).format(msg=error.strerror)
            # TODO: should we still display lyrics?
            #self.m_song.status = False
