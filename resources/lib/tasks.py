#!/usr/bin/python
# -*- coding: UTF-8 -*-
#
## Tasks Module: Runs common tasks

import xbmc
import xbmcgui


class Tasks(object):
    """
        Tasks Class: Runs common tasks
    """

    def __init__(self, *args, **kwargs):
        # set addon object
        self.m_addon = kwargs["addon"]
        # do task
        exec "self.{task}()".format(task=kwargs["task"])

    def check_for_updates(self):
        def _convert_version(version):
            # split parts into major, minor & micro
            parts = version.split(".")
            # return an integer value
            return int(parts[0]) * 100000 + int(parts[1]) * 1000 + int(parts[2])
        try:
            # import needed modules
            import re
            import urllib2
            # create dialog
            pDialog = xbmcgui.DialogProgress()
            # give feedback
            pDialog.create(self.m_addon.getAddonInfo("Name"), self.m_addon.getLocalizedString(30760))
            pDialog.update(0)
            # URL to addon.xml file
            url = "{repo}{branch}{id}/addon.xml".format(repo=self.m_addon.getSetting("repo"), branch=self.m_addon.getSetting("branch"), id=self.m_addon.getAddonInfo("Id"))
            # get addon.xml source
            xml = urllib2.urlopen(url).read()
            # parse version
            version = re.search("<addon.+?version\=\"(.+?)\".*?>", xml, re.DOTALL).group(1)
        except urllib2.URLError as error:
            # set proper error messages
            msg1 = self.m_addon.getLocalizedString(30770)
            msg2 = str(error)
            msg3 = url
        else:
            # set proper message
            msg1 = self.m_addon.getLocalizedString(30700).format(version=self.m_addon.getAddonInfo("Version"))
            msg2 = ""
            msg3 = [self.m_addon.getLocalizedString(30701), self.m_addon.getLocalizedString(30702).format(version=version)][_convert_version(version) > _convert_version(self.m_addon.getAddonInfo("Version"))]

        # done, close dialog
        pDialog.close()
        # notify user of result
        ok = xbmcgui.Dialog().ok(self.m_addon.getAddonInfo("Name"), msg1, msg2, msg3)

    def clear_artist_aliases(self):
        # import needed modules
        import os
        # ask if user is sure
        if (xbmcgui.Dialog().yesno(self.m_addon.getAddonInfo("Name"), self.m_addon.getLocalizedString(30845))):
            # create path to alias file
            path = os.path.join(xbmc.translatePath(self.m_addon.getAddonInfo("Profile")).decode("UTF-8"), u"artist_aliases.txt")
            # if file exists remove it
            if (os.path.exists(path)):
                os.remove(path)
            # notify user
            ok = xbmcgui.Dialog().ok(self.m_addon.getAddonInfo("Name"), self.m_addon.getLocalizedString(30830))

    def scraper_editor(self):
        # import GUI class
        from resources.lib.editor import GUI
        # set our GUI class
        gui = GUI("lyrics.xbmc_lyrics-editor.xml", self.m_addon.getAddonInfo("Path"), "default", "720p", addon=self.m_addon)
        # show dialog
        gui.doModal()
        # free memory
        del gui
