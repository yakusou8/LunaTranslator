from qtsymbols import *
import gobject, os
import qtawesome, winsharedutils, functools
from myutils.config import globalconfig, _TR
from myutils.utils import get_time_stamp
from gui.usefulwidget import closeashidewindow, WebviewWidget
from gui.dynalang import LAction
from urllib.parse import quote
from myutils.wrapper import threader
from gui.setting_display_text import extrahtml


class wvtranshist(WebviewWidget):
    def scrollend(self):
        self.debugeval("scrollend()")

    def __init__(self, p):
        super().__init__(p)
        self.loadex()
        self.bind("calllunaloadready", self.setflags)
        self.add_menu_noselect(0, _TR("清空"), self.clear)
        self.add_menu_noselect(1, _TR("滚动到最后"), self.scrollend)
        self.add_menu_noselect(2, _TR("字体"), self.seletcfont)
        self.add_menu_noselect(3)
        self.add_menu_noselect(
            4,
            _TR("显示原文"),
            self.showhideraw,
            checkable=True,
            getchecked=lambda: globalconfig["history"]["showorigin"],
        )
        self.add_menu_noselect(
            5,
            _TR("显示翻译"),
            self.showtrans,
            checkable=True,
            getchecked=lambda: globalconfig["history"]["showtrans"],
        )
        self.add_menu_noselect(
            6,
            _TR("显示时间"),
            self.showhidetime,
            checkable=True,
            getchecked=lambda: globalconfig["history"]["showtime"],
        )
        self.add_menu_noselect(7)

        self.add_menu_noselect(
            8,
            _TR("使用Webview2显示"),
            self.useweb,
            True,
            lambda: globalconfig["history"]["usewebview2"],
        )
        self.add_menu_noselect(
            9,
            _TR("附加HTML"),
            functools.partial(
                extrahtml,
                self,
                "extrahtml_transhist",
                r"LunaTranslator\gui\exampleextrahtml.html",
                self,
            ),
        )
        self.add_menu_noselect(10)

        self.add_menu(
            0,
            _TR("查词"),
            threader(
                lambda w: gobject.baseobject.searchwordW.search_word.emit(
                    w.replace("\n", "").strip(), False
                )
            ),
        )
        self.add_menu(1, _TR("翻译"), gobject.baseobject.textgetmethod)
        self.add_menu(2, _TR("朗读"), gobject.baseobject.read_text)
        self.add_menu(3)

    def loadex(self, extra=None):
        if not extra:
            extra = self.loadextra()
            extra = extra if extra else ""
        with open(
            r"LunaTranslator\gui\transhistwebview.html", "r", encoding="utf8"
        ) as ff:
            html = ff.read().replace("__PLACEHOLDER_EXTRA_HTML_", extra)
        with open(
            r"LunaTranslator\gui\transhistwebview_parsed.html", "w", encoding="utf8"
        ) as ff:
            ff.write(html)
        self.navigate(
            os.path.abspath(r"LunaTranslator\gui\transhistwebview_parsed.html")
        )

    def loadextra(self):
        for _ in [
            "userconfig/extrahtml_transhist.html",
            r"LunaTranslator\gui\exampleextrahtml.html",
        ]:
            if not os.path.exists(_):
                continue
            with open(_, "r", encoding="utf8") as ff:
                return ff.read()

    def seletcfont(self):
        f = QFont()
        cur = globalconfig.get("histfont")
        if cur:
            f.fromString(cur)
        font, ok = QFontDialog.getFont(f, self)
        if ok:
            _s = font.toString()
            globalconfig["histfont"] = _s
            self.setf()

    def setf(self):
        key = "histfont"
        fontstring = globalconfig.get(key, "")
        if fontstring:
            _f = QFont()
            _f.fromString(fontstring)
            _style = "font-size:{}pt;".format(_f.pointSize())
            _style += 'font-family:"{}";'.format(_f.family())
            self.debugeval("setfont('body{{{}}}')".format(quote(_style)))

    def useweb(self):
        globalconfig["history"]["usewebview2"] = not globalconfig["history"][
            "usewebview2"
        ]
        self.parent().loadviewer()

    def showhideraw(self):
        globalconfig["history"]["showorigin"] = not globalconfig["history"][
            "showorigin"
        ]
        self.debugeval(
            "showhideorigin({})".format(int(globalconfig["history"]["showorigin"]))
        )

    def showtrans(self):
        globalconfig["history"]["showtrans"] = not globalconfig["history"]["showtrans"]
        self.debugeval(
            "showhidetrans({})".format(int(globalconfig["history"]["showtrans"]))
        )

    def showhidetime(self):
        globalconfig["history"]["showtime"] = not globalconfig["history"]["showtime"]
        self.debugeval(
            "showhidetime({})".format(int(globalconfig["history"]["showtime"]))
        )

    def setflags(self):
        self.debugeval(
            "showhideorigin({})".format(int(globalconfig["history"]["showorigin"]))
        )
        self.debugeval(
            "showhidetrans({})".format(int(globalconfig["history"]["showtrans"]))
        )
        self.debugeval(
            "showhidetime({})".format(int(globalconfig["history"]["showtime"]))
        )
        self.setf()
        self.refresh()

    def clear(self, _=None):
        self.debugeval("clear()")
        self.parent().trace.clear()

    def refresh(self):
        seted = False
        for i, line in enumerate(self.parent().trace):
            if seted and (len(line[1]) == 2):
                self.addbr()
            self.visline(line)

    def visline(self, line):
        ii, _ = line
        if ii == 0:
            self.getnewsentence(line)
        elif ii == 1:
            self.getnewtrans(line)

    def addbr(self):
        self.debugeval("addbr();")

    def getnewsentence(self, sentence):
        self.addbr()
        sentence = sentence[1]
        self.debugeval(
            'getnewsentence("{}","{}");'.format(
                quote(sentence[0] + " "), quote(sentence[1])
            )
        )

    def getnewtrans(self, sentence):
        sentence = sentence[1]
        self.debugeval(
            'getnewtrans("{}","{}","{}");'.format(
                quote(sentence[0] + " "), quote(sentence[1] + " "), quote(sentence[2])
            )
        )

    def debugeval(self, js):
        # print(js)
        self.eval(js)


class Qtranshist(QPlainTextEdit):
    def __init__(self, p):
        super().__init__(p)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showmenu)
        self.setUndoRedoEnabled(False)
        self.setReadOnly(True)
        self.setf()
        self.refresh()

    def showmenu(self, _):
        menu = QMenu(self)
        qingkong = LAction("清空", menu)
        baocun = LAction("保存", menu)
        tts = LAction("朗读", menu)
        copy = LAction("复制", menu)
        hideshowraw = LAction("显示原文", menu)
        hideshowraw.setCheckable(True)
        hideshowraw.setChecked(globalconfig["history"]["showorigin"])
        hideshowtrans = LAction("显示翻译", menu)
        hideshowtrans.setCheckable(True)
        hideshowtrans.setChecked(globalconfig["history"]["showtrans"])
        hidetime = LAction("显示时间", menu)
        hidetime.setCheckable(True)
        hidetime.setChecked(globalconfig["history"]["showtime"])
        scrolltoend = LAction("滚动到最后", menu)
        font = LAction("字体", menu)
        search = LAction("查词", menu)
        translate = LAction("翻译", menu)
        webview2qt = LAction("使用Webview2显示", menu)
        webview2qt.setCheckable(True)
        webview2qt.setChecked(globalconfig["history"]["usewebview2"])
        if len(self.textCursor().selectedText()):
            menu.addAction(copy)
            menu.addAction(search)
            menu.addAction(translate)
            menu.addAction(tts)
        else:
            menu.addAction(qingkong)
            menu.addAction(baocun)
            menu.addAction(scrolltoend)
            menu.addAction(font)
            menu.addSeparator()
            menu.addAction(hideshowraw)
            menu.addAction(hideshowtrans)
            menu.addAction(hidetime)
            menu.addSeparator()
            menu.addAction(webview2qt)

        action = menu.exec(QCursor.pos())
        if action == qingkong:
            self.clear()
            self.parent().trace.clear()
        elif action == webview2qt:
            globalconfig["history"]["usewebview2"] = not globalconfig["history"][
                "usewebview2"
            ]
            self.parent().loadviewer()
        elif action == search:
            gobject.baseobject.searchwordW.search_word.emit(
                self.textCursor().selectedText(), False
            )
        elif action == translate:
            gobject.baseobject.textgetmethod(self.textCursor().selectedText(), False)
        elif action == tts:
            gobject.baseobject.read_text(self.textCursor().selectedText())
        elif action == copy:
            winsharedutils.clipboard_set(self.textCursor().selectedText())
        elif action == baocun:
            ff = QFileDialog.getSaveFileName(self, directory="save.txt")
            if ff[0] == "":
                return
            with open(ff[0], "w", encoding="utf8") as ff:
                ff.write(self.toPlainText())
        elif action == font:
            f = QFont()
            cur = globalconfig.get("histfont")
            if cur:
                f.fromString(cur)
            font, ok = QFontDialog.getFont(f, self)
            if ok:
                _s = font.toString()
                globalconfig["histfont"] = _s
                self.setf()
        elif action == hideshowtrans:
            globalconfig["history"]["showtrans"] = not globalconfig["history"][
                "showtrans"
            ]
            self.refresh()
        elif action == hideshowraw:
            globalconfig["history"]["showorigin"] = not globalconfig["history"][
                "showorigin"
            ]
            self.refresh()
        elif action == hidetime:
            globalconfig["history"]["showtime"] = not globalconfig["history"][
                "showtime"
            ]
            self.refresh()
        elif action == scrolltoend:
            scrollbar = self.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())

    def setf(self):
        key = "histfont"
        fontstring = globalconfig.get(key, "")
        if fontstring:
            _f = QFont()
            _f.fromString(fontstring)
            _style = "font-size:{}pt;".format(_f.pointSize())
            _style += 'font-family:"{}";'.format(_f.family())
            self.setStyleSheet(_style)

    def refresh(self):
        collect = ""
        seted = False
        for i, line in enumerate(self.parent().trace):
            if seted and (len(line[1]) == 2):
                collect += "\n"
                seted = True
            line = self.visline(line)
            if line:
                if seted:
                    collect += "\n"
                collect += line
                seted = True
        self.setPlainText(collect)

    def visline(self, line):
        ii, line = line
        if ii == 0:
            tm, sentence = line
            if not globalconfig["history"]["showorigin"]:
                return
            else:
                if globalconfig["history"]["showtime"]:
                    sentence = tm + " " + sentence
                return sentence
        elif ii == 1:
            tm, api, sentence = line
            if not globalconfig["history"]["showtrans"]:
                return
            sentence = api + " " + sentence
            if globalconfig["history"]["showtime"]:
                sentence = tm + " " + sentence
            return sentence

    def getnewsentence(self, sentence):
        self.appendPlainText("")
        line = self.visline(sentence)
        if line:
            self.appendPlainText(line)

    def getnewtrans(self, sentence):
        line = self.visline(sentence)
        if line:
            self.appendPlainText(line)


class transhist(closeashidewindow):

    getnewsentencesignal = pyqtSignal(str)
    getnewtranssignal = pyqtSignal(str, str)

    def __init__(self, parent):
        super(transhist, self).__init__(parent, globalconfig["hist_geo"])
        self.trace = []
        self.textOutput = None
        self.setupUi()
        # self.setWindowFlags(self.windowFlags()&~Qt.WindowMinimizeButtonHint)
        self.getnewsentencesignal.connect(self.getnewsentence)
        self.getnewtranssignal.connect(self.getnewtrans)
        self.setWindowTitle("历史文本")

    def setupUi(self):
        self.setWindowIcon(qtawesome.icon("fa.rotate-left"))
        self.loadviewer()

    def getnewsentence(self, sentence):
        tm = get_time_stamp()
        self.trace.append((0, (tm, sentence)))
        self.textOutput.getnewsentence(self.trace[-1])

    def getnewtrans(self, api, sentence):
        tm = get_time_stamp()
        self.trace.append((1, (tm, api, sentence)))
        self.textOutput.getnewtrans(self.trace[-1])

    def loadviewer(self):
        if self.textOutput:
            self.textOutput.hide()
            self.textOutput.deleteLater()
        if globalconfig["history"]["usewebview2"]:
            self.textOutput = wvtranshist(self)
        else:
            self.textOutput = Qtranshist(self)
        self.setCentralWidget(self.textOutput)
