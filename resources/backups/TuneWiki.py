MAINTAINER = u"nuka1195"
EMAIL = ""
DATE = "2012.05.14"

TITLE = u"TuneWiki"
BASE_URL = "http://www.tunewiki.com/"
USERAGENT = "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 1.1.4322; .NET CLR 2.0.50727)"
SONG_GROUP_BY = []
SONG_JOIN_CHAR = "/"
SONG_SPACE_CHAR = "-"
SONG_ESCAPE = "-"
SONG_CLEAN = False
SONG_CASE = "lower"
SONG_SEARCH_HEAD = ""
SONG_URLENCODE = True
ARTIST_HEAD = "artists/"
ARTIST_TAIL = ""
TITLE_HEAD = "lyrics/"
TITLE_TAIL = ""
SOURCE_ENCODING = "UTF-8"
SOURCE_COMPRESS = "gzip"
LYRICS_TYPE = "standard"
LYRICS_CLEAN = True
LYRICS_REGEX_EXP = "<p class=\"lyric-lines\" unselectable=\"on\">(.+?)</p>"
LYRICS_REGEX_FLAGS = ["dotall", "ignorecase"]
LYRICS_INVALID_EXP = "(No lyrics available.|We don't have lyrics for this song!|These lyrics have been )"
LYRICS_INVALID_FLAGS = ["ignorecase"]
SONGLIST_SWAP = True
SONGLIST_ALWAYS = False
SONGLIST_AUTO_SELECT = False
SONGLIST_REGEX_EXP = "<li><a href=\"/lyrics/(.+?/.+?)\">(.+?)</a></li>"
SONGLIST_REGEX_FLAGS = ["ignorecase"]
SONGLIST_INVALID_EXP = ""
SONGLIST_INVALID_FLAGS = []
