MAINTAINER = u"nuka1195"
EMAIL = ""
DATE = "2012.05.14"

TITLE = u"LyricsTime"
BASE_URL = "http://www.lyricstime.com/"
USERAGENT = "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 1.1.4322; .NET CLR 2.0.50727)"
SONG_GROUP_BY = []
SONG_JOIN_CHAR = "-"
SONG_SPACE_CHAR = "-"
SONG_ESCAPE = ""
SONG_CLEAN = True
SONG_CASE = "lower"
SONG_SEARCH_HEAD = ""
SONG_URLENCODE = False
ARTIST_HEAD = ""
ARTIST_TAIL = "-lyrics.html"
TITLE_HEAD = ""
TITLE_TAIL = "-lyrics.html"
SOURCE_ENCODING = "UTF-8"
SOURCE_COMPRESS = ""
LYRICS_TYPE = "standard"
LYRICS_CLEAN = True
LYRICS_REGEX_EXP = "<div.+?id=\"songlyrics\".*?>(.+?)</div>"
LYRICS_REGEX_FLAGS = ["dotall", "ignorecase" ]
LYRICS_INVALID_EXP = ""
LYRICS_INVALID_FLAGS = []
SONGLIST_SWAP = True
SONGLIST_ALWAYS = False
SONGLIST_AUTO_SELECT = False
SONGLIST_REGEX_EXP = "<a.+?href=\"/(.+?-lyrics.html)\"><b>[^<]+</b>([^<]+)<b>lyrics</b></a><br/>"
SONGLIST_REGEX_FLAGS = ["ignorecase"]
SONGLIST_INVALID_EXP = ""
SONGLIST_INVALID_FLAGS = []
