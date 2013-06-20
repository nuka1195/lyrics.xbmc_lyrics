xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<!--Maintainer: {maintainer}-->
<!--Email: {email}-->
<!--Date: {date}-->
<scraper title="{title}">
    <url address="{baseurl}" useragent="{useragent}">
        <song groupby="{songgroupby}" join="{songjoinchar}" space="{songspacechar}" escape="{songescape}" clean="{songclean}" case="{songcase}" search="{songsearchhead}" urlencode="{songurlencode}">
            <artist head="{artisthead}" tail="{artisttail}"/>
            <title head="{titlehead}" tail="{titletail}"/>
        </song>
    </url>
    <source encoding="{sourceencoding}" compress="{sourcecompress}">
        <lyrics type="{lyricstype}" clean="{lyricsclean}">
            <regex flags="{lyricsregexflags}">{lyricsregexexp}</regex>
            <invalid flags="{lyricsinvalidflags}">{lyricsinvalidexp}</invalid>
        </lyrics>
        <songlist swap="{songlistswap}" always="{songlistalways}" autoselect="{songlistselect}">
            <regex flags="{songlistregexflags}">{songlistregexexp}</regex>
            <invalid flags="{songlistinvalidflags}">{songlistinvalidexp}</invalid>
        </songlist>
    </source>
</scraper>
"""

json = """{{
  'Maintainer': {maintainer!r},
  'Email': {email!r},
  'Date': {date!r},
  'scraper': {{
    'title':{title!r},
    'url': {{
      'address': {baseurl!r},
      'useragent': {useragent!r},
      'song': {{
        'groupby': {songgroupby!r},
        'join': {songjoinchar!r},
        'space': {songspacechar!r},
        'escape': {songescape!r},
        'clean': {songclean!r},
        'case': {songcase!r},
        'search': {songsearchhead!r},
        'urlencode': {songurlencode!r},
        'artist': {{
          'head': {artisthead!r},
          'tail': {artisttail!r},
        }},
        'title': {{
          'head': {titlehead!r},
          'tail': {titletail!r},
        }},
      }},
    }},
    'source': {{
      'encoding': {sourceencoding!r},
      'compress': {sourcecompress!r},
      'lyrics': {{
        'type': {lyricstype!r},
        'clean': {lyricsclean!r},
        'regex': {{
          'exp': {lyricsregexexp!r},
          'flags': {lyricsregexflags!r},
        }},
        'invalid': {{
          'exp': {lyricsinvalidexp!r},
          'flags': {lyricsinvalidflags!r},
        }},
      }},
      'songlist': {{
        'swap': {songlistswap!r},
        'always': {songlistalways!r},
        'autoselect': {songlistautoselect},
        'regex': {{
          'exp': {songlistregexexp!r},
          'flags': {songlistregexflags!r},
        }},
        'invalid': {{
          'exp': {songlistinvalidexp!r},
          'flags': {songlistinvalidflags!r},
        }},
      }},
    }},
  }},
}}
"""

def _escape(text):
    # return escaped text
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\"", "&quot;").replace("'", "&apos;")

def _save_scraper(name):
    exec "from {module} import *".format(module=name)
    filename = TITLE.replace(":", "-")

    open ("../scrapers/{title}.xml".format(title=filename), "w").write(xml.format(
       maintainer=MAINTAINER,
       email=EMAIL,
       date=DATE,
       title=TITLE,
       baseurl=BASE_URL,
       useragent=_escape(USERAGENT),
       songgroupby=" ".join(SONG_GROUP_BY),
       songjoinchar=SONG_JOIN_CHAR,
       songspacechar=SONG_SPACE_CHAR,
       songescape=_escape(SONG_ESCAPE),
       songclean=str(SONG_CLEAN).lower(),
       songcase=SONG_CASE,
       songsearchhead=_escape(SONG_SEARCH_HEAD),
       songurlencode=str(SONG_URLENCODE).lower(),
       artisthead=ARTIST_HEAD,
       artisttail=ARTIST_TAIL,
       titlehead=TITLE_HEAD,
       titletail=TITLE_TAIL,
       sourceencoding=SOURCE_ENCODING,
       sourcecompress=SOURCE_COMPRESS,
       lyricstype=LYRICS_TYPE,
       lyricsclean=str(LYRICS_CLEAN).lower(),
       lyricsregexexp=_escape(LYRICS_REGEX_EXP),
       lyricsregexflags=" ".join(LYRICS_REGEX_FLAGS),
       lyricsinvalidexp=_escape(LYRICS_INVALID_EXP),
       lyricsinvalidflags=" ".join(LYRICS_INVALID_FLAGS),
       songlistswap=str(SONGLIST_SWAP).lower(),
       songlistalways=str(SONGLIST_ALWAYS).lower(),
       songlistselect=str(SONGLIST_AUTO_SELECT).lower(),
       songlistregexexp=_escape(SONGLIST_REGEX_EXP),
       songlistregexflags=" ".join(SONGLIST_REGEX_FLAGS),
       songlistinvalidexp=_escape(SONGLIST_INVALID_EXP),
       songlistinvalidflags=" ".join(SONGLIST_INVALID_FLAGS),
     ))

    open ("../scrapers/{title}.xpr".format(title=filename), "w").write(json.format(
       maintainer=MAINTAINER,
       email=EMAIL,
       date=DATE,
       title=TITLE,
       baseurl=BASE_URL,
       useragent=USERAGENT,
       songgroupby=SONG_GROUP_BY,
       songjoinchar=SONG_JOIN_CHAR,
       songspacechar=SONG_SPACE_CHAR,
       songescape=SONG_ESCAPE,
       songclean=SONG_CLEAN,
       songcase=SONG_CASE,
       songsearchhead=SONG_SEARCH_HEAD,
       songurlencode=SONG_URLENCODE,
       artisthead=ARTIST_HEAD,
       artisttail=ARTIST_TAIL,
       titlehead=TITLE_HEAD,
       titletail=TITLE_TAIL,
       sourceencoding=SOURCE_ENCODING,
       sourcecompress=SOURCE_COMPRESS,
       lyricstype=LYRICS_TYPE,
       lyricsclean=LYRICS_CLEAN,
       lyricsregexexp=LYRICS_REGEX_EXP,
       lyricsregexflags=LYRICS_REGEX_FLAGS,
       lyricsinvalidexp=LYRICS_INVALID_EXP,
       lyricsinvalidflags=LYRICS_INVALID_FLAGS,
       songlistswap=SONGLIST_SWAP,
       songlistalways=SONGLIST_ALWAYS,
       songlistautoselect=SONGLIST_AUTO_SELECT,
       songlistregexexp=SONGLIST_REGEX_EXP,
       songlistregexflags=SONGLIST_REGEX_FLAGS,
       songlistinvalidexp=SONGLIST_INVALID_EXP,
       songlistinvalidflags=SONGLIST_INVALID_FLAGS,
     ))

    return True


if (__name__ == "__main__"):
    name = "LyrDB"
    success = _save_scraper(name)
    if (success):
        print "Saved {name}.xpr in scrapers directory".format(name=name)
