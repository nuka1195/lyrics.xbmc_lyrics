#!/usr/bin/python
# -*- coding: UTF-8 -*-
#
## debugging module

import xbmc
from song import Song
from addonmodule import XBMCAddon


if (__name__ == "__main__"):

    # set to song you wish to test
    SONG_ID = 17

    songs = {
        0: (u"Wings", u"Live and let Die",),
        1: (u"The Guess Who", u"Proper Stranger",),
        2: (u"The Beatles", u"Back in the USSR",),
        3: (u"britney spears", u"(You Drive Me) Crazy",),
        4: (u"38 Special", u"Rockin' Into the Night",),
        5: (u"The babys", u"Isn't it time",),
        6: (u"4 Non Blondes", u"Dear Mr. President",),
        7: (u"ABBA", u"Gimme! Gimme! Gimme! (A Man After Midnight)",),
        8: (u"AC/DC", u"Have a Drink on Me",),
        9: (u"Blue Öyster Cult", u"Burning for you",),
        10: (u"The Rolling Stones (feat. Cheryl Crow)", u"Get off of my cloud",),
        11: (u"38 Special", u"Hold on Loosely",),
        12: (u"ABBA", u"Eagle",),
        13: (u"Enya", u"Aniron (I Desire)",),
        14: (u"Enya", u"Book of Days",),
        15: (u"*NSync", u"Bye Bye Bye",),
        16: (u"Enya", u"Orinoco Flow",),
        17: (u"ABBA", u"S.O.S.",),
        18: (u"Duffy", u"Warwick Avenue",),
        19: (u"Eminem", u"Not Afraid",),
        20: (u"Queen", u"I Want to Break Free",),
        21: (u"Eminem", u"'97 bonnie & clyde",),
        22: (u"Clairy Browne and the Bangin’ Rackettes", u"Love Letter",),
        23: (u"Reba McEntire", u"The Night The Lights Went Out In Georgia",),
        24: (u"Styx", u"Renegade",),
        25: (u"Enya", u"Orinoco Flow",),
    }

    xbmc.INFOLABEL["musicplayer.offset(0).artist"] = ""  #songs[SONG_ID][0]
    xbmc.INFOLABEL["musicplayer.offset(0).title"] = ""  #songs[SONG_ID][1]
    xbmc.INFOLABEL["musicplayer.offset(0).filenameandpath"] = "/Users/scottjohns/Development/debug/music/{artist}/{album}/{artist} - {title}.mp3".format(artist=songs[SONG_ID][0], album="Unknown", title=songs[SONG_ID][1])

    class Player(object):

        def __init__(self, addon):
            # set addon object
            self.m_addon = addon
            # grab our dummy song class
            self.song = Song(addon=self.m_addon, prefetch=False)
            self.song.get_song_info()
            self._set_karaoke_lyrics(self.song.m_song.lyrics, self.song.m_song.lyrics_tags)
            #scraper = Scraper(prefetch=False)
            #scraper.fetch_lyrics(_song, False)
            # print result
            print
            print u"Status for '{title}' by '{artist}'".format(title=self.song.m_song.title, artist=self.song.m_song.artist)
            print u"site={website!r: <29}success={status!r: <10}message={msg!r}".format(website=self.song.m_song.website, status=self.song.m_song.status, msg=self.song.m_song.message)
            if (self.song.m_song.lyrics is not None):
                print "----------"
                print "Lyrics:"
                print "----------"
                for count, lyric in enumerate(self.song.m_song.lyrics.splitlines()):
                    print u"[{0:1.0f}:{1:05.02f}] - {lyric}".format(*divmod(self.song.m_song.lyrics_tags[count], 60), lyric=lyric)

        def _set_karaoke_lyrics(self, lyrics, tags):
            pass

    Player(addon=XBMCAddon())
