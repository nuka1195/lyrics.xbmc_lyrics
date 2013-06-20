#!/usr/bin/python
# -*- coding: UTF-8 -*-
#
## GUI Module for running in foreground

import xbmcgui


class GUI(xbmcgui.WindowXMLDialog):
    """GUI Class:

    Main window shows lyrics and adds ability to tag lyrics in LRC simple format.

    """
    # default actions
    ACTION_CLOSE_DIALOG = (9, 10,)
    # timeout for yesno dialog
    AUTO_CLOSE_TIME = 30000

    def __init__(self, *args, **kwargs):
        # initialize our super class
        xbmcgui.WindowXMLDialog.__init__(self)
        # clear GUI attributes
        self._clear_gui_attributes()
        # set our passed Player class
        self._player = kwargs["player"]
        # TODO: we set self._allow_tagging and self._tag_offset for faster performance?
        # allow tagging
        self._allow_tagging = (self._player.m_addon.getSetting("enable_karaoke_mode") and
            not self._player.m_addon.getSetting("autoscroll_lyrics") and
            self._player.m_addon.getSetting("lyrics_allow_tagging"))
        # tag offset setting
        # TODO: is this assignment necessary? we set the setting already, probably fast enough
        self._tag_offset = self._player.m_addon.getSetting("lyrics_tagging_offset")

    def onInit(self):
        try:
            # grab list control (try catch is necessary in case skinner did not
            # include a list control for karaoke mode)
            self._listcontrol = self.getControl(self._player.CONTROL_LIST)
        except Exception:
            # no control, set to None
            self._listcontrol = None
        # start
        self._player.startup(self._listcontrol)

    def onAction(self, action):
        # only action is close
        if (action in self.ACTION_CLOSE_DIALOG):
            self._player.finish_up()

    def onClick(self, controlId):
        # tag lyric
        if (controlId == self._player.CONTROL_LIST and self._allow_tagging):
            self._append_tagged_lyric()
        # save lyrics
        elif (controlId == self._player.CONTROL_SAVE_LYRICS):
            self._save_user_tagged_lyrics()

    def onFocus(self, controlId):
        pass

    def _clear_gui_attributes(self, tagged=True):
        # initialize these for tagging
        if (tagged): self._tagged_lyrics = list()
        self._non_lyrics = list()

    def _append_tagged_lyric(self):
        # get current time
        current = self._player.getTime() + self._tag_offset
        # get current lyric
        lyric = unicode(self._listcontrol.getSelectedItem().getLabel(), "UTF-8")
        # mark as tagged
        self._listcontrol.getSelectedItem().setLabel2(u"\u221A")
        # select next item
        self._listcontrol.selectItem(self._listcontrol.getSelectedPosition() + 1)
        # if a non lyric line we don't want to highlight it
        if (not lyric or lyric.startswith("[")):
            self._non_lyrics.append(lyric)
        else:
            # format tag
            tag = "[{0:1.0f}:{1:05.02f}]".format(*divmod(current, 60))
            # set any non lyrics with tag
            for non_lyric in self._non_lyrics:
                self._tagged_lyrics.append(tag + non_lyric)
            # set current lyric with tag
            self._tagged_lyrics.append(tag + lyric)
            # reset non lyrics
            self._clear_gui_attributes(tagged=False)

    def _save_user_tagged_lyrics(self, ask=False):
        # only save if lyrics were tagged
        if (self._tagged_lyrics):
            # show a yes/no dialog if ask is True
            if (ask):
                ok = xbmcgui.Dialog().yesno(
                    heading=self._player.song.m_song.title,
                    line1=self._player.m_addon.getLocalizedString(30840),
                    autoclose=self.AUTO_CLOSE_TIME
                )
            # are we go for saving
            if (not ask or ok):
                # join together and save lyrics
                self._player.save_user_tagged_lyrics("\n".join(self._tagged_lyrics))
        # clear gui attributes
        self._clear_gui_attributes()

    def close_dialog(self):
        # save any lyrics?
        self._save_user_tagged_lyrics(ask=True)
        # close dialog
        self.close()
