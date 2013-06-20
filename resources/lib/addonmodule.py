#!/usr/bin/python
# -*- coding: UTF-8 -*-
#
## xbmcaddon.Addon module

import xbmc
import xbmcaddon

__all__ = ["XBMCAddon"]


class XBMCAddon(xbmcaddon.Addon):
    """XBMCAddon Class:

    Subclasses xbmcaddon.Addon class to override getSetting() and return proper setting values.

    """

    def __init__(self, *args, **kwargs):
        # initialize Addon class
        xbmcaddon.Addon.__init__(self)
        # set settings
        self.__set_settings()

    def __set_settings(self):
        """sets all settings to proper values expected by the addon"""
        # private dict() to hold settings
        self.__settings = {
            "autoscroll_lyrics": super(XBMCAddon, self).getSetting("autoscroll_lyrics") == "true",
            "autoscroll_lyrics_delay": int(float(super(XBMCAddon, self).getSetting("autoscroll_lyrics_delay"))),
            "branch": super(XBMCAddon, self).getSetting("branch"),
            "editor_scraper": super(XBMCAddon, self).getSetting("editor_scraper"),
            "enable_karaoke_mode": super(XBMCAddon, self).getSetting("enable_karaoke_mode") == "true",
            "fetch_lyrics_delay": float(super(XBMCAddon, self).getSetting("fetch_lyrics_delay")),
            "lyrics_allow_tagging": super(XBMCAddon, self).getSetting("lyrics_allow_tagging") == "true",
            "lyrics_save_extension": super(XBMCAddon, self).getSetting("lyrics_save_extension"),
            "lyrics_save_mode": int(super(XBMCAddon, self).getSetting("lyrics_save_mode")),
            "lyrics_save_path": xbmc.translatePath(super(XBMCAddon, self).getSetting("lyrics_save_path").replace(
                "$PROFILE", super(XBMCAddon, self).getAddonInfo("profile"))),
            "lyrics_subfolder": super(XBMCAddon, self).getSetting("lyrics_subfolder"),
            "lyrics_subfolder_template": super(XBMCAddon, self).getSetting("lyrics_subfolder_template"),
            "lyrics_tagging_offset": float(super(XBMCAddon, self).getSetting("lyrics_tagging_offset")) / 1000,
            "prefetch_lyrics": super(XBMCAddon, self).getSetting("prefetch_lyrics") == "true",
            "repo": super(XBMCAddon, self).getSetting("repo"),
            "scraper_1": super(XBMCAddon, self).getSetting("scraper_1"),
            "scraper_2": super(XBMCAddon, self).getSetting("scraper_2"),
            "scraper_3": super(XBMCAddon, self).getSetting("scraper_3"),
            "scraper_4": super(XBMCAddon, self).getSetting("scraper_4"),
            "scraper_5": super(XBMCAddon, self).getSetting("scraper_5"),
            "song_filename_template": super(XBMCAddon, self).getSetting("song_filename_template"),
        }

    def getSetting(self, id):
        """method to override xbmcaddon.Addon().getSetting to return proper values"""

        # return converted setting in proper form
        return self.__settings[id]

    def setSetting(self, id, value):
        """method to override xbmcaddon.Addon().setSetting to set string values"""

        # set new value for id
        self.__settings[id] = value
        # convert value and set
        if (isinstance(value, bool)):
            pass
