#!/usr/bin/python
# -*- coding: UTF-8 -*-
#
## Player module: main module

from properties import Properties
from song import Song
from threading import Timer
import sys
import xbmc
import xbmcgui


class XBMCPlayer(xbmc.Player):
    """
        Subclass of XBMC Player class.
        Overrides onplayback* events, for custom actions.
    """
    def __init__(self, *args, **kwargs):
        # initialize our super classes
        xbmc.Player.__init__(self)

    def onPlayBackStarted(self):
        # handle start event
        self.handle_onplayback_event("onPlayBackStarted")

    def onQueueNextItem(self):
        # handle queuing event, we just pass as started will handle song change
        # TODO: test to see if this is a better event than started
        self.handle_onplayback_event("onQueueNextItem")

    def onPlayBackStopped(self):
        # handle stopped event
        self.handle_onplayback_event("onPlayBackStopped")

    def onPlayBackEnded(self):
        # handle ended event
        self.handle_onplayback_event("onPlayBackEnded")

    def onPlayBackPaused(self):
        # handle paused event
        self.handle_onplayback_event("onPlayBackPaused")

    def onPlayBackResumed(self):
        # handle resumed event
        self.handle_onplayback_event("onPlayBackResumed")

    def onPlayBackSpeedChanged(self, speed):
        # handle FF/RW event
        self.handle_onplayback_event("onPlayBackSpeedChanged", speed)

    def onPlayBackSeek(self, _time, offset):
        # handle seek event
        self.handle_onplayback_event("onPlayBackSeek", (_time, offset,))

    def onPlayBackSeekChapter(self, chapter):
        # handle chapter seek event
        self.handle_onplayback_event("onPlayBackSeekChapter", chapter)


class Player(XBMCPlayer, Properties):
    # window for setting lyrics properties
    WINDOW = xbmcgui.Window(12006)
    # control id's
    CONTROL_LIST = 110
    CONTROL_SAVE_LYRICS = 606
    # FIXME: is 20 seconds a good time?
    PREFETCH_DELAY_TIME = 20

    def __init__(self, *args, **kwargs):
        # set addon object
        self.m_addon = kwargs["addon"]
        # passing "<windowId>" from RunScript() means run in background
        self.use_gui = kwargs["gui"]
        # initialize our super classes
        XBMCPlayer.__init__(self)
        Properties.__init__(self)
        # initialize timers
        self._lyric_timer = None
        self._fetch_timer = None
        # log started action
        self._log_addon_action("started")
        # initialize our Song class
        self.song = Song(addon=self.m_addon)
        # initialize our prefetched Song class
        # TODO: remove the self.isPlayingAudio() check when/if XBMC supports offset for player
        self.prefetched_song = None
        if (self.m_addon.getSetting("prefetch_lyrics") and self.isPlayingAudio()):
            self.prefetched_song = Song(addon=self.m_addon, prefetch=True)
        # start
        if (self.use_gui):
            self._start_gui()
        else:
            self._start_background()

    def _log_addon_action(self, action):
        # log addon info
        xbmc.log("{0:-<80}".format(""), xbmc.LOGNOTICE)
        xbmc.log(
            u"[ADD-ON] - {name!r} has {action}! [{mode}]".format(
            name=self.m_addon.getAddonInfo("Name"),
            action=action,
            mode=["BACKGROUND MODE (window={id})".format(
                id=sys.argv[-1]), "GUI MODE"][self.use_gui]),
            xbmc.LOGNOTICE
        )
        xbmc.log(
            u"{0: <12}Id: {id} - Type: {type} - Version: {version}".format(
            "",
            id=self.m_addon.getAddonInfo("Id"),
            type=self.m_addon.getAddonInfo("Type"),
            version=self.m_addon.getAddonInfo("Version")),
            xbmc.LOGNOTICE
        )
        xbmc.log("{0:-<80}".format(""), xbmc.LOGNOTICE)

    def _start_gui(self):
        # import GUI class
        from resources.lib.gui import GUI
        # set our GUI class
        self._gui = GUI(
            "custom_lyrics.xbmc_lyrics-gui.xml",
            self.m_addon.getAddonInfo("Path"), "default", "720p",
            player=self
        )
        # show dialog
        self._gui.doModal()
        # free memory
        del self._gui
        # cancel any running timers
        # FIXME: why is this necessary now. before subclass changes this was unnecessary
        self.cancel_timers()

    def _start_background(self):
        # set to True so script will continue
        self._loop = True
        # set window id
        self.window_id = int(sys.argv[1]) + 10000
        # get list control if skinner included one
        try:
            window = xbmcgui.Window(self.window_id)
            listcontrol = window.getControl(self.CONTROL_LIST)
        except Exception:
            listcontrol = None
        # start
        self.startup(listcontrol)
        # loop here to keep script running
        while not xbmc.abortRequested and self._loop:
            # 100 msecs seems like a good number FIXME: play with this
            xbmc.sleep(100)
        # FIXME: why is this necessary now. before subclass changes this was unnecessary
        self.cancel_timers()

    def startup(self, listcontrol=None):
        # set listcontrol object if one exists and user preference is to support scrolling lyrics
        self.listcontrol = [None, listcontrol][self.m_addon.getSetting("enable_karaoke_mode")]
        # start
        self.onPlayBackStarted()

    def handle_onplayback_event(self, event, *args):
        # cancel any timers, (we don't want to cancel timers on queue next item
        #                     XBMC queues next item during onQueueNextItem event
        #                     and cross fading would interrupt scrolling lyrics.)
        if (event != "onQueueNextItem"):
            self.cancel_timers()
        # log event
        xbmc.log(
            "XBMCPlayer::handle_onplayback_event (Event: {event: <35} Playing: {media})".format(
                event="{name} {args}".format(name=event, args=["", "args={0}".format(args)][args != ()]),
                media=["(none)", "Audio", "Video"][int(self.isPlayingAudio()) + (int(self.isPlayingVideo()) * 2)]),
            xbmc.LOGNOTICE
        )
        # on these event there is nothing to do
        if (event in ["onQueueNextItem", "onPlayBackPaused", "onPlayBackSeek", "onPlayBackSeekChapter"]):
            pass
        # on song change fetch lyrics
        elif (event == "onPlayBackStarted"):
            # log title and artist
            xbmc.log(
                u"{0: <36}(Title: {title!r: <36} Artist: {artist!r})".format(
                    "",
                    title=unicode(xbmc.getInfoLabel("MusicPlayer.Title"), "UTF-8"),
                    artist=unicode(xbmc.getInfoLabel("MusicPlayer.Artist"), "UTF-8")),
                xbmc.LOGNOTICE
            )
            # do we have any unsaved tagged lyrics
            if (self.use_gui):
                self._gui._save_user_tagged_lyrics(ask=True)
            # set new timer (we use this in case user is skipping thru playlist)
            self._fetch_timer = Timer(self.m_addon.getSetting("fetch_lyrics_delay") / 1000, self._fetch_lyrics)
            # start timer
            self._fetch_timer.start()
        # on resume from FF/RW we need to reset any timers
        elif (event == "onPlayBackResumed"):
            # update lyric if karaoke mode is enabled
            self._update_lyric()
        # on speedchanged?
        elif (event == "onPlayBackSpeedChanged"):
            # if speed==1 (resumed) we need to update lyrics
            if (args[0] == 1):
                self._update_lyric()
        # if music has ended we want to clear lyrics
        elif (event in ["onPlayBackStopped", "onPlayBackEnded"]):
            # give time for XBMC in case a glitch in a song fired the event
            # (only seems to happen with cross-fading enabled)
            # TODO: determine if this just needs to be hard coded
            xbmc.sleep(int(self.m_addon.getSetting("fetch_lyrics_delay")))
            # if we're still playing continue
            if (self.isPlaying()): return
            # finish up
            self.finish_up()

    def _set_properties(self, lyrics="", tags=list(), lrc_lyrics=False, message="", website="", status=True, prefetched=False):
        # set window properties
        self.set_properties(lyrics, tags, lrc_lyrics, message, website, status, prefetched)
        # only need to fill lyrics list control if lyrics exist, otherwise we just use textbox to display messages.
        if (self.song.m_song.lyrics is not None):
            # fill list if karaoke mode is enabled
            self._set_karaoke_lyrics()  #lyrics, tags)

    def _set_karaoke_lyrics(self):  #, lyrics, tags):
        # if no list control or not user preference skip
        if (self.listcontrol is None or
                not self.m_addon.getSetting("enable_karaoke_mode") or
                (not self.use_gui and not xbmc.getCondVisibility("Window.IsActive({id})".format(id=self.window_id)))):
            return
        # clear list
        self.listcontrol.reset()
        # add lyrics
        self.listcontrol.addItems(self.song.m_song.lyrics.splitlines())
        # select proper lyric
        self._update_lyric()

    def _update_lyric(self):
        # if no time tags, return
        if (not self.isPlaying() or not self.song.m_song.lyrics_tags or self.listcontrol is None or
                not self.m_addon.getSetting("enable_karaoke_mode") or
                (not self.use_gui and not xbmc.getCondVisibility("Window.IsActive({id})".format(id=self.window_id)))):
            return
        #FIXME: make sure this is necessary, I don't believe it is
        # cance only lyric timer
        self.cancel_timers(fetch=False)
        # get current time
        current = self.getTime()
        # get position
        pos = [count for count, tag in enumerate(self.song.m_song.lyrics_tags + [current + 1]) if (tag > current)][0]
        # select listitem
        self.listcontrol.selectItem(pos - 1)
        # return if no more lyrics
        if (pos == len(self.song.m_song.lyrics_tags)): return
        # calculate update time, additional time necessary to limit the number of repeat timer events
        update = self.song.m_song.lyrics_tags[pos] - current + 0.02
        # set new timer
        self._lyric_timer = Timer(update, self._update_lyric)
        # start timer
        self._lyric_timer.start()

    def cancel_timers(self, fetch=True):
        # if there's a timer cancel it
        if (self._lyric_timer is not None):
            self._lyric_timer.cancel()
        if (self._fetch_timer is not None and fetch):
            self._fetch_timer.cancel()

    def _fetch_lyrics(self):
        # set fetching lyrics message
        self._set_properties(
            message=self.m_addon.getLocalizedString(30800).format(
            title=unicode(xbmc.getInfoLabel("MusicPlayer.Title"), "UTF-8"))
        )
        # if prefetching failed, we go straight to song list
        songlist = self.prefetched_song is not None and not self.prefetched_song.m_song.status
        # fetch lyrics
        self.song.get_song_info(songlist=songlist)
        # set lyrics and messages
        self._set_properties(
            self.song.m_song.lyrics,
            self.song.m_song.lyrics_tags,
            self.song.m_song.lrc_lyrics,
            self.song.m_song.message,
            self.song.m_song.website,
            self.song.m_song.status,
            self.song.m_song.prefetched
        )
        # prefetch next song
        if (self.prefetched_song is not None and xbmc.getCondVisibility("MusicPlayer.HasNext")):
            # set new prefetch delay timer
            self._fetch_timer = Timer(
                self.PREFETCH_DELAY_TIME,
                self._prefetch_lyrics,
                (self.song.m_song.message, self.song.m_song.website, self.song.m_song.status, self.song.m_song.prefetched,)
            )
            # start timer
            self._fetch_timer.start()

    def _prefetch_lyrics(self, message, website, status, prefetched):
        # set prefetching message
        self.set_info_properties(
            message=self.m_addon.getLocalizedString(30805).format(
                title=unicode(xbmc.getInfoLabel("MusicPlayer.Offset(1).Title"), "UTF-8")),
            status=status,
            prefetching=True
        )
        # fetch next songs lyrics
        self.prefetched_song.get_song_info()
        # set previous properties
        self.set_info_properties(message, website, status, prefetched)

    def save_user_tagged_lyrics(self, lyrics):
        # set default saved lyrics message
        self.song.m_song.message = self.m_addon.getLocalizedString(30863)
        # set song's lyrics
        self.song.m_song.lyrics = lyrics
        # save lyrics
        self.song.save_lyrics()
        # set new message
        self._set_properties(lyrics=None, message=self.song.m_song.message)

    def finish_up(self):
        # cancel any timer
        self.cancel_timers()
        # close dialog
        if (self.use_gui):
            # close the GUI
            self._gui.close_dialog()
        else:
            # set to False so script will exit
            self._loop = False
            # close window
            xbmc.executebuiltin("Dialog.Close({id})".format(id=self.window_id))
        # clear existing properties
        self._set_properties()
        # log ended action
        self._log_addon_action("ended")
