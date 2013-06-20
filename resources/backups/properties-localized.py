## Properties Module

class Properties:

    def __init__( self, *args, **kwargs ):
        # set our Addon class
        self.Addon = kwargs[ "Addon" ]
        # set our window object
        self.WINDOW = kwargs[ "window" ]
        # set title & logo
        self._set_addon_info()
        # set user preferences
        self._set_user_preferences()

    def _set_addon_info( self ):
        """ set addon's logo, id and name """

        # $BEGIN_GROUP[30910]
        # $LOCALIZE[30911]
        self.WINDOW.setProperty( "Addon.Logo", self.Addon.getAddonInfo( "Icon" ) )
        # $LOCALIZE[30912]
        self.WINDOW.setProperty( "Addon.Id", self.Addon.getAddonInfo( "Id" ) )
        # $LOCALIZE[30913]
        self.WINDOW.setProperty( "Addon.Name", self.Addon.getAddonInfo( "Name" ) )
        # $END_GROUP

    def _set_user_preferences( self ):
        """ set user preference settings """

        # $BEGIN_GROUP[30920]
        self.WINDOW.setProperty( "EnableKaraokeMode", self.Addon.getSetting( "enable_karaoke_mode" ) )
        # $END_GROUP

    def _set_properties( self, lyrics="", tags=list(), lrc_lyrics=False, message="", website="", status=True, prefetched=False ):
        """ we set the properties on the visualisation window """

        # set informational properties
        self._set_info_properties( message, website, status, prefetched )

        # $BEGIN_GROUP[30930]
        self.WINDOW.setProperty( "Autoscroll", str( not lrc_lyrics and len( tags ) > 0 ) )
        self.WINDOW.setProperty( "KaraokeMode", str( self.Addon.getSetting( "enable_karaoke_mode" ) == "true" and len( tags ) > 0 and status ) )
        self.WINDOW.setProperty( "AllowTagging", str( self.Addon.getSetting( "enable_karaoke_mode" ) == "true" and self.Addon.getSetting( "lyrics_allow_tagging" ) == "true" and self.Addon.getSetting( "autoscroll_lyrics" ) == "false" and self.use_gui and len( tags ) == 0 and status and lyrics is not None ) )
        # $END_GROUP

        # $BEGIN_GROUP[30940]
        # if lyrics is None we only set messages
        if ( lyrics is not None ):
            # set lyrics property for textbox control
            # LOCALIZE[30951]
            self.WINDOW.setProperty( "Lyrics", lyrics )
        # $END_GROUP

    def _set_info_properties( self, message, website="", status=True, prefetched=False, prefetching=False ):
        """ set status properties """

        # $BEGIN_GROUP[30950]
        # LOCALIZE[30951]
        self.WINDOW.setProperty( "Message", message )
        # LOCALIZE[30952]
        self.WINDOW.setProperty( "Website", website )
        # LOCALIZE[30953]
        self.WINDOW.setProperty( "Success", str( status ) )
        # LOCALIZE[30954]
        self.WINDOW.setProperty( "Prefetched", str( prefetched ) )
        # LOCALIZE[30955]
        self.WINDOW.setProperty( "Prefetching", str( prefetching ) )
        # $END_GROUP

print str( False )
