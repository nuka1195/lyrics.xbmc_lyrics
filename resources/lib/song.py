#!/usr/bin/python
# -*- coding: UTF-8 -*-
#
## Song module

from lyrics import Lyrics
import os
import xbmc


class Info(object):
    pass


class Song(Lyrics):
    """Song Class:

    Parses song info and holds all song attributes.

    """
    # infolabel constants
    # TODO: change to Player.* when/if XBMC supports Player.Offset
    INFOLABEL_ARTIST = "MusicPlayer.Offset({prefetch:d}).Artist"
    INFOLABEL_ALBUM = "MusicPlayer.Offset({prefetch:d}).Album"
    INFOLABEL_TITLE = "MusicPlayer.Offset({prefetch:d}).Title"
    INFOLABEL_FILEPATH = "MusicPlayer.Offset({prefetch:d}).FilenameAndPath"

    def __init__(self, *args, **kwargs):
        # set addon object
        self.m_addon = kwargs["addon"]
        # our we prefetching
        self.prefetch = kwargs.get("prefetch", False)
        # clear song info
        self._clear_song_attributes()
        # initialize our super classes
        Lyrics.__init__(self)

    def get_song_info(self, songlist=False):
        # clear song info
        self._clear_song_attributes()
        # TODO: when/if XBMC supports Player.offset(), we can then support video
        # just need to change MusicPlayer -> Player
        # get song info from infolabels
        self.m_song.artist = unicode(xbmc.getInfoLabel(
            self.INFOLABEL_ARTIST.format(prefetch=self.prefetch)), "UTF-8")
        self.m_song.album = unicode(xbmc.getInfoLabel(
            self.INFOLABEL_ALBUM.format(prefetch=self.prefetch)), "UTF-8")
        self.m_song.title = unicode(xbmc.getInfoLabel(
            self.INFOLABEL_TITLE.format(prefetch=self.prefetch)), "UTF-8")
        file_ = unicode(xbmc.getInfoLabel(
            self.INFOLABEL_FILEPATH.format(prefetch=self.prefetch)), "UTF-8")
        # if no proper tags, parse from filename
        if (not self.m_song.artist or not self.m_song.title):
            self._get_song_info_from_filename(file_)
        # no song info found so skip
        if (self.m_song.artist is None):
            # set no song info error message and status
            self.m_song.message = self.m_addon.getLocalizedString(30850)
            self.m_song.status = False
        else:
            # we use localized "Unknown" for non existent albums.
            # it's used for tagging and saving lyrics
            self.m_song.album = self.m_song.album or self.m_addon.getLocalizedString(30799)
            # split basepath from file
            basepath, file_ = os.path.split(file_)
            # set shared path if user preference
            if (self.m_addon.getSetting("lyrics_save_mode") == 0):
                # set basepath
                basepath = self.m_addon.getSetting("lyrics_save_path")
                # set user subfolder preference
                if (self.m_addon.getSetting("lyrics_subfolder_template") == r"%A/"):
                    subfolder = self.m_song.artist
                else:
                    subfolder = os.path.join(self.m_song.artist, self.m_song.album)
            # set song path if user preference
            elif (self.m_addon.getSetting("lyrics_save_mode") in [1, 2]):
                # if save to artist's folder, assume artist/album/song.ext folder structure
                if (self.m_addon.getSetting("lyrics_save_mode") == 2):
                    basepath = os.path.dirname(basepath)
                # set user preferred subfolder
                subfolder = self.m_addon.getSetting("lyrics_subfolder")
            # change extension
            file_ = u"{file}{ext}".format(file=os.path.splitext(file_)[0],
                ext=self.m_addon.getSetting("lyrics_save_extension"))
            # create path to lyric file
            self.m_song.lyrics_path = xbmc.validatePath(
                xbmc.makeLegalFilename(os.path.join(basepath, subfolder, file_))).decode("UTF-8")
            # get lyrics
            self.get_lyrics(songlist)

    def _clear_song_attributes(self):
        # initialize our song attributes
        self.m_song = Info()
        self.m_song.album = None
        self.m_song.artist = None
        self.m_song.lrc_lyrics = False
        self.m_song.lyrics = None
        self.m_song.lyrics_path = None
        self.m_song.lyrics_tags = list()
        self.m_song.message = None
        self.m_song.prefetch = self.prefetch
        self.m_song.prefetched = False
        self.m_song.status = True
        self.m_song.title = None
        self.m_song.website = ""

    def _get_song_info_from_filename(self, file_):
        try:
            # log message
            xbmc.log(u"Song::_get_song_info_from_filename (format={format!r}, file={file!r})".format(
                format=self.m_addon.getSetting("song_filename_template"), file=file_), xbmc.LOGDEBUG)
            # parse artist/title from filename
            if (self.m_addon.getSetting("song_filename_template") == r"[%N - ]%A - %T"):
                artist, title = os.path.splitext(os.path.basename(file_))[0].split("-")[-2:]
                album = self.m_addon.getLocalizedString(30799)
            # parse artist and album from folder names, title from filename
            elif (self.m_addon.getSetting("song_filename_template") == r"%A/%B/[%N - ][%A - ]%T"):
                artist = os.path.basename(os.path.dirname(os.path.dirname(file_)))
                # if we couldn't get artist, raise an error, should never happen, but you
                # could get an invalid artist name, which won't raise an error
                if (not artist):
                    raise ValueError
                album = os.path.basename(os.path.dirname(file_))
                title = os.path.splitext(os.path.basename(file_))[0].split("-")[-1]
        except ValueError:
            # log error
            xbmc.log("Invalid file format setting! (could not determine artist)", xbmc.LOGERROR)
            # clear song info if a parsing error occurred
            self._clear_song_attributes()
        else:
            # set our member variables
            self.m_song.artist = artist.strip()
            self.m_song.album = album.strip()
            self.m_song.title = title.strip()
