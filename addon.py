#!/usr/bin/python
# -*- coding: UTF-8 -*-
#
## XBMC Lyrics

from resources.lib.addonmodule import XBMCAddon
import sys

ADDON_ID = "lyrics.xbmc_lyrics"


if (__name__ == "__main__"):
    """We pass an instance of XBMCAddon() to all modules to keep it consistent
    and to avoid the calls to __set_settings()

    """
    # text viewer
    if (len(sys.argv) == 2 and sys.argv[1].startswith("view=")):
        import resources.lib.viewer as viewer
        viewer.Viewer(addon=XBMCAddon(), view=sys.argv[1].split("=")[1])
    # utilities
    elif (len(sys.argv) == 2 and sys.argv[1].startswith("task=")):
        import resources.lib.tasks as tasks
        tasks.Tasks(addon=XBMCAddon(), task=sys.argv[1].split("=")[1])
    # player
    else:
        import resources.lib.player as player
        player.Player(addon=XBMCAddon(), gui=len(sys.argv) == 1)
