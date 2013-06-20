Find, download, save and display song lyrics from the Internet using JSON based scrapers. Displays embedded lyrics if available. Ability to play and tag LRC (simple format) lyrics. *see Tagging lyrics. Can be set to auto-scroll non LRC lyrics. Can save lyrics in the song's folder or the song's artist folder under an optional sub-folder or a shared folder under album and/or artist sub-folders. (*Note, to save under the song's artist folder your folder structure must be artist/album/song.ext; this is good for multiple albums with same songs, but songs must also be named the same to prevent duplicates.) *see settings.

Uses primary scraper first then searches using other enabled scrapers in your preferred order. *see settings. Will list all available songs for an artist if no song match was found. Artist aliases allow you to input an alias if no artist match was found. Ability to prefetch the next songs lyrics (will not interrupt user if no match was found).

Can run as a stand alone script (GUI mode) or in the background. *see Running add-on.

*Thanks to VelvetKevorkian for the icon.png.


[B]Running add-on:[/B]
----------------------------------------------------------------------------------------------------------------------------------------------------------
[I]Gui mode[/I] - RunScript(lyrics.xbmc.lyrics)
Allows tagging LRC (simple format) lyrics. Script exits when you close the dialog or music ends.

[I]Background mode[/I] - RunScript(lyrics.xbmc.lyrics,[I]<windowId>[/I])
Allows navigating away while script continues to run. Script exits when music ends.
[I]*requires skin support. Use resources/skins/default as a base skin.[/I]
----------------------------------------------------------------------------------------------------------------------------------------------------------

[B]Tagging lyrics:[/B]
----------------------------------------------------------------------------------------------------------------------------------------------------------
Add-on must be run in GUI mode. You must enable Karaoke mode and lyrics tagging in settings (there is a tagging offset setting to aid you).

    1. Start music and launch XBMC Lyrics
    2. Move to the lyrics control
    3. As each lyric is sung, click the appropriate lyric
    4. When done click the save lyrics button
[COLOR 00000000]    4. [/COLOR][I](If the song changes, you will be prompted to save tagged lyrics)[/I]

[B]Creating a scraper:[/B]
----------------------------------------------------------------------------------------------------------------------------------------------------------
In settings you may run Scraper Editor. This is a helper script that allows easy formatting of the scraper.xpr file. Just fill in the required information and press save.


*Tips: Disable cross-fading. Any blank line or line that starts with a [ will be considered a non lyric (e.g. [Chorus]). These lines are only for formatting and will be skipped when in Karaoke mode. If you make a mistake, you may be able to click a line again, then manually edit the lyrics file later (be careful if a non lyric line was clicked, it must have the same time as the next lyric). 
----------------------------------------------------------------------------------------------------------------------------------------------------------
