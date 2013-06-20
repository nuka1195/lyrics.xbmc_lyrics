MAINTAINER = u"nuka1195"
EMAIL = ""
DATE = "2012.05.14"

TITLE = u"LyricsMode"
BASE_URL = "http://www.lyricsmode.com/lyrics/"
USERAGENT = "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 1.1.4322; .NET CLR 2.0.50727)"
SONG_GROUP_BY_ARTIST = "$GROUP[0-9]$GROUP[1ST_LETTER]"
SONG_GROUP_BY = ["$ARTIST[0-9]", "$ARTIST[1ST_LETTER]"]
SONG_JOIN_CHAR = "/"
SONG_SPACE_CHAR = "_"
SONG_ESCAPE = ""
SONG_CLEAN = True
SONG_CASE = "lower"
SONG_SEARCH_HEAD = ""
SONG_URLENCODE = False
ARTIST_HEAD = ""
ARTIST_TAIL = "/"
TITLE_HEAD = ""
TITLE_TAIL = ".html"
SOURCE_ENCODING = "ISO-8859-1"
SOURCE_COMPRESS = "gzip"
LYRICS_TYPE = "standard"
LYRICS_CLEAN = True
LYRICS_REGEX_EXP = "<div.+?id='songlyrics_h'.+?class='dn'>(.+?)</div>"
LYRICS_REGEX_FLAGS = ["dotall", "ignorecase" ]
LYRICS_INVALID_EXP = ""
LYRICS_INVALID_FLAGS = []
SONGLIST_SWAP = True
SONGLIST_ALWAYS = False
SONGLIST_AUTO_SELECT = False
SONGLIST_REGEX_EXP = "<a.+?href=\"/lyrics/([^\"]+)\".+?title=\"[^\"]+\">(.+?) lyrics[^<]*</a>"
SONGLIST_REGEX_FLAGS = ["ignorecase"]
SONGLIST_INVALID_EXP = ""
SONGLIST_INVALID_FLAGS = []
