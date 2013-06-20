#!/usr/bin/python
# -*- coding: UTF-8 -*-
#
## Scraper Editor

from datetime import datetime
import os
import xbmc
import xbmcgui


class GUI(xbmcgui.WindowXMLDialog):
    """
        GUI class: used for editing scraper files.
    """
    # default actions
    ACTION_CLOSE_DIALOG = (9, 10,)

    BUTTON_OK = 30010
    BUTTON_CANCEL = 30011
    BUTTON_RESET = 30012
    BUTTON_OPEN = 30013

    CONTROL_START = 100
    CONTROL_END = CONTROL_START + 34

    CATEGORY_BUTTON_START = 300
    CATEGORY_BUTTON_END = CATEGORY_BUTTON_START + 2

    def __init__(self, *args, **kwargs):
        # initialize our super classes
        xbmcgui.WindowXMLDialog.__init__(self)
        # set addon object
        self.m_addon = kwargs["addon"]
        # set constants
        self._set_constants()

    def onInit(self):
        # set special parameters for controls
        self._set_controls_params()
        # reset scraper from previous work if available
        self._reset_scraper(scraper=self.m_addon.getSetting("editor_scraper"))

    def onAction(self, action):
        # only action is close [action.getButtonCode()]
        if (action in self.ACTION_CLOSE_DIALOG):
            self.close_dialog()

    def onClick(self, controlId):
        # handle <onclick> events
        if (controlId == self.BUTTON_CANCEL):
            self.close_dialog()
        elif (controlId == self.BUTTON_OK):
            self.close_dialog(save=True)
        elif (controlId == self.BUTTON_RESET):
            self._reset_scraper(ask=True, scraper=self.m_addon.getSetting("editor_scraper"))
        elif (controlId == self.BUTTON_OPEN):
            self._open_scraper()
        else:
            # set controls enabled status
            self._enable_controls(controlId)

    def onFocus(self, controlId):
        pass

    def _enable_controls(self, id_=0):
        # only have a valid id if this was sent from onClick(), -1 indicates a forced refresh (e.g. at start)
        if (id_ == -1 or (self.CONTROL_START <= id_ <= self.CONTROL_END)):
            # set 'title' property allows a visual aid for which scraper you're working on
            if (id_ == -1 or self.control_ids[id_] == "['scraper']['title']"):
                cid = [k for k, v in self.control_ids.items() if v == "['scraper']['title']"][0]
                xbmc.executebuiltin("SetProperty(title,{value})".format(value=self.getControl(cid).getText()))
            # set 'string' field to UA of currently selected UA as a visual aid
            if (id_ == -1 or self.control_ids[id_] == "['scraper']['url']['useragent']['title']"):
                cid = [k for k, v in self.control_ids.items() if v == "['scraper']['url']['useragent']['title']"][0]
                self.getControl(cid + 1).setText(self.useragents[self.getControl(cid).getValue()])
            # update user-agents with other value if we edit string
            if (id_ == -1 or self.control_ids[id_] == "['scraper']['url']['useragent']['string']"):
                cid = [k for k, v in self.control_ids.items() if v == "['scraper']['url']['useragent']['title']"][0]
                if (self.getControl(cid).getValue() == self.m_addon.getLocalizedString(30990)):
                    self.useragents.update({self.m_addon.getLocalizedString(30990): self.getControl(cid + 1).getText()})

        # enable other controls
        cid = [k for k, v in self.control_ids.items() if v == "['scraper']['url']['useragent']['string']"][0]
        self.getControl(cid).setEnabled(self.getControl(cid - 1).getValue() == self.m_addon.getLocalizedString(30990))
        cid = [k for k, v in self.control_ids.items() if v == "['scraper']['source']['lyrics']['regex']['flags']"][0]
        self.getControl(cid).setEnabled(self.getControl(cid - 1).getText() != "")
        cid = [k for k, v in self.control_ids.items() if v == "['scraper']['source']['lyrics']['invalid']['flags']"][0]
        self.getControl(cid).setEnabled(self.getControl(cid - 1).getText() != "")
        cid = [k for k, v in self.control_ids.items() if v == "['scraper']['source']['songlist']['regex']['flags']"][0]
        self.getControl(cid).setEnabled(self.getControl(cid - 1).getText() != "")
        cid = [k for k, v in self.control_ids.items() if v == "['scraper']['source']['songlist']['invalid']['flags']"][0]
        self.getControl(cid).setEnabled(self.getControl(cid - 1).getText() != "")

    def _reset_scraper(self, ask=False, scraper="Defaults"):
        # we share a default/reset button, so if ask, ask user which method
        if (ask):
            scraper = [scraper, "Defaults"][self._get_choice()]
        # set user-agents
        self._set_useragents()
        # get defaults from previous scraper if any
        self._get_scraper_values(scraper=scraper)
        # set the current scraper so reset works as expected
        if (scraper != "Defaults"):
            self.m_addon.setSetting("editor_scraper", scraper)

    def _get_choice(self, **kwargs):
        # TODO: universalize this function
        return xbmcgui.Dialog().yesno(
            self.m_addon.getLocalizedString(30900),
            self.m_addon.getLocalizedString(30736),
            self.m_addon.getLocalizedString(30737),
            "",
            self.m_addon.getLocalizedString(30741),
            self.m_addon.getLocalizedString(30742)
        )

    def _set_controls_params(self):
        # we want spinner controls to return the text value not position
        for spinner in [
            "['scraper']['url']['useragent']['title']",
            "['scraper']['url']['song']['groupby']",
            "['scraper']['source']['encoding']",
            "['scraper']['source']['compress']",
            "['scraper']['source']['lyrics']['regex']['flags']",
            "['scraper']['source']['lyrics']['invalid']['flags']",
            "['scraper']['source']['songlist']['format']",
            "['scraper']['source']['songlist']['regex']['flags']",
            "['scraper']['source']['songlist']['invalid']['flags']"
        ]:
            id_ = [k for k, v in self.control_ids.items() if v == spinner][0]
            self.getControl(id_).setType(xbmcgui.SPIN_CONTROL_TYPE_TEXT)

    def _set_constants(self):
        # controls dict() key
        self.control_ids = {
            self.CONTROL_START + 0: "['maintainer']['name']",
            self.CONTROL_START + 1: "['maintainer']['username']",
            self.CONTROL_START + 2: "['maintainer']['email']",
            self.CONTROL_START + 3: "['maintainer']['date']",
            self.CONTROL_START + 4: "['scraper']['title']",
            self.CONTROL_START + 5: "['scraper']['url']['address']",
            self.CONTROL_START + 6: "['scraper']['url']['useragent']['title']",
            self.CONTROL_START + 7: "['scraper']['url']['useragent']['string']",
            self.CONTROL_START + 8: "['scraper']['url']['song']['groupby']",
            self.CONTROL_START + 9: "['scraper']['url']['song']['join']",
            self.CONTROL_START + 10: "['scraper']['url']['song']['space']",
            self.CONTROL_START + 11: "['scraper']['url']['song']['escape']",
            self.CONTROL_START + 12: "['scraper']['url']['song']['clean']",
            self.CONTROL_START + 13: "['scraper']['url']['song']['case']",
            self.CONTROL_START + 14: "['scraper']['url']['song']['search']",
            self.CONTROL_START + 15: "['scraper']['url']['song']['urlencode']",
            self.CONTROL_START + 16: "['scraper']['url']['song']['artist']['head']",
            self.CONTROL_START + 17: "['scraper']['url']['song']['artist']['tail']",
            self.CONTROL_START + 18: "['scraper']['url']['song']['title']['head']",
            self.CONTROL_START + 19: "['scraper']['url']['song']['title']['tail']",
            self.CONTROL_START + 20: "['scraper']['source']['encoding']",
            self.CONTROL_START + 21: "['scraper']['source']['compress']",
            self.CONTROL_START + 22: "['scraper']['source']['lyrics']['lrc']",
            self.CONTROL_START + 23: "['scraper']['source']['lyrics']['clean']",
            self.CONTROL_START + 24: "['scraper']['source']['lyrics']['regex']['exp']",
            self.CONTROL_START + 25: "['scraper']['source']['lyrics']['regex']['flags']",
            self.CONTROL_START + 26: "['scraper']['source']['lyrics']['invalid']['exp']",
            self.CONTROL_START + 27: "['scraper']['source']['lyrics']['invalid']['flags']",
            self.CONTROL_START + 28: "['scraper']['source']['songlist']['format']",
            self.CONTROL_START + 29: "['scraper']['source']['songlist']['always']",
            self.CONTROL_START + 30: "['scraper']['source']['songlist']['autoselect']",
            self.CONTROL_START + 31: "['scraper']['source']['songlist']['regex']['exp']",
            self.CONTROL_START + 32: "['scraper']['source']['songlist']['regex']['flags']",
            self.CONTROL_START + 33: "['scraper']['source']['songlist']['invalid']['exp']",
            self.CONTROL_START + 34: "['scraper']['source']['songlist']['invalid']['flags']",
        }

    def _set_useragents(self):
        # user-agents
        self.useragents = {
            "Chrome":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
            "Firefox": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:15.0) Gecko/20120427 Firefox/15.0a1",
            "Internet Explorer": "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C; .NET4.0E)",
            "Safari": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/534.55.3 (KHTML, like Gecko) Version/5.1.3 Safari/534.53.10",
        }
        # user-agent keys, for sorting purposes we do it this way
        self.useragents_keys = self.useragents.keys()
        self.useragents_keys.sort()
        self.useragents_keys.insert(0, self.m_addon.getLocalizedString(30990))
        self.useragents.update({self.m_addon.getLocalizedString(30990): ""})

    def _set_control_values(self):
        # loop thru and set each controls value
        for id_ in range(self.CONTROL_START, self.CONTROL_END + 1):
            # ControlEdit
            if (isinstance(self.getControl(id_), xbmcgui.ControlEdit)):
                self.getControl(id_).setText(eval("self.scraper{key}".format(key=self.control_ids[id_])))
            # ControlRadioButton
            elif (isinstance(self.getControl(id_), xbmcgui.ControlRadioButton)):
                self.getControl(id_).setSelected(eval("self.scraper{key}".format(key=self.control_ids[id_])))
            # ControlSpinEx
            elif (isinstance(self.getControl(id_), xbmcgui.ControlSpinEx)):
                # set the proper items to pass to _set_spinner()
                if (self.control_ids[id_].endswith("['useragent']['title']")):
                    items = self.useragents_keys
                elif (self.control_ids[id_].endswith("['case']")):
                    items = [self.m_addon.getLocalizedString(30991), "lower", "UPPER", "Title"]
                elif (self.control_ids[id_].endswith("['groupby']")):
                    items = [self.m_addon.getLocalizedString(30991), "Artist [0-9]", "Artist [first letter]", "Artist [0-9] | [first letter]"]
                elif (self.control_ids[id_].endswith("['encoding']")):
                    items = [self.m_addon.getLocalizedString(30992), "UTF-8", "ISO-8859-1"]
                elif (self.control_ids[id_].endswith("['compress']")):
                    items = [self.m_addon.getLocalizedString(30991), "gzip"]
                elif (self.control_ids[id_].endswith("['flags']")):
                    items = [self.m_addon.getLocalizedString(30991), "dotall", "ignorecase", "multiline", "dotall | ignorecase", "dotall | multiline", "dotall | ignorecase | multiline", "ignorecase | multiline"]
                elif (self.control_ids[id_].endswith("['songlist']['format']")):
                    items = ["Title | Url", "Url | Title", "Title | Url | other", "Url | Title | other"]
                # set the spinners values and position
                self._set_spinner(items, id_=id_, selection=eval("self.scraper{key}".format(key=self.control_ids[id_])))
        # this sleep is necessary to give time for get() functions to work properly
        xbmc.sleep(100)
        # enable controls
        self._enable_controls(id_= -1)

    def _set_spinner(self, items, id_, selection):
        # add our items
        self.getControl(id_).addItems(items)
        # now set the correct choice
        self.getControl(id_).setValue(eval("self.scraper{key}".format(key=self.control_ids[id_])))

    def _get_scraper_values(self, scraper="Defaults"):
        # initialize scraper dict
        self.scraper = dict()
        # get values from last preferred scraper
        try:
            # get preferred scraper
            self.scraper = eval(unicode(open(self._set_scraper_path(scraper), "r").read(), "UTF-8"))
        except IOError:
            # TODO: Maybe notify user of failed try with 'Defaults.xpr' (shouldn't happen)
            # try again with 'Defaults.xpr' if not already tried.
            if (scraper != "Defaults"):
                self._get_scraper_values()
        else:
            # set current date
            self.scraper["maintainer"]["date"] = "{0:%Y-%m-%d}".format(datetime.now())
            # set controls
            self._set_control_values()

    def _get_control_values(self):
        # loop thru and get each controls value
        for id_ in range(self.CONTROL_START, self.CONTROL_END + 1):
            # ControlEdit
            if (isinstance(self.getControl(id_), xbmcgui.ControlEdit)):
                value = unicode(self.getControl(id_).getText(), "UTF-8")
            # ControlRadioButton
            elif (isinstance(self.getControl(id_), xbmcgui.ControlRadioButton)):
                value = self.getControl(id_).isSelected()
            # ControlSpinEx
            elif (isinstance(self.getControl(id_), xbmcgui.ControlSpinEx)):
                value = self.getControl(id_).getValue()

            # update dict()
            exec "self.scraper{key} = {value!r}".format(key=self.control_ids[id_], value=value)

    def _set_scraper_path(self, scraper):
        # Loop thru and replace any illegal characters
        scraper = "".join([char for char in scraper if char not in "\\,*=|<>?;:\"+ "])
        # 'Defaults.xpr' is saved in a subfolder so it doesn't get added to valid scraper choices in settings
        subfolder = ["", "default"][scraper == "Defaults"]
        # return full path
        return os.path.join(self.m_addon.getAddonInfo("path"), "resources", "scrapers", subfolder, "{title}.xpr".format(title=scraper)).decode("UTF-8")

    def _save_scraper_file(self):
        try:
            # get our current values
            self._get_control_values()
            # set correct path and clean filename
            path = self._set_scraper_path(self.scraper["scraper"]["title"])
            # save scraper file
            open(path, "w").write(repr(self.scraper))
            # update setting for retaining previous work
            self.m_addon.setSetting("editor_scraper", self.scraper["scraper"]["title"])
        except IOError as error:
            ok = xbmcgui.Dialog().ok(self.m_addon.getLocalizedString(30002), self.m_addon.getLocalizedString(30783).format(file=os.path.basename(path)))

    def _open_scraper(self):
        try:
            # set path to scrapers
            path = os.path.join(self.m_addon.getAddonInfo("path"), "resources", "scrapers").decode("UTF-8")
            # get list of scrapers
            scrapers = [os.path.splitext(s)[0] for s in os.listdir(path) if (s.endswith(".xpr"))]
        except IOError as error:
            #FIXME!!!
            ok = xbmcgui.Dialog().ok(self.m_addon.getLocalizedString(30002), self.m_addon.getLocalizedString(30783).format(file=os.path.basename(path)), error.strerror)
        else:
            # get user selection
            choice = xbmcgui.Dialog().select(self.m_addon.getLocalizedString(30901), scrapers)
            # if not cancelled, load scraper
            if (choice >= 0):
                # Load new scraper info
                self._reset_scraper(scraper=scrapers[choice])

    def close_dialog(self, save=False):
        # only save on OK, but ask if there were changes
        if (save):
            self._save_scraper_file()
        # close dialog
        self.close()
