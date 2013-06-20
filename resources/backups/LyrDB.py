MAINTAINER = u"nuka1195"
EMAIL = ""
DATE = "2012.05.14"

TITLE = u"LyrDB"
BASE_URL = "http://www.lyrdb.com/karaoke/"
USERAGENT = "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 1.1.4322; .NET CLR 2.0.50727)"
SONG_GROUP_BY = []
SONG_JOIN_CHAR = "+"
SONG_SPACE_CHAR = "+"
SONG_ESCAPE = ""
SONG_CLEAN = True
SONG_CASE = "lower"
SONG_SEARCH_HEAD = "?action=search&q="
SONG_URLENCODE = False
ARTIST_HEAD = ""
ARTIST_TAIL = ""
TITLE_HEAD = ""
TITLE_TAIL = ""
SOURCE_ENCODING = "UTF-8"
SOURCE_COMPRESS = "gzip"
LYRICS_TYPE = "lrc"#["standard", "lrc"][1]
LYRICS_CLEAN = True#["false", "true"][1]
LYRICS_REGEX_EXP = "<p.+?style=\"font-family:[^\"]+\">(.+?)</p></div>"
LYRICS_REGEX_FLAGS = ["dotall", "ignorecase"]
LYRICS_INVALID_EXP = ""
LYRICS_INVALID_FLAGS = []#" ".join(["dotall", "ignorecase", "multiline"][1 : 2])
SONGLIST_SWAP = True#["false", "true"][1]
SONGLIST_ALWAYS = True#["false", "true"][1]
SONGLIST_AUTO_SELECT = True#"auto"#["manual", "auto"][1]
SONGLIST_REGEX_EXP = "<tr><td.+?class=\"tresults\"><a.+?href=\"/karaoke/([0-9]+.htm)\">(.*?)</td><td.+?class=\"tresults\">(.*?)</td>"
SONGLIST_REGEX_FLAGS = ["ignorecase"] # " ".join(["dotall", "ignorecase", "multiline"][1 : 2])
SONGLIST_INVALID_EXP = ""
SONGLIST_INVALID_FLAGS = []#""# ".join(["dotall", "ignorecase", "multiline"][1 : 2])
