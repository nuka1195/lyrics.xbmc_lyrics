#!/usr/bin/python
# -*- coding: UTF-8 -*-
#
## Properties Module


class Properties(object):
    """
        Class used to set window properties
    """
    # $MSG[* When playing audio. Properties are set on the "Visualisation" window.]$END_MSG
    # $SUB_MSG[Use: "Window(Visualisation).Property(<property>)"]$END_SUB_MSG
    # $MSG[* When playing video. Properties are set on the "Fullscreen video" window.]$END_MSG
    # $SUB_MSG[Use: "Window(FullScreenVideo).Property(<property>)"]$END_SUB_MSG

    def __init__(self, *args, **kwargs):
        # set title & logo
        self._set_addon_info()
        # set user preferences
        self._set_user_preferences()

    def _set_addon_info(self):
        # $BEGIN_GROUP[Addon Info]
        # Id of addon (useful for customized logo's)
        self.WINDOW.setProperty("Addon.Id", self.m_addon.getAddonInfo("Id"))
        # Full path to addon's icon.png file
        self.WINDOW.setProperty("Addon.Logo", self.m_addon.getAddonInfo("Icon"))
        # Name of addon
        self.WINDOW.setProperty("Addon.Name", self.m_addon.getAddonInfo("Name"))
        # $END_GROUP

    def _set_user_preferences(self):
        # $BEGIN_GROUP[User Preferences]
        # User setting to notify skinner user wants auto scrolling lyrics (True/False)
        self.WINDOW.setProperty("EnableKaraokeMode", str(self.m_addon.getSetting("enable_karaoke_mode")))
        # $END_GROUP

    def set_properties(self, lyrics="", tags=list(), lrc_lyrics=False, message="", website="", status=True, prefetched=False):
        # set informational properties
        self.set_info_properties(message, website, status, prefetched)

        # $BEGIN_GROUP[Special Skinning Properties]
        # Determines if current song supports LRC tagging lyrics (True/False)
        self.WINDOW.setProperty("AllowTagging", str(self.m_addon.getSetting("enable_karaoke_mode") and self.m_addon.getSetting("lyrics_allow_tagging") and self.m_addon.getSetting("autoscroll_lyrics") and self.use_gui and len(tags) == 0 and status and lyrics is not None))
        # Determines if current song supports auto scrolling non LRC tagged lyrics (True/False)
        self.WINDOW.setProperty("Autoscroll", str(not lrc_lyrics and len(tags) > 0))
        # Determines if current song supports LRC auto scrolling lyrics (True/False)
        self.WINDOW.setProperty("KaraokeMode", str(self.m_addon.getSetting("enable_karaoke_mode") and len(tags) > 0 and status))
        # $END_GROUP

        # $BEGIN_GROUP[Lyrics]
        # no need to set lyrics if None
        if (lyrics is not None):
            # This is the song's lyrics (used to populate textbox control)
            self.WINDOW.setProperty("Lyrics", lyrics)
        # $END_GROUP

    def set_info_properties(self, message, website="", status=True, prefetched=False, prefetching=False):
        # $BEGIN_GROUP[Messages]
        # Status message returned from lyrics scraper
        self.WINDOW.setProperty("Message", message)
        # Were the current lyrics prefetched (True/False)
        self.WINDOW.setProperty("Prefetched", repr(prefetched))
        # Are we currently prefetching next songs lyrics (True/False)
        self.WINDOW.setProperty("Prefetching", repr(prefetching))
        # Were valid lyrics found (True/False)
        self.WINDOW.setProperty("Success", repr(status))
        # Website the lyrics were successfully scraped from
        self.WINDOW.setProperty("Website", website)
        # $END_GROUP
