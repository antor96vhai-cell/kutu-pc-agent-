# ============================================================
#  KUTU Agent - App Window (v3.1)
#  KUTU.bat / Desktop shortcut diye khule. Asol program
#  (agent.py) ekta alada thread e chole - ei window ta
#  holo tar mukh: status, shona kotha, jawab, ar sob log.
#  v3.1: niche chat box (type koreo command deya jay) ar
#  Bangla/English language select korar option ache.
#
#  Console chara chole (pythonw) - tai sob print ei window
#  er log box e ashe, abar kutu.log file-eo save hoy.
# ============================================================

import base64
import os
import queue
import sys
import threading

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

# ---- Sob print dhorar bebostha (agent import er AGEI) ----
# pythonw diye chalu hole sys.stdout thakei na; agent.py abar
# import er somoy-i print kore. Tai age thekei ekta
# queue-writer bosiye dei - lekha gula GUI r log box e jabe.
LOG_QUEUE = queue.Queue()


class _QueueWriter:
    """print() er lekha soja GUI r queue te pathiye dey."""

    encoding = "utf-8"
    errors = "replace"

    def write(self, s):
        if s:
            LOG_QUEUE.put(("log", str(s)))
        return len(s)

    def flush(self):
        pass

    def isatty(self):
        return False


_writer = _QueueWriter()
sys.stdout = _writer
sys.stderr = _writer

import tkinter as tk
from tkinter import messagebox, ttk

try:
    from PIL import Image, ImageTk
except Exception:
    Image = None
    ImageTk = None

import agent


def _agent_event(kind, text):
    """agent.py theke asa event queue te rakhe (thread-safe)."""
    LOG_QUEUE.put(("event", kind, text))


agent.EVENT_HOOK = _agent_event

STATUS_TEXT = {
    "listening": "🟢 Shunchi…",
    "thinking": "🤔 Bhabchi…",
    "speaking": "🔊 Bolchi…",
    "working": "🛠️ Kaj korchi…",
    "idle": "⚪ Theme achi",
}

BG = "#1f2430"
BG_DARK = "#12151c"
FG = "#e8eaf0"
FG_DIM = "#9aa3b2"
BTN_BG = "#2d333f"


def ensure_icon_png():
    """kutu.png thakle seta, na thakle icon_data.py theke
    decode kore baniye ney. Kono tai na hole None."""
    path = os.path.join(HERE, "kutu.png")
    if os.path.exists(path):
        return path
    try:
        import icon_data
        with open(path, "wb") as f:
            f.write(base64.b64decode(icon_data.PNG_B64))
        return path
    except Exception:
        return None


class KutuApp:
    def __init__(self, root):
        self.root = root
        self.thread = None
        self._sc_seen = None
        self._photo = None
        self._icon_photo = None

        root.title("KUTU Agent")
        root.geometry("560x660")
        root.minsize(520, 600)
        root.configure(bg=BG)
        root.protocol("WM_DELETE_WINDOW", self._on_close)

        png = ensure_icon_png()

        # Window icon
        if png:
            try:
                self._icon_photo = tk.PhotoImage(file=png)
                root.iconphoto(True, self._icon_photo)
            except Exception:
                pass

        # ---- Uporer ongsho: parrot + status ----
        top = tk.Frame(root, bg=BG)
        top.pack(fill="x", padx=12, pady=(8, 2))

        img_label = tk.Label(top, bg=BG)
        if png and Image is not None:
            try:
                im = Image.open(png).convert("RGBA")
                im.thumbnail((110, 110), Image.LANCZOS)
                self._photo = ImageTk.PhotoImage(im)
            except Exception:
                self._photo = None
        if self._photo is None and png:
            try:
                ph = tk.PhotoImage(file=png)
                self._photo = ph.zoom(3, 3).subsample(7, 7)  # 256px -> ~110px
            except Exception:
                self._photo = None
        if self._photo is not None:
            img_label.configure(image=self._photo)
        else:
            img_label.configure(text="🦜", font=("Segoe UI Emoji", 52),
                                fg=FG)
        img_label.pack()

        tk.Label(top, text="KUTU Agent", bg=BG, fg=FG,
                 font=("Segoe UI", 17, "bold")).pack(pady=(2, 0))

        self.status_label = tk.Label(
            top, text=STATUS_TEXT["idle"], bg=BG, fg="#7ee787",
            font=("Segoe UI", 15, "bold"))
        self.status_label.pack(pady=(2, 6))

        self.heard_label = tk.Label(
            top, text="Shunlam: —", bg=BG, fg=FG, wraplength=500,
            justify="left", font=("Segoe UI", 11))
        self.heard_label.pack(fill="x")

        self.reply_label = tk.Label(
            top, text="KUTU: —", bg=BG, fg="#ffd166", wraplength=500,
            justify="left", font=("Segoe UI", 11))
        self.reply_label.pack(fill="x", pady=(2, 0))

        # ---- Language select (Bangla / English) ----
        # Bodla bodli sathe sathe-i kaj kore, restart lage na;
        # choice ta agent settings.json e save kore rakhe.
        lang_frame = tk.Frame(top, bg=BG)
        lang_frame.pack(fill="x", pady=(6, 0))
        tk.Label(lang_frame, text="🌐 Language:", bg=BG, fg=FG_DIM,
                 font=("Segoe UI", 10)).pack(side="left")
        self.lang_combo = ttk.Combobox(
            lang_frame, values=["Bangla", "English"], state="readonly",
            width=12, font=("Segoe UI", 10))
        self.lang_combo.set("English" if agent.LANG == "en" else "Bangla")
        self.lang_combo.pack(side="left", padx=(6, 0))
        self.lang_combo.bind("<<ComboboxSelected>>",
                             self._on_lang_change)

        # ---- Self-check er result ----
        check_frame = tk.Frame(root, bg=BG)
        check_frame.pack(fill="x", padx=12, pady=(6, 0))
        tk.Label(check_frame, text="Self-check:", bg=BG, fg=FG_DIM,
                 font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.check_label = tk.Label(
            check_frame, text="(Chalu korle ekhane dekhabe)", bg=BG,
            fg=FG, justify="left", anchor="w", font=("Consolas", 10))
        self.check_label.pack(anchor="w")

        # ---- Chat box (bottom zone er sobar niche - tai
        # bottom theke PROTHOM pack kori; type koreo command
        # deya jay, voice er pasapashi, wake word lage na) ----
        chat_frame = tk.Frame(root, bg=BG)
        chat_frame.pack(side="bottom", fill="x", padx=12, pady=(0, 8))
        self.chat_entry = tk.Entry(
            chat_frame, bg=BG_DARK, fg=FG,
            insertbackground="#ffffff", font=("Segoe UI", 11),
            relief="flat")
        self.chat_entry.pack(side="left", fill="x", expand=True,
                             ipady=5)
        self.chat_entry.bind("<Return>", lambda _e: self._send_chat())
        self.send_btn = tk.Button(
            chat_frame, text="📨 Pathao", command=self._send_chat,
            bg=BTN_BG, fg=FG, activebackground="#3a4152",
            activeforeground=FG, font=("Segoe UI", 11, "bold"),
            relief="flat", padx=12, pady=5)
        self.send_btn.pack(side="left", padx=(8, 0))

        # ---- Button (bottom e pin - log er AGE pack kori, jeno
        # window choto holeo button kokhono baire na jay) ----
        btn_frame = tk.Frame(root, bg=BG)
        btn_frame.pack(side="bottom", fill="x", padx=12, pady=(2, 2))
        self.start_btn = tk.Button(
            btn_frame, text="▶️  Chalu koro (Start)", command=self.start,
            bg=BTN_BG, fg=FG, activebackground="#3a4152",
            activeforeground=FG, font=("Segoe UI", 12, "bold"),
            relief="flat", padx=14, pady=6)
        self.start_btn.pack(side="left")
        self.stop_btn = tk.Button(
            btn_frame, text="⏹️  Bondho koro (Stop)", command=self.stop,
            bg=BTN_BG, fg=FG, activebackground="#3a4152",
            activeforeground=FG, font=("Segoe UI", 12, "bold"),
            relief="flat", padx=14, pady=6, state="disabled")
        self.stop_btn.pack(side="left", padx=(10, 0))

        # Note ta button er thik upore - bottom zone ei pack kori
        tk.Label(root, text="Somossa hole kutu.log file ta KUTU ke pathao",
                 bg=BG, fg=FG_DIM, font=("Segoe UI", 9)).pack(
                     side="bottom", pady=(4, 0))

        # ---- Log box (majher baki jayga joto tuku thake) ----
        log_frame = tk.Frame(root, bg=BG)
        log_frame.pack(fill="both", expand=True, padx=12, pady=(6, 4))
        tk.Label(log_frame, text="Log:", bg=BG, fg=FG_DIM,
                 font=("Segoe UI", 10, "bold")).pack(anchor="w")
        inner = tk.Frame(log_frame, bg=BG)
        inner.pack(fill="both", expand=True)
        self.log_text = tk.Text(
            inner, wrap="word", bg=BG_DARK, fg="#d6deeb",
            insertbackground="#ffffff", font=("Consolas", 10),
            height=10,
            state="disabled", relief="flat")
        scroll = tk.Scrollbar(inner, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scroll.set)
        self.log_text.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        self.root.after(100, self._poll)

    # ---------------- Agent control ----------------

    def start(self):
        if self.thread is not None and self.thread.is_alive():
            return
        agent.GUI_MODE = True
        agent.STOP_REQUESTED = False
        self._sc_seen = None
        self.thread = threading.Thread(target=self._run_agent,
                                       daemon=True)
        self.thread.start()
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.status_label.configure(text="🟢 Shunchi…")

    def _run_agent(self):
        try:
            agent.main()
        except Exception as e:
            LOG_QUEUE.put(("log", f"\n(Agent theme gelo: {e})\n"))
        finally:
            LOG_QUEUE.put(("event", "status", "idle"))
            LOG_QUEUE.put(("agent_done",))

    def stop(self):
        agent.STOP_REQUESTED = True
        self.status_label.configure(text="⏹️ Thamchi…")

    # ---------------- Chat + language ----------------

    def _send_chat(self):
        """Chat box er lekha command hishebe pathai. Agent
        na cholle age chalu kore nei; asol kaj ta alada
        thread e hoy (Tk thread kokhono atke na)."""
        try:
            text = self.chat_entry.get().strip()
        except Exception:
            return
        if not text:
            return
        self.chat_entry.delete(0, "end")
        if self.thread is None or not self.thread.is_alive():
            self.start()
        threading.Thread(target=self._run_typed, args=(text,),
                         daemon=True).start()

    def _run_typed(self, text):
        try:
            agent.handle_typed(text)
        except Exception as e:
            LOG_QUEUE.put(("log", f"\n(Typed command e somossa: {e})\n"))

    def _on_lang_change(self, _event=None):
        sel = self.lang_combo.get()
        code = "en" if sel == "English" else "bn"
        try:
            agent.set_language(code)
        except Exception:
            pass
        print(f"(Language: {sel})")

    def _on_close(self):
        try:
            agent.STOP_REQUESTED = True
        except Exception:
            pass
        self.root.destroy()

    # ---------------- Queue poll (Tk thread ei chole) -----------

    def _poll(self):
        try:
            for _ in range(300):
                try:
                    item = LOG_QUEUE.get_nowait()
                except queue.Empty:
                    break
                if item[0] == "log":
                    self._append_log(item[1])
                elif item[0] == "event":
                    self._handle_event(item[1], item[2])
                elif item[0] == "agent_done":
                    self.start_btn.configure(state="normal")
                    self.stop_btn.configure(state="disabled")
            # Self-check result ashle dekhai (ekbar-i render)
            sc = getattr(agent, "LAST_SELF_CHECK", None)
            if sc and sc is not self._sc_seen:
                self._sc_seen = sc
                lines = [("✅ " if ok else "❌ ") + f"{label} — {detail}"
                         for label, ok, detail in sc]
                self.check_label.configure(text="\n".join(lines))
        except Exception:
            pass
        self.root.after(100, self._poll)

    def _handle_event(self, kind, text):
        if kind == "status":
            self.status_label.configure(
                text=STATUS_TEXT.get(text, STATUS_TEXT["idle"]))
            if text == "idle":
                # Agent sesh hole Stop o off, Start abar on
                if self.thread is None or not self.thread.is_alive():
                    self.start_btn.configure(state="normal")
                    self.stop_btn.configure(state="disabled")
        elif kind == "heard":
            self.heard_label.configure(text=f"Shunlam: {text}")
        elif kind == "reply":
            self.reply_label.configure(text=f"KUTU: {text}")

    def _append_log(self, s):
        try:
            self.log_text.configure(state="normal")
            self.log_text.insert("end", s)
            # Khub lomba hole ager ongsho kete choto rakhi
            lines = int(self.log_text.index("end-1c").split(".")[0])
            if lines > 1500:
                self.log_text.delete("1.0", "400.0")
            self.log_text.see("end")
            self.log_text.configure(state="disabled")
        except Exception:
            pass


def main():
    try:
        root = tk.Tk()
    except Exception:
        # Display-i nai - kichu korar nai
        return
    try:
        KutuApp(root)
        root.mainloop()
    except Exception as e:
        try:
            messagebox.showerror("KUTU Agent",
                                 f"Kichu ekta somossa holo:\n{e}")
        except Exception:
            pass


if __name__ == "__main__":
    main()
