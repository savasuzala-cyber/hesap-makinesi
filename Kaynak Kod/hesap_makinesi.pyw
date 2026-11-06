"""Basit masaüstü hesap makinesi (tkinter).

Çalıştırmak için dosyaya çift tıkla ya da: python hesap_makinesi.pyw

Copyright (c) 2026 YGS. Tüm hakları saklıdır.
Bu yazılımın izinsiz kopyalanması, değiştirilmesi, dağıtılması veya
ticari amaçla kullanılması yasaktır. Ayrıntılar için LICENSE dosyasına bakın.
"""

__author__ = "YGS"
__copyright__ = "Copyright (c) 2026 YGS. Tüm hakları saklıdır."

import hashlib
import sys

# Gömülü imza: ekranda görünür ve açılışta doğrulanır. Metin değiştirilir ya da
# silinirse program açılmaz.
_SIGNATURE = "© 2026 YGS"
_SIGNATURE_SHA256 = hashlib.sha256(b"\xc2\xa9 2026 YGS").hexdigest()


def _verify_signature():
    ok = (
        hashlib.sha256(_SIGNATURE.encode("utf-8")).hexdigest() == _SIGNATURE_SHA256
        and "YGS" in __copyright__
        and __author__ == "YGS"
    )
    if not ok:
        sys.exit("İmza doğrulanamadı: bu kopya değiştirilmiş. © YGS")

import ctypes
from decimal import Decimal, ROUND_HALF_UP
import tkinter as tk
from pathlib import Path

ICON_FILE = Path(__file__).with_name("hesap_makinesi.ico")
SYMBOLS = {"+": "+", "-": "−", "*": "×", "/": "÷", "%": "%", "%+": "%+", "%-": "%−"}
UI_SCALE = 1.10
MAX_DIGITS = 15
DIV_ZERO = "Sıfıra bölünemez"
KDV_RATE = 20  # KDV− tuşunun kullandığı oran (%)

COLORS = {
    "case": "#232a2d",
    "lcd": "#cbd6c4",
    "lcd_ink": "#1c2a21",
    "lcd_dim": "#55665a",
    "key": "#3b4549",
    "key_ink": "#f2f5f4",
    "fn": "#5d696e",
    "fn_ink": "#f2f5f4",
    "op": "#2a8a84",
    "op_ink": "#f3fbfa",
    "op_on": "#1b5f5b",
    "eq": "#e2a71f",
    "eq_ink": "#2b1e00",
}


def format_number(s):
    """Türkçe yazım: binlik ayracı nokta, ondalık ayracı virgül."""
    if "e" in s.lower():
        return format(Decimal(s), ".2e").replace(".", ",").replace("-", "−")
    if "." in s and not s.endswith("."):
        s = format(Decimal(s).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP), "f")
    neg = s.startswith("-")
    if neg:
        s = s[1:]
    whole, sep, frac = s.partition(".")
    groups = []
    while len(whole) > 3:
        groups.insert(0, whole[-3:])
        whole = whole[:-3]
    groups.insert(0, whole)
    out = ".".join(groups)
    if sep:
        out += "," + frac
    return ("−" if neg else "") + out


def to_text(n):
    """Sayıyı ekranda tutulan iç gösterime çevirir (ondalık ayracı ".")."""
    n = float(f"{n:.15g}")  # 0,1 + 0,2 = 0,3 olsun
    if n == int(n) and abs(n) < 1e15:
        return str(int(n))
    return repr(n)


class Calculator:
    """Arayüzden bağımsız hesap mantığı."""

    def __init__(self):
        self.stored = None    # AC+ / AC− ile biriken toplam
        self.stored_op = None  # AC= için en son basılan AC işlemi
        self._reset()

    def clear(self):
        """AC: işlemi de biriken toplamı da siler."""
        self.stored = None
        self.stored_op = None
        self._reset()

    def _reset(self):
        self.cur = "0"        # ekrandaki sayı
        self.prev = None      # işlemin sol tarafı
        self.op = None        # seçili işlem
        self.pending = False  # işlem seçildi, sağ taraf henüz girilmedi
        self.replace = False  # sonraki rakam ekrandakinin yerine yazılır
        self.error = False
        self.entered = False  # ekrana elle rakam girildi
        self.expr = ""

    @property
    def display(self):
        return self.cur if self.error else format_number(self.cur)

    @property
    def stored_text(self):
        if self.stored is None:
            return ""
        return "Bekleyen: " + format_number(to_text(self.stored))

    def _compute(self, a, b, op):
        if op == "+":
            r = a + b
        elif op == "-":
            r = a - b
        elif op == "*":
            r = a * b
        elif op == "%":  # 100 % 25 → 100'ün %25'i
            r = a * b / 100
        elif op == "%+":  # 100 %+ 20 → 100'e kendi %20'sini ekle
            r = a + a * b / 100
        elif op == "%-":  # 100 %− 20 → 100'den kendi %20'sini çıkar
            r = a - a * b / 100
        else:
            if b == 0:
                return None
            r = a / b
        if r in (float("inf"), float("-inf")) or r != r:
            return None
        return r

    def _fail(self):
        self._reset()
        self.error = True
        self.cur = DIV_ZERO

    def digit(self, d):
        if self.error:
            self._reset()
        self.entered = True
        if self.replace:
            if self.op is None:
                self.expr = ""
            self.cur = d
            self.replace = False
            self.pending = False
        elif self.cur == "0":
            self.cur = d
        elif self.cur == "-0":
            self.cur = "-" + d
        elif sum(c.isdigit() for c in self.cur) < MAX_DIGITS:
            self.cur += d

    def dot(self):
        if self.error:
            self._reset()
        self.entered = True
        if self.replace:
            if self.op is None:
                self.expr = ""
            self.cur = "0."
            self.replace = False
            self.pending = False
        elif "." not in self.cur:
            self.cur += "."

    def set_op(self, op):
        if self.error:
            return
        if self.op is not None and not self.pending:
            try:
                r = self._compute(self.prev, float(self.cur), self.op)
            except OverflowError:
                r = None
            if r is None:
                self._fail()
                return
            self.cur = to_text(r)
        self.prev = float(self.cur)
        self.op = op
        self.pending = True
        self.replace = True
        self.expr = f"{format_number(to_text(self.prev))} {SYMBOLS[op]}"

    def equals(self):
        if self.error or self.op is None:
            return
        b = float(self.cur)
        try:
            r = self._compute(self.prev, b, self.op)
        except OverflowError:
            r = None
        if r is None:
            self._fail()
            return
        self.expr = (
            f"{format_number(to_text(self.prev))} {SYMBOLS[self.op]} "
            f"{format_number(to_text(b))} ="
        )
        self.cur = to_text(r)
        self.prev = None
        self.op = None
        self.pending = False
        self.replace = True

    def negate(self):
        if self.error:
            return
        self.cur = self.cur[1:] if self.cur.startswith("-") else "-" + self.cur
        self.pending = False

    def kdv_minus(self):
        """KDV−: ekrandaki KDV dahil fiyattan KDV hariç tutarı bulur.
        580 KDV− → 580 ÷ 1,20 = 483,33 (580 − %20 = 464 DEĞİL)."""
        if self.error:
            return
        self._finish_pending()  # örn. 500 + 80 KDV− → önce 580, sonra KDV hariç
        if self.error:
            return
        gross = float(self.cur)
        net = gross / (1 + KDV_RATE / 100)
        self._reset()
        self.expr = f"{format_number(to_text(gross))} KDV− (%{KDV_RATE}) ="
        self.cur = to_text(net)
        self.replace = True

    def back(self):
        if self.error:
            self._reset()
            return
        if self.replace:
            return
        self.cur = self.cur[:-1]
        if self.cur in ("", "-"):
            self.cur = "0"

    def _finish_pending(self):
        """Yarım kalan normal işlemi bitirir; ekranda sayı varsa True döner."""
        if self.op is not None and not self.pending:
            self.equals()
        return not self.error and (self.entered or self.replace)

    def _store(self, op):
        """AC+ / AC− / AC× / AC÷: ekrandaki sayıyı biriken toplama işler ve ekranı
        sıfırlar. İlk basışta sayı toplamın başlangıcı olur. Sonuç AC= ile görünür."""
        if self.error:
            return
        has_value = self._finish_pending()
        if self.error:
            return
        value = float(self.cur)
        first = self.stored
        self._reset()
        if first is None:
            self.stored = value
            self.stored_op = op
            return
        if not has_value:  # ekran boş: sadece işlemi değiştir (örn. AC+ → AC−)
            self.stored_op = op
            return
        try:
            r = self._compute(first, value, op)
        except OverflowError:
            r = None
        if r is None:
            self._fail()  # biriken toplam kaybolmasın
            return
        self.stored = r
        self.stored_op = op

    def store_eq(self):
        """AC=: biriken toplamı, ekrandaki sayıyı da son AC işlemiyle katarak verir."""
        if self.error or self.stored is None:
            return
        has_value = self._finish_pending()
        if self.error:
            return
        value = float(self.cur)
        first = self.stored
        op = self.stored_op
        self._reset()
        if has_value:
            try:
                r = self._compute(first, value, op)
            except OverflowError:
                r = None
            if r is None:
                self._fail()
                return
            self.expr = (
                f"{format_number(to_text(first))} {SYMBOLS[op]} "
                f"{format_number(to_text(value))} ="
            )
        else:
            r = first
            self.expr = "Toplam ="
        self.stored = None
        self.stored_op = None
        self.cur = to_text(r)
        self.replace = True

    def store_add(self):
        self._store("+")

    def store_sub(self):
        self._store("-")

    def store_mul(self):
        self._store("*")

    def store_div(self):
        self._store("/")


class App(tk.Tk):
    # Her tuş: (yazı, tür, eylem) ve isteğe bağlı olarak kapladığı sütun sayısı.
    LAYOUT = [
        [("AC+", "fn", "store_add"), ("AC−", "fn", "store_sub"), ("AC×", "fn", "store_mul"), ("AC÷", "fn", "store_div")],
        [("AC=", "eq", "store_eq"), ("KDV−", "fn", "kdv_minus"), ("%+", "op", "%+"), ("%−", "op", "%-")],
        [("AC", "fn", "clear"), ("⌫", "fn", "back"), ("%", "op", "%"), ("÷", "op", "/")],
        [("7", "key", "7"), ("8", "key", "8"), ("9", "key", "9"), ("×", "op", "*")],
        [("4", "key", "4"), ("5", "key", "5"), ("6", "key", "6"), ("−", "op", "-")],
        [("1", "key", "1"), ("2", "key", "2"), ("3", "key", "3"), ("+", "op", "+")],
        [("±", "key", "negate"), ("0", "key", "0"), (",", "key", "dot"), ("=", "eq", "equals")],
    ]

    def __init__(self):
        _verify_signature()
        super().__init__()
        self.withdraw()
        self.ui_scale = 1.0
        self.calc = Calculator()
        self.op_buttons = {}

        self.title("Hesap Makinesi — YGS")
        if ICON_FILE.exists():
            self.iconbitmap(default=str(ICON_FILE))
        self.configure(bg=COLORS["case"], padx=round(16 * self.ui_scale), pady=round(16 * self.ui_scale))
        self.resizable(False, False)

        self._build_display()
        self._build_keys()
        self.update_idletasks()
        width, height = self.winfo_reqwidth(), self.winfo_reqheight()
        for child in self.winfo_children():
            child.destroy()
        self.op_buttons.clear()
        self.ui_scale = UI_SCALE
        self.tk.call("tk", "scaling", float(self.tk.call("tk", "scaling")) * UI_SCALE)
        self.configure(padx=round(16 * UI_SCALE), pady=round(16 * UI_SCALE))
        self._build_display()
        self._build_keys()
        self.geometry(f"{round(width * UI_SCALE)}x{round(height * UI_SCALE)}")
        self.deiconify()
        self.bind("<Key>", self._on_key)
        self._render()

    def _build_display(self):
        lcd = tk.Frame(self, bg=COLORS["lcd"], padx=round(12 * self.ui_scale), pady=round(8 * self.ui_scale))
        lcd.pack(fill="x", pady=(0, round(14 * self.ui_scale)))
        # Sabit yükseklik: yazı küçülünce pencere oynamasın.
        lcd.configure(height=round(112 * self.ui_scale))
        lcd.pack_propagate(False)

        self.stored_label = tk.Label(
            lcd, anchor="w", bg=COLORS["lcd"], fg=COLORS["lcd_dim"],
            font=("Consolas", 10),
        )
        self.stored_label.pack(fill="x")

        self.expr_label = tk.Label(
            lcd, anchor="e", bg=COLORS["lcd"], fg=COLORS["lcd_dim"],
            font=("Consolas", 11),
        )
        self.expr_label.pack(fill="x")
        self.value_label = tk.Label(
            lcd, anchor="e", bg=COLORS["lcd"], fg=COLORS["lcd_ink"],
            font=("Consolas", 28, "bold"),
        )
        self.value_label.pack(fill="both", expand=True)

    def _build_keys(self):
        keys = tk.Frame(self, bg=COLORS["case"])
        keys.pack()
        for r, row in enumerate(self.LAYOUT):
            c = 0
            for label, kind, action, *rest in row:
                span = rest[0] if rest else 1
                btn = tk.Button(
                    keys, text=label, width=4, height=1,
                    font=("Segoe UI", 16),
                    bg=COLORS[kind], fg=COLORS[kind + "_ink"],
                    activebackground=COLORS[kind], activeforeground=COLORS[kind + "_ink"],
                    relief="flat", bd=0, cursor="hand2", takefocus=False,
                    command=lambda a=action: self._press(a),
                )
                btn.grid(row=r, column=c, columnspan=span, sticky="ew", padx=round(4 * self.ui_scale), pady=round(4 * self.ui_scale), ipady=round(6 * self.ui_scale))
                c += span
                if kind == "op":
                    self.op_buttons[action] = btn
        tk.Label(
            self, text=_SIGNATURE, bg=COLORS["case"], fg=COLORS["lcd_dim"],
            font=("Segoe UI", 8),
        ).pack(pady=(round(8 * self.ui_scale), 0))

    def _press(self, action):
        calc = self.calc
        if action.isdigit():
            calc.digit(action)
        elif action in SYMBOLS:
            calc.set_op(action)
        else:
            getattr(calc, action)()
        self._render()

    def _on_key(self, event):
        ch, sym = event.char, event.keysym
        if event.state & 0x4:  # Ctrl kısayollarına karışma
            return
        if ch.isdigit() and ch.isascii():
            self._press(ch)
        elif ch in SYMBOLS:
            self._press(ch)
        elif ch in ("x", "X"):
            self._press("*")
        elif ch in (".", ","):
            self._press("dot")
        elif ch == "=" or sym in ("Return", "KP_Enter"):
            self._press("equals")
        elif sym == "BackSpace":
            self._press("back")
        elif sym in ("Escape", "Delete"):
            self._press("clear")

    def _render(self):
        text = self.calc.display
        size = 28 if len(text) <= 12 else max(12, int(28 * 12 / len(text)))
        self.value_label.configure(text=text, font=("Consolas", size, "bold"))
        self.expr_label.configure(text=self.calc.expr)
        self.stored_label.configure(text=self.calc.stored_text)
        for op, btn in self.op_buttons.items():
            on = self.calc.pending and self.calc.op == op
            bg = COLORS["op_on"] if on else COLORS["op"]
            btn.configure(bg=bg, activebackground=bg)


if __name__ == "__main__":
    # Görev çubuğunda Python'un değil uygulamanın kendi simgesi görünsün.
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Savas.HesapMakinesi")
    App().mainloop()
