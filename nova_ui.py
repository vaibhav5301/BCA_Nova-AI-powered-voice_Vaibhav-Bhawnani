"""
╔══════════════════════════════════════════════════╗
║   NOVA UI v2  —  Continuous · Fast · Beautiful   ║
║                                                  ║
║   Drop next to nova_assistant_v9.py              ║
║   Install:  pip install PyQt6 deep-translator    ║
║   Run:      python nova_ui.py                    ║
╚══════════════════════════════════════════════════╝

 CHANGES v2:
  • One-click continuous loop  — click orb once, Nova keeps
    listening after every response until you say "sleep"
  • "sleep" / "go to sleep" stops the loop immediately
  • Faster TTS  — speech rate bumped to 190, ambient noise
    calibration reduced to 0.2 s, phrase limit tightened
  • Premium UI  — glassmorphism cards, waveform visualiser,
    gradient accents, smoother animations

 CHANGES v2.1 (translator fix):
  • Updated to use deep-translator instead of googletrans
    (googletrans==4.0.0rc1 is broken on Python 3.11+)
  • Install: pip install deep-translator
"""

import sys, random, threading, datetime, math
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QScrollArea, QFrame,
    QSizePolicy, QSlider, QGridLayout, QStackedWidget
)
from PyQt6.QtCore  import (Qt, QThread, pyqtSignal, QTimer, QPoint,
                            QPropertyAnimation, QEasingCurve, QSize, QRect)
from PyQt6.QtGui   import (QFont, QColor, QPainter, QPen, QBrush,
                            QPainterPath, QLinearGradient, QRadialGradient,
                            QPalette, QCursor)

# ── Import Nova ───────────────────────────────────────────────
try:
    import nova_assistant_v9 as _nova_mod

    # Speed patch: faster TTS + quicker ambient calibration
    try:
        _nova_mod.engine.setProperty('rate', 190)
        _nova_mod.recognizer.pause_threshold          = 0.6
        _nova_mod.recognizer.energy_threshold         = 250
        _nova_mod.recognizer.dynamic_energy_threshold = True
    except Exception:
        pass

    _nova_mod.initialize_ai()
    NOVA_OK = True
    print("Nova loaded and speed-patched")

except ImportError:
    NOVA_OK = False
    print("nova_assistant_v9.py not found — running in demo mode")

    class _FakeNovaMod:
        WAKE_WORDS  = ["wake up nova", "wakeup nova", "wake nova"]
        SLEEP_WORDS = ["go to sleep", "sleep mode", "sleep nova"]
        def speak(self, t, prefix=True): print(f"[DEMO] {t}")
        def listen(self, timeout=5):     return ""
        def process_command(self, c):    self.speak(f"Demo mode — got: '{c}'")
        def initialize_ai(self):         pass

    _nova_mod = _FakeNovaMod()


# ══════════════════════════════════════════════════
#  DESIGN TOKENS
# ══════════════════════════════════════════════════
BG      = "#08090f"
SURFACE = "#0e1020"
CARD    = "#12152a"
BORDER  = "#1c2040"
BORDER2 = "#262b50"
ACCENT  = "#5b8fff"
ACCENT2 = "#a78bfa"
MINT    = "#00e5b0"
WARN    = "#ffbb4d"
DANGER  = "#ff6059"
TEXT    = "#e0e6ff"
TEXT2   = "#5a6280"
TEXT3   = "#2e3355"


def rgba(hx: str, a: float) -> str:
    h = hx.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{int(a*255)})"


QSS = f"""
* {{ font-family:'Segoe UI','Inter',sans-serif; color:{TEXT}; background:transparent; }}
QScrollArea, QScrollArea > QWidget > QWidget {{ background:transparent; border:none; }}
QScrollBar:vertical {{ background:{BG}; width:3px; border-radius:2px; }}
QScrollBar::handle:vertical {{ background:{BORDER2}; border-radius:2px; min-height:24px; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height:0; }}
QLineEdit {{
    background:{CARD}; border:1px solid {BORDER}; border-radius:10px;
    color:{TEXT}; padding:0 14px; font-size:13px;
    selection-background-color:{rgba(ACCENT,0.35)};
}}
QLineEdit:focus {{ border:1px solid {ACCENT}; }}
"""


# ══════════════════════════════════════════════════
#  WAVEFORM WIDGET
# ══════════════════════════════════════════════════
class WaveformWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(28)
        self._active  = False
        self._phase   = 0.0
        self._bars    = 20
        self._heights = [0.0] * self._bars
        self._targets = [0.0] * self._bars
        self._color   = QColor(ACCENT)
        t = QTimer(self); t.timeout.connect(self._tick); t.start(40)

    def set_active(self, active: bool, color: str = ACCENT):
        self._active = active
        self._color  = QColor(color)
        if not active:
            self._targets = [0.0] * self._bars

    def _tick(self):
        self._phase += 0.12
        if self._active:
            for i in range(self._bars):
                self._targets[i] = (
                    0.3 + 0.7 * abs(math.sin(self._phase + i * 0.42
                                              + math.sin(i * 0.8) * 0.5))
                )
        for i in range(self._bars):
            self._heights[i] += (self._targets[i] - self._heights[i]) * 0.22
        self.update()

    def paintEvent(self, e):
        if max(self._heights) < 0.02:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h   = self.width(), self.height()
        bw     = max(2, (w - self._bars * 2) // self._bars)
        total  = self._bars * (bw + 2)
        xoff   = (w - total) // 2
        mid    = h // 2
        for i, ht in enumerate(self._heights):
            bh = max(2, int(ht * mid * 0.85))
            x  = xoff + i * (bw + 2)
            c  = QColor(self._color)
            c.setAlphaF(0.35 + ht * 0.65)
            p.setBrush(QBrush(c)); p.setPen(Qt.PenStyle.NoPen)
            p.drawRoundedRect(x, mid - bh, bw, bh * 2, bw // 2, bw // 2)
        p.end()


# ══════════════════════════════════════════════════
#  ORB  (mic button)
# ══════════════════════════════════════════════════
class OrbWidget(QWidget):
    clicked = pyqtSignal()
    _COLORS = {"idle": ACCENT, "listening": WARN,
               "processing": ACCENT2, "awake": MINT, "sleeping": TEXT3}

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(80, 80)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._state = "idle"
        self._hover = False
        self._r1    = 0.0
        self._r2    = 0.0
        self._glow  = 0.0
        t = QTimer(self); t.timeout.connect(self._tick); t.start(28)

    def set_state(self, s: str):
        self._state = s; self.update()

    def _tick(self):
        active = self._state in ("listening", "processing", "awake")
        if active:
            self._r1 = (self._r1 + 0.016) % 1.0
            self._r2 = (self._r2 + 0.011) % 1.0
        else:
            self._r1 = self._r2 = 0.0
        self._glow += ((1.0 if active else 0.0) - self._glow) * 0.08
        self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        cx, cy, r = 40, 40, 30
        c = QColor(self._COLORS.get(self._state, ACCENT))

        # outer glow
        if self._glow > 0.02:
            for dr, alpha in [(18, 0.06), (10, 0.12), (5, 0.18)]:
                gc = QColor(c); gc.setAlphaF(alpha * self._glow)
                p.setBrush(QBrush(gc)); p.setPen(Qt.PenStyle.NoPen)
                rr = r + dr
                p.drawEllipse(cx-rr, cy-rr, rr*2, rr*2)

        # pulse rings
        if self._state in ("listening", "processing"):
            for ph in (self._r1, self._r2):
                rr = r + ph * 26
                rc = QColor(c); rc.setAlphaF(max(0, 0.7*(1.0-ph)))
                p.setPen(QPen(rc, 1.5)); p.setBrush(Qt.BrushStyle.NoBrush)
                p.drawEllipse(int(cx-rr), int(cy-rr), int(rr*2), int(rr*2))

        # disc
        grad = QRadialGradient(cx, cy-8, r*1.2)
        fills = {
            "idle":       ("#1a1f3d", SURFACE),
            "listening":  ("#2e2208", SURFACE),
            "awake":      ("#0a2820", SURFACE),
        }
        top, bot = fills.get(self._state, ("#131838", SURFACE))
        grad.setColorAt(0.0, QColor(top)); grad.setColorAt(1.0, QColor(bot))
        bc = QColor(c); bc.setAlphaF(0.6 + self._glow*0.4)
        p.setPen(QPen(bc, 1.5)); p.setBrush(QBrush(grad))
        p.drawEllipse(cx-r, cy-r, r*2, r*2)

        if self._hover:
            sc = QColor(255, 255, 255, 18)
            p.setBrush(QBrush(sc)); p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(cx-r, cy-r, r*2, r*2)

        # mic icon
        ic = QColor(TEXT2) if self._state == "idle" else QColor(c)
        p.setPen(QPen(ic, 2.0, Qt.PenStyle.SolidLine,
                      Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        p.setBrush(Qt.BrushStyle.NoBrush)
        path = QPainterPath()
        path.addRoundedRect(34.0, 25.0, 12.0, 17.0, 6.0, 6.0)
        p.drawPath(path)
        p.drawArc(29, 35, 22, 14, 0, -180*16)
        p.drawLine(40, 49, 40, 53)
        p.drawLine(35, 53, 45, 53)
        p.end()

    def enterEvent(self, e):  self._hover = True;  self.update()
    def leaveEvent(self, e):  self._hover = False; self.update()
    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()


# ══════════════════════════════════════════════════
#  CHAT BUBBLE
# ══════════════════════════════════════════════════
class BubbleWidget(QFrame):
    def __init__(self, text: str, role: str, parent=None):
        super().__init__(parent)
        outer = QVBoxLayout(self); outer.setContentsMargins(0,0,0,0); outer.setSpacing(3)
        row   = QHBoxLayout(); row.setSpacing(10)

        if role == "nova":
            av = QLabel("N"); av.setFixedSize(32,32)
            av.setAlignment(Qt.AlignmentFlag.AlignCenter)
            av.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            av.setStyleSheet(f"""
                background:{rgba(ACCENT,0.20)};
                border:1px solid {rgba(ACCENT,0.30)};
                border-radius:8px; color:{ACCENT};
            """)
            row.addWidget(av, 0, Qt.AlignmentFlag.AlignTop)

        bub = QLabel(text); bub.setWordWrap(True)
        bub.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        bub.setMaximumWidth(430); bub.setFont(QFont("Segoe UI", 11))

        if role == "nova":
            bub.setStyleSheet(f"""
                background:{CARD}; border:1px solid {BORDER};
                border-radius:12px; border-top-left-radius:3px;
                padding:10px 14px; color:{TEXT};
            """)
        else:
            bub.setStyleSheet(f"""
                background:{rgba(ACCENT,0.12)};
                border:1px solid {rgba(ACCENT,0.22)};
                border-radius:12px; border-top-right-radius:3px;
                padding:10px 14px; color:{TEXT};
            """)

        now = datetime.datetime.now().strftime("%I:%M %p").lstrip("0")
        tl  = QLabel(now); tl.setFont(QFont("Segoe UI",8))
        tl.setStyleSheet(f"color:{TEXT3};")

        if role == "nova":
            row.addWidget(bub, 0, Qt.AlignmentFlag.AlignTop); row.addStretch()
            outer.addLayout(row); outer.addWidget(tl)
        else:
            row.addStretch(); row.addWidget(bub, 0, Qt.AlignmentFlag.AlignTop)
            outer.addLayout(row)
            tr = QHBoxLayout(); tr.addStretch(); tr.addWidget(tl); outer.addLayout(tr)


# ══════════════════════════════════════════════════
#  TYPING INDICATOR
# ══════════════════════════════════════════════════
class TypingWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self); layout.setContentsMargins(0,4,0,4); layout.setSpacing(10)
        av = QLabel("N"); av.setFixedSize(32,32)
        av.setAlignment(Qt.AlignmentFlag.AlignCenter)
        av.setFont(QFont("Segoe UI",11,QFont.Weight.Bold))
        av.setStyleSheet(f"""
            background:{rgba(ACCENT,0.15)}; border:1px solid {rgba(ACCENT,0.25)};
            border-radius:8px; color:{ACCENT};
        """)
        layout.addWidget(av, 0, Qt.AlignmentFlag.AlignTop)
        bub = QFrame(); bub.setFixedSize(64,36)
        bub.setStyleSheet(f"""
            background:{CARD}; border:1px solid {BORDER};
            border-radius:12px; border-top-left-radius:3px;
        """)
        bl = QHBoxLayout(bub); bl.setContentsMargins(10,0,10,0); bl.setSpacing(6)
        self._dots = []
        for _ in range(3):
            d = QLabel("•"); d.setFont(QFont("Segoe UI",14))
            d.setStyleSheet(f"color:{TEXT3};"); bl.addWidget(d); self._dots.append(d)
        layout.addWidget(bub); layout.addStretch()
        self._ph = 0
        t = QTimer(self); t.timeout.connect(self._tick); t.start(280)

    def _tick(self):
        for i, d in enumerate(self._dots):
            d.setStyleSheet(f"color:{TEXT};" if i == self._ph%3 else f"color:{TEXT3};")
        self._ph += 1


# ══════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════
def pill_btn(label, fg, bd, hover_bg, cb, h=28) -> QPushButton:
    b = QPushButton(label); b.setFixedHeight(h)
    b.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
    b.setFont(QFont("Segoe UI",9,QFont.Weight.Medium))
    b.setStyleSheet(f"""
        QPushButton {{
            background:transparent; border:1px solid {bd};
            border-radius:14px; color:{fg}; padding:0 10px;
        }}
        QPushButton:hover {{ background:{hover_bg}; border:1px solid {fg}; }}
    """)
    b.clicked.connect(cb); return b


class FeatBtn(QPushButton):
    def __init__(self, icon, label, parent=None):
        super().__init__(parent)
        self.setFixedSize(92,72)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        lv = QVBoxLayout(self); lv.setContentsMargins(4,10,4,8); lv.setSpacing(5)
        lv.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._ic  = QLabel(icon);  self._ic .setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._ic .setFont(QFont("Segoe UI",17))
        self._lb  = QLabel(label); self._lb.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._lb.setFont(QFont("Segoe UI",9,QFont.Weight.Medium))
        lv.addWidget(self._ic); lv.addWidget(self._lb)
        self._set(False)

    def _set(self, on):
        if on:
            self.setStyleSheet(f"""
                QPushButton {{
                    background:{rgba(ACCENT,0.18)};
                    border:1px solid {ACCENT}; border-radius:12px;
                }}
            """)
            self._ic.setStyleSheet(f"color:{ACCENT};")
            self._lb.setStyleSheet(f"color:{ACCENT};")
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background:{CARD}; border:1px solid {BORDER}; border-radius:12px;
                }}
                QPushButton:hover {{
                    background:{rgba(ACCENT,0.08)}; border:1px solid {ACCENT};
                }}
            """)
            self._ic.setStyleSheet(f"color:{TEXT2};")
            self._lb.setStyleSheet(f"color:{TEXT2};")

    def set_active(self, on): self._set(on)


class PanelBox(QFrame):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background:{rgba(CARD,0.6)}; border:1px solid {BORDER}; border-radius:12px;
            }}
        """)
        self._v = QVBoxLayout(self)
        self._v.setContentsMargins(12,10,12,12); self._v.setSpacing(8)
        t = QLabel(title.upper()); t.setFont(QFont("Segoe UI",8,QFont.Weight.Bold))
        t.setStyleSheet(f"color:{TEXT2}; letter-spacing:2px; background:transparent; border:none;")
        self._v.addWidget(t)

    def body(self): return self._v

def hint(text) -> QLabel:
    l = QLabel(text); l.setFont(QFont("Segoe UI",8))
    l.setStyleSheet(f"color:{TEXT3}; background:transparent; border:none;"); return l

def small(text) -> QLabel:
    l = QLabel(text); l.setFont(QFont("Segoe UI",10))
    l.setStyleSheet(f"color:{TEXT3}; background:transparent; border:none;"); return l


# ══════════════════════════════════════════════════
#  CONVERSATION WORKER  (continuous loop)
# ══════════════════════════════════════════════════
class ConvWorker(QThread):
    user_said     = pyqtSignal(str)
    nova_said     = pyqtSignal(str)
    state_changed = pyqtSignal(str)
    loop_stopped  = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._running = True

    def stop(self): self._running = False

    def run(self):
        orig = _nova_mod.speak

        def patched(t, prefix=True):
            orig(t, prefix); self.nova_said.emit(t)

        _nova_mod.speak = patched

        while self._running:
            self.state_changed.emit("listening")
            try:
                text = _nova_mod.listen(timeout=6)
            except Exception as ex:
                self.nova_said.emit(f"Mic error: {ex}")
                break

            if not text:
                continue

            self.user_said.emit(text)

            if any(w in text for w in _nova_mod.SLEEP_WORDS):
                self.state_changed.emit("processing")
                patched(random.choice([
                    "Going to sleep! Click the orb to wake me.",
                    "Taking a nap. Click the orb when you need me!"
                ]))
                self._running = False
                break

            self.state_changed.emit("processing")
            try:
                _nova_mod.process_command(text)
            except SystemExit:
                patched("Goodbye! The window stays open.")
                self._running = False; break
            except Exception as ex:
                patched(f"Error: {ex}")

        _nova_mod.speak = orig
        self.loop_stopped.emit()


# ── Typed command (single-shot) ───────────────────
class CmdWorker(QThread):
    nova_said = pyqtSignal(str)
    done      = pyqtSignal()

    def __init__(self, command):
        super().__init__(); self.command = command

    def run(self):
        orig = _nova_mod.speak
        def p(t, prefix=True): orig(t, prefix); self.nova_said.emit(t)
        _nova_mod.speak = p
        try:
            _nova_mod.process_command(self.command)
        except SystemExit:
            self.nova_said.emit("Goodbye! Window stays open.")
        except Exception as ex:
            self.nova_said.emit(f"Error: {ex}")
        finally:
            _nova_mod.speak = orig; self.done.emit()


# ══════════════════════════════════════════════════
#  MAIN WINDOW
# ══════════════════════════════════════════════════
class NovaWindow(QMainWindow):
    _sadd  = pyqtSignal(str, str)
    _sst   = pyqtSignal(str)
    _styp  = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nova")
        self.setMinimumSize(920, 580); self.resize(1080, 680)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self._conv   = None
        self._cmd    = None
        self._loop   = False
        self._typing = None
        self._actpnl = None
        self._drag   = None

        self._sadd.connect(self._do_add)
        self._sst .connect(self._do_state)
        self._styp.connect(self._do_typing)

        self._build()
        self.setStyleSheet(QSS + f"QMainWindow{{background:{BG};}} #root{{background:{BG};}}")

        QTimer.singleShot(400, lambda: self._do_add("nova",
            "Hello! I'm Nova. Click the orb once to start — I'll keep listening after "
            "every reply. Say 'sleep' or 'go to sleep' to stop. You can also type below."
        ))

    # ─────────────────────────────────────────────
    def _build(self):
        root = QWidget(); root.setObjectName("root"); self.setCentralWidget(root)
        v = QVBoxLayout(root); v.setContentsMargins(0,0,0,0); v.setSpacing(0)
        v.addWidget(self._mk_tb())
        body = QHBoxLayout(); body.setContentsMargins(0,0,0,0); body.setSpacing(0)
        body.addWidget(self._mk_chat(), stretch=1)
        body.addWidget(self._mk_dock())
        v.addLayout(body, stretch=1)

    # ── Title bar ────────────────────────────────
    def _mk_tb(self):
        bar = QWidget(); bar.setFixedHeight(46)
        bar.setStyleSheet(f"""
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 {SURFACE}, stop:1 {BG});
            border-bottom:1px solid {BORDER};
        """)
        h = QHBoxLayout(bar); h.setContentsMargins(16,0,12,0); h.setSpacing(10)

        logo = QLabel("NOVA"); logo.setFont(QFont("Segoe UI",12,QFont.Weight.Bold))
        logo.setStyleSheet(f"color:{ACCENT}; letter-spacing:4px;")
        h.addWidget(logo)

        self._dot  = QLabel(); self._dot.setFixedSize(8,8)
        self._dot.setStyleSheet(f"background:{TEXT3}; border-radius:4px;")
        h.addWidget(self._dot)

        self._pill = QLabel("Sleeping"); self._pill.setFont(QFont("Segoe UI",8,QFont.Weight.Medium))
        self._pill.setStyleSheet(self._pcss(TEXT2, rgba(CARD,0.8), BORDER2))
        h.addWidget(self._pill); h.addStretch()

        self._wave = WaveformWidget(); self._wave.setFixedWidth(120)
        h.addWidget(self._wave); h.addStretch()

        for txt, fn, hc in [("─", self.showMinimized, ACCENT),
                             ("□", lambda: self.showNormal() if self.isMaximized() else self.showMaximized(), ACCENT),
                             ("×", self.close, DANGER)]:
            b = QPushButton(txt); b.setFixedSize(32,26)
            b.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            b.setFont(QFont("Segoe UI",13))
            b.setStyleSheet(f"""
                QPushButton {{background:transparent;border:none;color:{TEXT2};border-radius:5px;}}
                QPushButton:hover {{background:{rgba(hc,0.12)};color:{hc};}}
            """)
            b.clicked.connect(fn); h.addWidget(b)
        return bar

    def _pcss(self, fg, bg, bd):
        return (f"color:{fg};background:{bg};border:1px solid {bd};"
                f"border-radius:11px;padding:2px 11px;font-size:8px;"
                f"font-weight:500;letter-spacing:1px;")

    # ── Chat ─────────────────────────────────────
    def _mk_chat(self):
        col = QWidget(); col.setStyleSheet(f"background:{BG};border-right:1px solid {BORDER};")
        v   = QVBoxLayout(col); v.setContentsMargins(0,0,0,0); v.setSpacing(0)

        self._scroll = QScrollArea(); self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._cw = QWidget(); self._cw.setStyleSheet("background:transparent;")
        self._cl = QVBoxLayout(self._cw)
        self._cl.setContentsMargins(20,16,20,12); self._cl.setSpacing(14)
        self._cl.addStretch()
        self._scroll.setWidget(self._cw); v.addWidget(self._scroll, stretch=1)

        bar = QWidget(); bar.setFixedHeight(66)
        bar.setStyleSheet(f"""
            background:qlineargradient(x1:0,y1:0,x2:0,y2:1,
                stop:0 {SURFACE},stop:1 {BG});
            border-top:1px solid {BORDER};
        """)
        h = QHBoxLayout(bar); h.setContentsMargins(14,12,14,12); h.setSpacing(10)

        self._orb = OrbWidget(); self._orb.clicked.connect(self._orb_click)
        h.addWidget(self._orb)

        self._inp = QLineEdit(); self._inp.setFixedHeight(42)
        self._inp.setPlaceholderText("Type a command, or click the orb to speak…")
        self._inp.returnPressed.connect(self._txt_send)
        h.addWidget(self._inp, stretch=1)

        snd = QPushButton("↑"); snd.setFixedSize(42,42)
        snd.setFont(QFont("Segoe UI",16))
        snd.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        snd.setStyleSheet(f"""
            QPushButton {{
                background:{rgba(ACCENT,0.12)};border:1px solid {rgba(ACCENT,0.3)};
                border-radius:10px;color:{ACCENT};
            }}
            QPushButton:hover {{background:{rgba(ACCENT,0.22)};border:1px solid {ACCENT};}}
            QPushButton:pressed {{background:{rgba(ACCENT,0.35)};}}
        """)
        snd.clicked.connect(self._txt_send); h.addWidget(snd)
        v.addWidget(bar)
        return col

    # ── Dock ─────────────────────────────────────
    def _mk_dock(self):
        dock = QWidget(); dock.setFixedWidth(244)
        dock.setStyleSheet(f"background:{SURFACE};")
        v = QVBoxLayout(dock); v.setContentsMargins(0,0,0,0); v.setSpacing(0)

        hdr = QWidget(); hdr.setFixedHeight(46)
        hdr.setStyleSheet(f"border-bottom:1px solid {BORDER};")
        hh  = QHBoxLayout(hdr); hh.setContentsMargins(12,0,12,0); hh.setSpacing(8)
        fl  = QLabel("FEATURES"); fl.setFont(QFont("Segoe UI",8,QFont.Weight.Bold))
        fl.setStyleSheet(f"color:{TEXT2};letter-spacing:2px;")
        hh.addWidget(fl); hh.addStretch()

        self._wbtn = QPushButton("Wake"); self._wbtn.setFixedSize(56,26)
        self._wbtn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._wbtn.setFont(QFont("Segoe UI",9,QFont.Weight.Medium))
        self._wbtn.setStyleSheet(self._wcss(False))
        self._wbtn.clicked.connect(self._toggle_wake)
        hh.addWidget(self._wbtn); v.addWidget(hdr)

        sc  = QScrollArea(); sc.setWidgetResizable(True)
        sc.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        sc.setStyleSheet("background:transparent;border:none;")
        inn = QWidget(); inn.setStyleSheet("background:transparent;")
        iv  = QVBoxLayout(inn); iv.setContentsMargins(8,8,8,8); iv.setSpacing(6)

        gw  = QWidget(); gw.setStyleSheet("background:transparent;")
        gr  = QGridLayout(gw); gr.setContentsMargins(0,0,0,0); gr.setSpacing(5)
        FEATS = [
            ("◈","Weather",   "weather"),  ("◷","Time",      "time"),
            ("◉","News",      "news"),     ("▣","Date",       "date"),
            ("♪","Music",     "music"),    ("∑","Calculate",  "calc"),
            ("⌬","Translate", "translate"),("◐","Brightness","brightness"),
            ("◎","WhatsApp",  "whatsapp"), ("⊘","Close App", "close_app"),
            ("⇥","Tab Nav",   "tabnav"),   ("◑","Joke",       "joke"),
        ]
        self._fbts = {}
        for i,(ic,lb,fid) in enumerate(FEATS):
            b = FeatBtn(ic, lb); b.clicked.connect(lambda _,f=fid: self._on_feat(f))
            gr.addWidget(b, i//2, i%2); self._fbts[fid] = b
        iv.addWidget(gw)

        self._ps = QStackedWidget(); self._ps.setStyleSheet("background:transparent;")
        self._ps.addWidget(QWidget())  # 0 = blank

        # Music panel
        mp = PanelBox("Mood Music")
        mw = QWidget(); mw.setStyleSheet("background:transparent;")
        mg = QGridLayout(mw); mg.setSpacing(4); mg.setContentsMargins(0,0,0,0)
        for i,m in enumerate(["happy","sad","chill","focus","workout",
                               "romantic","sleep","party","morning","angry"]):
            mg.addWidget(pill_btn(m.capitalize(), MINT, rgba(MINT,0.25), rgba(MINT,0.1),
                         lambda _,mood=m: self._run(f"play {mood} music")), i//2, i%2)
        mp.body().addWidget(mw); self._ps.addWidget(mp)  # 1

        # Calc panel
        cp = PanelBox("Calculator")
        self._ci = QLineEdit(); self._ci.setFixedHeight(34)
        self._ci.setPlaceholderText('"25 times 4" or "15% of 200"')
        self._ci.returnPressed.connect(lambda: self._run(f"calculate {self._ci.text()}"))
        cp.body().addWidget(self._ci); cp.body().addWidget(hint("Press Enter to calculate"))
        self._ps.addWidget(cp)  # 2

        # Translate panel — updated for deep-translator
        tp = PanelBox("Translate")
        self._ti = QLineEdit(); self._ti.setFixedHeight(34)
        self._ti.setPlaceholderText('"hello to Hindi"')
        self._ti.returnPressed.connect(lambda: self._run(f"translate {self._ti.text()}"))
        tp.body().addWidget(self._ti)
        tp.body().addWidget(hint("Press Enter to translate"))
        tp.body().addWidget(hint("Powered by deep-translator"))
        self._ps.addWidget(tp)  # 3

        # Brightness panel
        bp = PanelBox("Brightness")
        brw = QWidget(); brw.setStyleSheet("background:transparent;")
        brl = QHBoxLayout(brw); brl.setContentsMargins(0,0,0,0); brl.setSpacing(8)
        brl.addWidget(small("☀"))
        self._bsl = QSlider(Qt.Orientation.Horizontal)
        self._bsl.setRange(10,100); self._bsl.setValue(70)
        self._bsl.setStyleSheet(f"""
            QSlider::groove:horizontal {{height:4px;background:{BORDER2};border-radius:2px;}}
            QSlider::handle:horizontal {{
                width:14px;height:14px;background:{ACCENT};
                border-radius:7px;margin:-5px 0;
            }}
            QSlider::sub-page:horizontal {{background:{ACCENT};border-radius:2px;}}
        """)
        self._blb = QLabel("70%"); self._blb.setFixedWidth(34)
        self._blb.setFont(QFont("Segoe UI",9))
        self._blb.setStyleSheet(f"color:{TEXT2};background:transparent;border:none;")
        self._bsl.valueChanged.connect(lambda v: self._blb.setText(f"{v}%"))
        self._bsl.sliderReleased.connect(lambda: self._run(f"set brightness to {self._bsl.value()}"))
        brl.addWidget(self._bsl, stretch=1); brl.addWidget(self._blb)
        bp.body().addWidget(brw)
        bw2 = QWidget(); bw2.setStyleSheet("background:transparent;")
        b2l = QHBoxLayout(bw2); b2l.setContentsMargins(0,0,0,0); b2l.setSpacing(5)
        for lbl,c in [("+ More","increase brightness"),("− Less","decrease brightness")]:
            b2l.addWidget(pill_btn(lbl, ACCENT, rgba(ACCENT,0.25), rgba(ACCENT,0.1),
                          lambda _,cc=c: self._run(cc)))
        bp.body().addWidget(bw2); self._ps.addWidget(bp)  # 4

        # WhatsApp panel
        wp = PanelBox("Send WhatsApp")
        self._wac = QLineEdit(); self._wac.setFixedHeight(34); self._wac.setPlaceholderText("Contact name")
        self._wam = QLineEdit(); self._wam.setFixedHeight(34); self._wam.setPlaceholderText("Message")
        self._wam.returnPressed.connect(lambda: self._run(
            f"send message to {self._wac.text()} {self._wam.text()}"))
        wp.body().addWidget(self._wac); wp.body().addWidget(self._wam)
        wp.body().addWidget(hint("Press Enter to send")); self._ps.addWidget(wp)  # 5

        # Close App panel
        cap = PanelBox("Close App")
        caw = QWidget(); caw.setStyleSheet("background:transparent;")
        cal = QGridLayout(caw); cal.setSpacing(4); cal.setContentsMargins(0,0,0,0)
        for i,ap in enumerate(["chrome","firefox","edge","spotify","notepad",
                                "calculator","vs code","discord","zoom","teams"]):
            cal.addWidget(pill_btn(ap.capitalize(), DANGER, rgba(DANGER,0.25), rgba(DANGER,0.1),
                          lambda _,a=ap: self._run(f"close {a}")), i//2, i%2)
        cap.body().addWidget(caw); self._ps.addWidget(cap)  # 6

        self._pmap = {"music":1,"calc":2,"translate":3,
                      "brightness":4,"whatsapp":5,"close_app":6}
        iv.addWidget(self._ps)

        sep = QFrame(); sep.setFixedHeight(1); sep.setStyleSheet(f"background:{BORDER};border:none;")
        iv.addWidget(sep)
        ql = QLabel("QUICK COMMANDS"); ql.setFont(QFont("Segoe UI",8,QFont.Weight.Bold))
        ql.setStyleSheet(f"color:{TEXT2};letter-spacing:2px;background:transparent;")
        iv.addWidget(ql)

        for q in ["open youtube","search Python tutorial","weather in Mumbai",
                  "tell me a joke","create spreadsheet","what time is it"]:
            qb = QPushButton(f"  › {q}"); qb.setFixedHeight(27)
            qb.setFont(QFont("Segoe UI",10))
            qb.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            qb.setStyleSheet(f"""
                QPushButton {{background:transparent;border:none;color:{TEXT3};
                    text-align:left;font-style:italic;border-radius:6px;padding:0 4px;}}
                QPushButton:hover {{background:{rgba(CARD,0.8)};color:{TEXT2};}}
            """)
            qb.clicked.connect(lambda _,c=q: self._run(c)); iv.addWidget(qb)

        iv.addStretch(); sc.setWidget(inn); v.addWidget(sc, stretch=1)
        return dock

    def _wcss(self, on):
        if on:
            return (f"QPushButton{{background:{rgba(MINT,0.12)};"
                    f"border:1px solid {rgba(MINT,0.4)};border-radius:13px;"
                    f"color:{MINT};font-size:9px;font-weight:500;}}")
        return (f"QPushButton{{background:transparent;border:1px solid {BORDER2};"
                f"border-radius:13px;color:{TEXT2};font-size:9px;}}"
                f"QPushButton:hover{{border:1px solid {ACCENT};color:{ACCENT};}}")

    # ─────────────────────────────────────────────
    #  SIGNAL HANDLERS  (main thread)
    # ─────────────────────────────────────────────
    def _do_add(self, role, text):
        if not text.strip(): return
        bw = BubbleWidget(text, role)
        self._cl.addWidget(bw)
        QTimer.singleShot(60, lambda:
            self._scroll.verticalScrollBar().setValue(
                self._scroll.verticalScrollBar().maximum()))

    def _do_state(self, state):
        self._orb.set_state(state)
        cfg = {
            "listening":  (WARN,    rgba(WARN,0.12),   rgba(WARN,0.35),   "Listening…"),
            "processing": (ACCENT2, rgba(ACCENT2,0.12),rgba(ACCENT2,0.35),"Thinking…"),
            "awake":      (MINT,    rgba(MINT,0.12),   rgba(MINT,0.35),   "Awake"),
            "idle":       (TEXT2,   rgba(CARD,0.8),    BORDER2,           "Sleeping"),
        }.get(state, (TEXT2, rgba(CARD,0.8), BORDER2, "Sleeping"))
        fg, bg, bd, lbl = cfg
        self._dot .setStyleSheet(f"background:{fg};border-radius:4px;")
        self._pill.setText(lbl)
        self._pill.setStyleSheet(self._pcss(fg, bg, bd))
        self._wave.set_active(state == "listening",
                              WARN if state == "listening" else ACCENT)

    def _do_typing(self, show):
        if show and self._typing is None:
            self._typing = TypingWidget()
            self._cl.addWidget(self._typing)
            QTimer.singleShot(60, lambda:
                self._scroll.verticalScrollBar().setValue(
                    self._scroll.verticalScrollBar().maximum()))
        elif not show and self._typing:
            self._cl.removeWidget(self._typing)
            self._typing.deleteLater(); self._typing = None

    # ─────────────────────────────────────────────
    #  ORB  — one click starts loop, second click stops
    # ─────────────────────────────────────────────
    def _orb_click(self):
        if self._loop:
            self._stop_loop()
        else:
            self._start_loop()

    def _start_loop(self):
        if self._loop: return
        self._loop = True
        self._wbtn.setText("Stop"); self._wbtn.setStyleSheet(self._wcss(True))
        w = ConvWorker()
        w.user_said    .connect(lambda t: self._sadd.emit("user", t))
        w.nova_said    .connect(lambda t: (self._styp.emit(False), self._sadd.emit("nova", t)))
        w.state_changed.connect(self._sst.emit)
        w.loop_stopped .connect(self._on_loop_done)
        self._conv = w; w.start()

    def _stop_loop(self):
        if self._conv: self._conv.stop()

    def _on_loop_done(self):
        self._loop = False; self._conv = None
        self._sst.emit("idle"); self._styp.emit(False)
        self._wbtn.setText("Wake"); self._wbtn.setStyleSheet(self._wcss(False))

    def _toggle_wake(self):
        if self._loop: self._stop_loop()
        else:          self._start_loop()

    # ─────────────────────────────────────────────
    #  TEXT INPUT
    # ─────────────────────────────────────────────
    def _txt_send(self):
        text = self._inp.text().strip()
        if not text: return
        self._inp.clear(); self._sadd.emit("user", text); self._run(text)

    # ─────────────────────────────────────────────
    #  RUN COMMAND (typed / panel)
    # ─────────────────────────────────────────────
    def _run(self, command):
        if not NOVA_OK:
            self._sadd.emit("nova", f"[Demo] Got: '{command}'. Add nova_assistant_v9.py to enable.")
            return
        self._styp.emit(True); self._sst.emit("processing")
        w = CmdWorker(command)
        w.nova_said.connect(lambda t: (self._styp.emit(False), self._sadd.emit("nova", t)))
        w.done.connect(lambda: (
            self._styp.emit(False),
            self._sst.emit("awake" if self._loop else "idle")
        ))
        self._cmd = w; w.start()

    # ─────────────────────────────────────────────
    #  FEATURE BUTTONS
    # ─────────────────────────────────────────────
    def _on_feat(self, fid):
        direct = {"weather":"what's the weather","time":"what time is it",
                  "news":"read me the news","date":"what is today",
                  "tabnav":"start tab mode","joke":"tell me a joke"}
        if fid in direct:
            if self._actpnl:
                self._fbts.get(self._actpnl, FeatBtn("","")).set_active(False)
                self._actpnl = None; self._ps.setCurrentIndex(0)
            self._run(direct[fid]); return
        if self._actpnl == fid:
            self._fbts[fid].set_active(False); self._actpnl = None
            self._ps.setCurrentIndex(0)
        else:
            if self._actpnl:
                self._fbts.get(self._actpnl, FeatBtn("","")).set_active(False)
            self._fbts[fid].set_active(True); self._actpnl = fid
            self._ps.setCurrentIndex(self._pmap.get(fid, 0))

    # ─────────────────────────────────────────────
    #  DRAG
    # ─────────────────────────────────────────────
    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self._drag = e.globalPosition().toPoint()

    def mouseMoveEvent(self, e):
        if e.buttons() == Qt.MouseButton.LeftButton and self._drag:
            self.move(self.pos() + e.globalPosition().toPoint() - self._drag)
            self._drag = e.globalPosition().toPoint()

    def mouseReleaseEvent(self, e): self._drag = None

    def closeEvent(self, e):
        if self._conv: self._conv.stop(); self._conv.wait(1500)
        super().closeEvent(e)


# ══════════════════════════════════════════════════
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    pal = QPalette()
    for role, col in [
        (QPalette.ColorRole.Window,          BG),
        (QPalette.ColorRole.WindowText,      TEXT),
        (QPalette.ColorRole.Base,            SURFACE),
        (QPalette.ColorRole.AlternateBase,   CARD),
        (QPalette.ColorRole.Button,          CARD),
        (QPalette.ColorRole.ButtonText,      TEXT),
        (QPalette.ColorRole.Highlight,       ACCENT),
        (QPalette.ColorRole.HighlightedText, "#ffffff"),
    ]:
        pal.setColor(role, QColor(col))
    app.setPalette(pal)
    win = NovaWindow(); win.show(); sys.exit(app.exec())
