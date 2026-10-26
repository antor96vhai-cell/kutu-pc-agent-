# ============================================================
#  KUTU PC Agent v2 - Tomar nijer voice assistant (Jarvis style)
#  Owner: Antor
#  Bolbe "Kutu" -> shunbe -> kaj korbe -> mukhe jawab debe.
#
#  v2 te notun: sudhu fixed command na - ekhon screen DEKHE
#  nije nije onek step er kaj korte pare (mouse, keyboard,
#  shell, file). Jemon: "Discord er call ta kete dao",
#  "Downloads e folder banao" - egulo ekhon somvob!
#
#  Change korte chaile beshir bhaag setting ei file er
#  uporer CONFIG ongsho tei ache. Bhoy nai, venge jabe na!
# ============================================================

import asyncio
import io
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.parse
import urllib.request
import webbrowser
from datetime import datetime
from pathlib import Path

# Windows console e Bangla print korte gele jeno crash na kore
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# ------------------ CONFIG (ekhane change koro) ------------------

# Microphone diye shona r language. "bn-BD" = Bangla,
# "en-US" = English. Bangla bolle bn-BD e best kaj kore.
LANG = "bn-BD"

# Kon kon shobdo shunle Kutu jagbe (wake word)
WAKE_WORDS = ["kutu", "hey kutu", "কুতু", "হে কুতু"]

# Voice (mukhe jawab dewar gola)
VOICE_BN = "bn-BD-NabanitaNeural"   # Bangla meye voice
VOICE_EN = "en-US-AriaNeural"       # English voice

# Gemini model (brain) - v1 shohoj command ar v2 agent loop, dui jaygatei
MODEL = "gemini-2.0-flash"

# V2 AGENT LOOP SETTING:
# Ekta boro kaje ekbare sorboccho koyta step chesta korbe
MAX_STEPS = 15

# Bipodjonok kajer age (shell command, app bondho kora,
# file lekha/delete) mukhe "korbo?" bole permission nebe kina.
# True = age jiggesh korbe (SAFE). False = jiggesh charai kore debe.
CONFIRM_DANGEROUS = True

# Notun app jog korte chaile ekhane ek line add koro.
# "url" = website, "exe" = PC r program.
APPS = {
    "youtube":    ("url", "https://www.youtube.com"),
    "facebook":   ("url", "https://www.facebook.com"),
    "instagram":  ("url", "https://www.instagram.com"),
    "google":     ("url", "https://www.google.com"),
    "gmail":      ("url", "https://mail.google.com"),
    "discord":    ("url", "https://discord.com/app"),
    "whatsapp":   ("url", "https://web.whatsapp.com"),
    "messenger":  ("url", "https://www.messenger.com"),
    "spotify":    ("url", "https://open.spotify.com"),
    "telegram":   ("url", "https://web.telegram.org"),
    "github":     ("url", "https://github.com"),
    "chrome":     ("exe", "chrome.exe"),
    "notepad":    ("exe", "notepad.exe"),
    "calculator": ("exe", "calc.exe"),
    "explorer":   ("exe", "explorer.exe"),
    "file explorer": ("exe", "explorer.exe"),
    "vs code":    ("exe", "code"),
    "visual studio code": ("exe", "code"),
}

# App bondho korar somoy kon app er process er naam ki.
# (Task Manager e je naam dekho, setai)
CLOSE_APP_NAMES = {
    "discord": "Discord.exe",
    "chrome": "chrome.exe",
    "google chrome": "chrome.exe",
    "whatsapp": "WhatsApp.exe",
    "spotify": "Spotify.exe",
    "notepad": "notepad.exe",
    "calculator": "CalculatorApp.exe",
    "telegram": "Telegram.exe",
    "vs code": "Code.exe",
}

# ------------------ Library load ------------------
# (egulo setup.bat diye install hoyeche)

try:
    import speech_recognition as sr
except ImportError:
    print("SpeechRecognition library nai. Age setup.bat chalao!")
    sys.exit(1)

try:
    import edge_tts
except ImportError:
    print("edge-tts library nai. Age setup.bat chalao!")
    sys.exit(1)

try:
    import numpy as np
    import sounddevice as sd
    import soundfile as sf
except ImportError:
    print("sounddevice / soundfile library nai (mic + speaker er jonno lage). Age setup.bat chalao!")
    sys.exit(1)

try:
    import pyautogui
    pyautogui.FAILSAFE = True  # mouse screen er konay nile sob theme jabe (safety)
except ImportError:
    pyautogui = None  # volume / screenshot / mouse-keyboard kaj korbe na

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ------------------ Gemini brain setup ------------------

API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()

# v1 er shohoj command planner (fast path)
gemini = None
# v2 er chokh-wala agent (screenshot dekhe step by step kaj kore)
agent_model = None

if API_KEY:
    try:
        import google.generativeai as genai
        genai.configure(api_key=API_KEY)
        gemini = genai.GenerativeModel(
            MODEL,
            system_instruction=(
                "You are KUTU, a friendly and playful PC voice assistant. "
                "Your owner is Antor. He speaks Bangla and English, mixed. "
                "Reply in the SAME language he used (Bangla -> Bangla, English -> English). "
                "Keep every spoken reply VERY short: 1-3 sentences, because it is read aloud.\n\n"
                "You must reply with ONLY a JSON object, no extra text, in this shape:\n"
                '{"say": "what to speak", "action": "none", "arg": ""}\n\n'
                "Possible actions:\n"
                '- "open_app"  arg = app or website name (youtube, facebook, instagram, google, gmail, discord, whatsapp, spotify, notepad, calculator, explorer, vs code)\n'
                '- "youtube_play" arg = the song or video name to search on YouTube\n'
                '- "google_search" arg = the search query\n'
                '- "time" / "date" arg = ""\n'
                '- "volume_up" / "volume_down" / "mute" arg = ""\n'
                '- "screenshot" arg = ""\n'
                '- "type_text" arg = the exact text to type\n'
                '- "exit" arg = "" (only when he says stop / goodbye / বিদায়)\n'
                '- "agent" arg = his FULL request, word for word. Use "agent" for ANYTHING that needs multiple steps, clicking inside an app, ending a call, making/moving/deleting files or folders, filling a form, changing a setting, or ANY task not covered by the simple actions above. Examples: "Discord er call kete dao", "Downloads e movies folder banao", "Chrome e amar site kholo ar login page e jao", "screen e ki ache bolo" (describing the screen also needs the agent, because only the agent can see).\n'
                '- "none" arg = "" for normal talk or questions (answer inside "say")\n'
            ),
        )
        agent_model = genai.GenerativeModel(
            MODEL,
            system_instruction=(
                "You are KUTU, a PC agent controlling Antor's Windows PC. You can see his screen: "
                "a screenshot is attached to every message. Antor speaks Bangla and English, mixed. "
                "Your job: complete his goal step by step.\n\n"
                "Reply with ONLY one JSON object, no extra text:\n"
                '{"thought": "what you see on screen + what you will do next", '
                '"tool": "<tool name>", "args": {...}, "say": "short line to speak, often empty"}\n\n'
                "Tools:\n"
                '- screenshot {} -> just look at the screen again\n'
                '- click {"x":0-1000,"y":0-1000} | double_click {"x","y"} | right_click {"x","y"} | mouse_move {"x","y"}\n'
                '  Coordinates are RELATIVE to the screenshot: 0,0 = top-left corner, 1000,1000 = bottom-right. NEVER use pixel numbers.\n'
                '- scroll {"amount": -10..10} (positive = scroll up, negative = down)\n'
                '- type_text {"text":"..."} | press_key {"key":"enter"} | hotkey {"keys":["ctrl","l"]}\n'
                '- open_app {"name":"discord"} (known apps, websites, or any program name)\n'
                '- close_app {"name":"Discord.exe"} [DANGEROUS - Antor must confirm by voice]\n'
                '- run_shell {"command":"..."} runs a PowerShell command [DANGEROUS - needs confirmation]\n'
                '- open_url {"url":"https://..."}\n'
                '- read_file {"path":"C:\\\\..."} | write_file {"path":"...","content":"..."} [write is DANGEROUS]\n'
                '- list_folder {"path":"..."} | delete_path {"path":"..."} [delete is DANGEROUS]\n'
                '- clipboard_get {} | clipboard_set {"text":"..."}\n'
                '- wait {"seconds":2}\n'
                '- done {"say":"final summary"} -> use when the goal is complete, or honestly impossible.\n\n'
                "Rules:\n"
                "1. ONE tool per reply. After every step you receive a NEW screenshot - look at it carefully and VERIFY your last action worked before continuing. If it did not work, try a different way.\n"
                "2. Prefer keyboard shortcuts, search boxes and menus over hunting for pixels.\n"
                "3. 'say' is spoken aloud to Antor. Keep it VERY short and in HIS language. Leave it empty most steps; speak only occasional progress. In 'done', 'say' is required: report the result honestly.\n"
                "4. For ending a Discord voice call: look at the bottom-left voice panel and click the red disconnect (phone) button; or right-click the channel... try the visible disconnect button first.\n"
                "5. NEVER type passwords, OTP or payment details. If a login window, CAPTCHA or Windows UAC/admin prompt blocks you, use 'done' and explain honestly.\n"
                "6. If you are stuck after several different tries, use 'done' and say what failed. Do not loop the same failed click again and again.\n"
            ),
        )
    except Exception as e:
        print("Gemini setup e somossa:", e)
        gemini = None
        agent_model = None

# ------------------ Mukhe bola (TTS) ------------------

def has_bangla(text):
    """Reply te Bangla lekha ache kina dekhe."""
    return any("\u0980" <= ch <= "\u09ff" for ch in text)


async def _make_mp3(text, voice, filename):
    tts = edge_tts.Communicate(text, voice)
    await tts.save(filename)


def play_mp3(filename):
    """MP3 file ta speaker e bajay (soundfile + sounddevice diye).
    File er nijer sample-rate ar mono/stereo onujayei bajbe."""
    data, rate = sf.read(filename, dtype="float32")
    sd.play(data, rate)
    sd.wait()


def speak(text):
    """Console e print kore + mukhe bole dey."""
    print("\nKUTU:", text)
    voice = VOICE_BN if has_bangla(text) else VOICE_EN
    filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_kutu_voice.mp3")
    try:
        asyncio.run(_make_mp3(text, voice, filename))
        play_mp3(filename)
    except Exception as e:
        print("(Voice cholche na, internet ache kina dekho. Error:", e, ")")

# ------------------ Shona (microphone) ------------------
# Mic diye record kore sounddevice (PyAudio lage na!),
# tarpor Google diye text e convert kore SpeechRecognition.

recognizer = sr.Recognizer()

# Mic er setting: 16kHz, mono, 100 millisecond er choto frame kore shuni
SAMPLE_RATE = 16000
FRAME_SAMPLES = 1600          # 100ms @ 16kHz
SAMPLE_WIDTH = 2              # int16 = 2 byte
# Frame er energy (RMS) er beshi hole "kotha bolche" dhora hoy.
# Shurute calibrate_noise() ghore r normal awaz mepe eta thik kore ney.
ENERGY_THRESHOLD = 300
SILENCE_SECONDS = 0.9         # kotha seshe etokkhon chup = phrase sesh


def _frame_rms(frame):
    """Ekta choto audio frame er jore-awaz (RMS) hishab kore."""
    arr = np.asarray(frame, dtype=np.float32).reshape(-1)
    if arr.size == 0:
        return 0.0
    return float(np.sqrt(np.mean(arr * arr)))


def calibrate_noise(duration=0.6):
    """Shurute ghore r faka awaz mepe ENERGY_THRESHOLD set kore.
    (Ager adjust_for_ambient_noise er motoi kaj, sudhu sounddevice diye.)
    Mic na pele exception uthbe - main() seta dhore nebo."""
    global ENERGY_THRESHOLD
    frames_needed = max(1, int(duration * SAMPLE_RATE / FRAME_SAMPLES))
    vals = []
    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1,
                        dtype="int16", blocksize=FRAME_SAMPLES) as stream:
        for _ in range(frames_needed):
            data, _overflowed = stream.read(FRAME_SAMPLES)
            vals.append(_frame_rms(data))
    noise = float(np.median(vals)) if vals else 0.0
    ENERGY_THRESHOLD = int(min(2500, max(120, noise * 3)))
    print(f"(Mic ready - ghore r noise: {int(noise)}, threshold: {ENERGY_THRESHOLD})")


def record_phrase(timeout=6, phrase_limit=8):
    """Mic theke ekta phrase record kore sr.AudioData ferot dey.
    Niyom ager recognizer.listen() er motoi:
      timeout      = kotha SURU howar jonno koto second opekkha (None = jotokkhon lage)
      phrase_limit = ekta phrase sorboccho koto second lomba hobe
      kotha seshe ~0.9 second chup thaklei phrase sesh.
    Kotha suru-e na hole None ferot dey."""
    chunks = []        # record howa audio r tukra (bytes)
    pre_roll = []      # kotha suru howar thik ager ~0.3s (prothom shobdo jeno kete na jay)
    started = False
    silent_frames = 0
    waited = 0.0
    silence_limit = int(SILENCE_SECONDS * SAMPLE_RATE / FRAME_SAMPLES)
    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1,
                        dtype="int16", blocksize=FRAME_SAMPLES) as stream:
        while True:
            data, _overflowed = stream.read(FRAME_SAMPLES)
            raw = np.asarray(data, dtype=np.int16).reshape(-1).tobytes()
            loud = _frame_rms(data) > ENERGY_THRESHOLD
            if not started:
                pre_roll.append(raw)
                if len(pre_roll) > 3:
                    pre_roll.pop(0)
                if loud:
                    started = True
                    chunks = list(pre_roll)
                    pre_roll = []
                else:
                    waited += FRAME_SAMPLES / SAMPLE_RATE
                    if timeout is not None and waited >= timeout:
                        return None
            else:
                chunks.append(raw)
                if loud:
                    silent_frames = 0
                else:
                    silent_frames += 1
                    if silent_frames >= silence_limit:
                        break
                if len(chunks) * FRAME_SAMPLES / SAMPLE_RATE >= phrase_limit:
                    break
    if not chunks:
        return None
    return sr.AudioData(b"".join(chunks), SAMPLE_RATE, SAMPLE_WIDTH)


def listen(timeout=6, phrase_limit=8):
    """Mic theke shone, lekha (text) ferot dey. Na bujhle None."""
    try:
        audio = record_phrase(timeout=timeout, phrase_limit=phrase_limit)
    except Exception:
        # Mic na pawa / permission nai (sounddevice PortAudioError ekhane ashe)
        print("Microphone pawa jacche na! Mic lagano ache kina / permission dekho.")
        time.sleep(2)
        return None
    if audio is None:
        return None
    try:
        text = recognizer.recognize_google(audio, language=LANG)
        return text
    except sr.UnknownValueError:
        return None
    except sr.RequestError:
        print("Internet nai mone hoy - voice shona jacche na.")
        time.sleep(2)
        return None

# ------------------ Kaj kora (v1 shohoj actions) ------------------

def open_app(name):
    name = (name or "").lower().strip()
    # prothome exact match, tarpor partial match
    key = None
    if name in APPS:
        key = name
    else:
        for k in APPS:
            if k in name or name in k:
                key = k
                break
    if key:
        kind, target = APPS[key]
        try:
            if kind == "url":
                webbrowser.open(target)
            else:
                os.startfile(target)  # Windows e program kholar shohoj way
            return True
        except Exception:
            # "code" er moto program PATH e thakle ei vabe khule
            try:
                os.system(f'start "" {target}')
                return True
            except Exception:
                return False
    # v2: APPS e na thakleo jekono program er naam try kore
    if name:
        try:
            os.system(f'start "" {name}')
            return True
        except Exception:
            return False
    return False


def youtube_play(query):
    """YouTube e search kore prothom video ta khule dey."""
    try:
        url = "https://www.youtube.com/results?search_query=" + urllib.parse.quote(query)
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        html = urllib.request.urlopen(req, timeout=10).read().decode("utf-8", "ignore")
        m = re.search(r'"videoId":"([\w-]{11})"', html)
        if m:
            webbrowser.open("https://www.youtube.com/watch?v=" + m.group(1))
            return True
    except Exception:
        pass
    # Fail hole sudhu search page tai khule dei
    webbrowser.open("https://www.youtube.com/results?search_query=" + urllib.parse.quote(query))
    return True


def google_search(query):
    webbrowser.open("https://www.google.com/search?q=" + urllib.parse.quote(query))
    return True


def do_volume(action):
    if pyautogui is None:
        return False
    if action == "volume_up":
        for _ in range(5):
            pyautogui.press("volumeup")
    elif action == "volume_down":
        for _ in range(5):
            pyautogui.press("volumedown")
    elif action == "mute":
        pyautogui.press("volumemute")
    return True


def take_screenshot():
    if pyautogui is None:
        return None
    folder = os.path.expanduser("~/Pictures")
    os.makedirs(folder, exist_ok=True)
    name = "kutu_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".png"
    path = os.path.join(folder, name)
    pyautogui.screenshot(path)
    return path


def clipboard_set(text):
    """Clipboard e lekha rakhe (Bangla/Unicode o hoy)."""
    import tkinter
    root = tkinter.Tk()
    root.withdraw()
    root.clipboard_clear()
    root.clipboard_append(text)
    root.update()
    root.destroy()


def clipboard_get():
    """Clipboard er lekha pore dey."""
    import tkinter
    root = tkinter.Tk()
    root.withdraw()
    try:
        text = root.clipboard_get()
    except Exception:
        text = ""
    root.destroy()
    return text


def type_text(text):
    if pyautogui is None or not text:
        return False
    time.sleep(0.5)  # user ke target jaygay click korar somoy dey
    try:
        if all(ord(ch) < 128 for ch in text):
            pyautogui.write(text, interval=0.03)
        else:
            # Bangla / unicode hole clipboard diye paste kore
            clipboard_set(text)
            pyautogui.hotkey("ctrl", "v")
        return True
    except Exception:
        return False


def run_action(action, arg):
    """v1: Gemini r deya shohoj action ta sotti kore kore. True/False ferot dey."""
    if action == "open_app":
        return open_app(arg)
    if action == "youtube_play":
        return youtube_play(arg)
    if action == "google_search":
        return google_search(arg)
    if action == "time":
        now = datetime.now().strftime("%I:%M %p")
        speak("এখন সময় " + now)  # "Ekhon somoy ..."
        return True
    if action == "date":
        today = datetime.now().strftime("%d %B %Y")
        speak("আজকের তারিখ " + today)
        return True
    if action in ("volume_up", "volume_down", "mute"):
        return do_volume(action)
    if action == "screenshot":
        path = take_screenshot()
        if path:
            speak("Screenshot niyechi! Pictures folder e rekhe dilam.")
            return True
        return False
    if action == "type_text":
        return type_text(arg)
    return False

# ============================================================
#  V2 TOOLS - Screen dekha, mouse, keyboard, shell, file
# ============================================================

# Ei tool gula bipodjonok - CONFIRM_DANGEROUS on thakle age permission nebe
DANGEROUS_TOOLS = {"run_shell", "close_app", "write_file", "delete_path"}

TOOL_EMOJI = {
    "screenshot": "📸", "click": "🖱️", "double_click": "🖱️", "right_click": "🖱️",
    "mouse_move": "↔️", "scroll": "🖱️", "type_text": "⌨️", "press_key": "⌨️",
    "hotkey": "⌨️", "open_app": "🚀", "close_app": "🛑", "run_shell": "💻",
    "open_url": "🌐", "read_file": "📖", "write_file": "✍️", "list_folder": "📂",
    "delete_path": "🗑️", "clipboard_get": "📋", "clipboard_set": "📋",
    "wait": "⏳", "done": "✅",
}


def get_screen_image():
    """Screen er chobi Gemini ke pathanor moto kore banay.
    (image_part, (asol_screen_width, asol_screen_height)) ferot dey."""
    if pyautogui is None:
        return None, (0, 0)
    img = pyautogui.screenshot()  # PIL Image
    real_w, real_h = img.size
    if real_w > 1280:
        # Boro screen hole choto kori - free quota bachbe, kaj o fast hobe
        img = img.resize((1280, int(real_h * 1280 / real_w)))
    buf = io.BytesIO()
    img.convert("RGB").save(buf, "JPEG", quality=70)
    part = {"mime_type": "image/jpeg", "data": buf.getvalue()}
    return part, (real_w, real_h)


def to_screen_xy(x, y):
    """Model er 0-1000 hishab ke asol screen er pixel e ney."""
    w, h = pyautogui.size()
    x = max(0, min(1000, float(x)))
    y = max(0, min(1000, float(y)))
    return int(x / 1000 * w), int(y / 1000 * h)


def clean_path(p):
    """Path er ~ ar %VAR% thik kore asol path banay."""
    return Path(os.path.expandvars(os.path.expanduser(str(p or "").strip())))


def path_is_blocked(p, for_write=False):
    """Khub bipodjonok jayga (Windows folder, puropuri drive, nijer
    basha-folder er root) delete/write theke bachanor guard."""
    try:
        target = p.resolve()
    except Exception:
        return True
    home = Path.home().resolve()
    win_dir = Path(os.environ.get("SystemRoot", "C:\\Windows")).resolve()
    # Drive er ekdom root (C:\, D:\) kokhonoi na
    if str(target) == target.anchor:
        return True
    # Windows folder er vitore kichu delete/write kora jabe na
    if target == win_dir or win_dir in target.parents or target in win_dir.parents:
        return True
    if for_write:
        return False
    # Delete er jonno aro strict: nijer home folder ta nijei ba tar uporer
    # kono folder delete kora jabe na (kintu vitore er file/folder parbe)
    if target == home or target in home.parents:
        return True
    return False


def shell_is_blocked(cmd):
    """Catastrophic (sob sesh kore deya) shell command atkano.
    choto ekta denylist - format, diskpart, ar root folder er
    recursive delete. Baki gula confirmation gate-i dekhbe."""
    low = (cmd or "").lower()
    if "diskpart" in low:
        return True
    if re.search(r"\bformat\s+[a-z]:", low):  # format c: type
        return True
    # recursive delete diye drive root / Windows / home muche fela
    if re.search(r"(remove-item|del|erase|rd|rmdir|ri)\b", low) and ("-recurse" in low or "/s" in low):
        if (re.search(r"[a-z]:\\?\s*$", low) or "c:\\windows" in low
                or "%userprofile%" in low or "$env:userprofile" in low
                or re.search(r"[a-z]:\\?\s*[\"']?\s*$", low)):
            return True
    return False


YES_WORDS = ["yes", "ha", "hæ", "হ্যাঁ", "হ্যা", "হা", "জি", "ji",
             "koro", "করো", "ok", "okay", "হু", "হুম", "হুমম", "sure", "হই"]
NO_WORDS = ["no", "na", "না", "koro na", "করো না", "না করো", "lagbe na",
            "লাগবে না", "বাদ", "bad", "cancel", "করো না তো"]
STOP_WORDS = ["stop", "tham", "থাম", "থামো", "bondho", "বন্ধ", "বন্ধ করো", "stop koro"]


def hear_verdict(text):
    """Shona uttor theke 'yes' / 'no' / 'stop' / None (bujha jay ni) ferot dey."""
    if not text:
        return None
    low = text.lower().strip()
    for w in STOP_WORDS:
        if w in low:
            return "stop"
    for w in NO_WORDS:
        if w in low:
            return "no"
    for w in YES_WORDS:
        if w in low:
            return "yes"
    return None


def describe_danger(tool, args):
    """Bipodjonok kaj ta mukhe bolar moto kore sajay."""
    if tool == "close_app":
        return f"{args.get('name', 'app')} app ta puropuri bondho kore dicchi. Korbo?"
    if tool == "run_shell":
        return f"Ekta computer command chalate chasci: {str(args.get('command', ''))[:80]}. Korbo?"
    if tool == "write_file":
        return f"{args.get('path', '')} - ei file e notun lekha save kortesi. Korbo?"
    if tool == "delete_path":
        return f"{args.get('path', '')} - eta DELETE kore dicchi, ar ferot asbe na. Korbo?"
    return "Ekta sensetive kaj korte chasci. Korbo?"


def ask_confirmation(tool, args):
    """Mukhe jiggesh kore, mic e 'ha'/'na' shune.
    'yes' / 'no' / 'stop' ferot dey. Na shunle ba bujha na gele 'no'."""
    speak(describe_danger(tool, args))
    print("(Mic e bolo: 'ha' = koro, 'na' = koro na, 'tham' = puropuri bondho)")
    heard = listen(timeout=7, phrase_limit=4)
    verdict = hear_verdict(heard)
    if verdict:
        return verdict
    print("(Thik moto shona jay ni - safety r jonno kaj ta korlam na)")
    return "no"


def tool_close_app(args):
    name = str(args.get("name", "")).strip()
    if not name:
        return "Error: app er naam nai"
    exe = CLOSE_APP_NAMES.get(name.lower(), name)
    if not exe.lower().endswith(".exe"):
        exe += ".exe"
    r = subprocess.run(["taskkill", "/IM", exe, "/F"],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=15)
    if r.returncode == 0:
        return f"{exe} bondho hoye geche."
    return f"{exe} bondho holo na: {(r.stderr or r.stdout or '').strip()[:200]}"


def tool_run_shell(args):
    cmd = str(args.get("command", "")).strip()
    if not cmd:
        return "Error: command khali"
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command", cmd],
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=30)
        out = ((r.stdout or "") + "\n" + (r.stderr or "")).strip()
        if not out:
            out = f"(kono output nai, code {r.returncode})"
        return out[-1500:]  # beshi lomba hole sheser ongsho
    except subprocess.TimeoutExpired:
        return "Error: command 30 second er beshi somoy nilo, theme gelam."
    except Exception as e:
        return f"Error: {e}"


def execute_tool(tool, args):
    """Ekta v2 tool chaliye choto result (text) ferot dey.
    Result ta Gemini porer step e dekhbe."""
    if pyautogui is None and tool in ("click", "double_click", "right_click",
                                      "mouse_move", "scroll", "press_key",
                                      "hotkey", "screenshot"):
        return "Error: pyautogui nai - mouse/keyboard cholbe na."

    if tool == "screenshot":
        return "Thik ache, notun screenshot porer step er sathei pabe."

    if tool in ("click", "double_click", "right_click", "mouse_move"):
        x, y = to_screen_xy(args.get("x", 0), args.get("y", 0))
        if tool == "click":
            pyautogui.click(x, y)
        elif tool == "double_click":
            pyautogui.doubleClick(x, y)
        elif tool == "right_click":
            pyautogui.click(x, y, button="right")
        else:
            pyautogui.moveTo(x, y, duration=0.3)
        return f"{tool} hoyeche ({x}, {y}) pixel e."

    if tool == "scroll":
        amt = max(-25, min(25, int(args.get("amount", 0))))
        pyautogui.scroll(amt)
        return f"Scroll hoyeche ({amt})."

    if tool == "type_text":
        ok = type_text(str(args.get("text", "")))
        return "Lekha type hoyeche." if ok else "Error: type kora jay ni."

    if tool == "press_key":
        key = str(args.get("key", "")).strip()
        if not key:
            return "Error: key nai"
        pyautogui.press(key)
        return f"'{key}' chap deya hoyeche."

    if tool == "hotkey":
        keys = [str(k).strip() for k in args.get("keys", []) if str(k).strip()]
        if not keys:
            return "Error: keys nai"
        pyautogui.hotkey(*keys)
        return f"Hotkey {'+'.join(keys)} deya hoyeche."

    if tool == "open_app":
        nm = str(args.get("name", ""))
        return f"'{nm}' khola hoyeche." if open_app(nm) else f"Error: '{nm}' khola jay ni."

    if tool == "open_url":
        url = str(args.get("url", "")).strip()
        if not url:
            return "Error: url nai"
        webbrowser.open(url)
        return f"Browser e khola hoyeche: {url}"

    if tool == "close_app":
        return tool_close_app(args)

    if tool == "run_shell":
        return tool_run_shell(args)

    if tool == "read_file":
        p = clean_path(args.get("path", ""))
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
            return f"{p} er lekha (prothom ongsho):\n" + text[:2000]
        except Exception as e:
            return f"Error: file pora jay ni - {e}"

    if tool == "write_file":
        p = clean_path(args.get("path", ""))
        try:
            if p.parent and not p.parent.exists():
                p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(str(args.get("content", "")), encoding="utf-8")
            return f"File save hoyeche: {p}"
        except Exception as e:
            return f"Error: file lekha jay ni - {e}"

    if tool == "list_folder":
        p = clean_path(args.get("path", ""))
        try:
            items = []
            for e in os.scandir(p):
                items.append(e.name + ("/" if e.is_dir() else ""))
                if len(items) >= 100:
                    items.append("...(aro ache)")
                    break
            return f"{p} er vitore:\n" + ("\n".join(items) if items else "(khali folder)")
        except Exception as e:
            return f"Error: folder dekha jay ni - {e}"

    if tool == "delete_path":
        p = clean_path(args.get("path", ""))
        try:
            if p.is_dir():
                shutil.rmtree(p)
            else:
                p.unlink()
            return f"Delete hoyeche: {p}"
        except Exception as e:
            return f"Error: delete hoy ni - {e}"

    if tool == "clipboard_get":
        try:
            return "Clipboard e ache: " + (clipboard_get() or "(khali)")[:1000]
        except Exception as e:
            return f"Error: clipboard pora jay ni - {e}"

    if tool == "clipboard_set":
        try:
            clipboard_set(str(args.get("text", "")))
            return "Clipboard e rakha hoyeche."
        except Exception as e:
            return f"Error: clipboard e rakha jay ni - {e}"

    if tool == "wait":
        sec = max(0, min(30, float(args.get("seconds", 1))))
        time.sleep(sec)
        return f"{sec} second wait korlam."

    return f"Error: '{tool}' name er tool nai."

# ============================================================
#  V2 AGENT LOOP - Screen dekhe, step by step, ja bolo tai kore
# ============================================================

def is_quota_error(e):
    """Gemini free quota / rate limit er error kina dekhe."""
    s = str(e).lower()
    return ("429" in s or "quota" in s or "exhausted" in s
            or "rate limit" in s or "resource_exhausted" in s.replace(" ", "_"))


def parse_step(raw):
    """Agent model er uttor theke step JSON ber kore. Vul hole None."""
    try:
        text = raw.strip()
        text = re.sub(r"^```(json)?", "", text).strip()
        text = re.sub(r"```$", "", text).strip()
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1:
            return None
        obj = json.loads(text[start:end + 1])
        args = obj.get("args", {})
        if not isinstance(args, dict):
            args = {}
        return {
            "thought": str(obj.get("thought", "")).strip(),
            "tool": str(obj.get("tool", "")).strip(),
            "args": args,
            "say": str(obj.get("say", "")).strip(),
        }
    except Exception:
        return None


def run_agent_loop(goal, intro=""):
    """Boro kaj: screenshot dekhe -> ek step kore -> abar dekhe...
    'done' na howa porjonto ba MAX_STEPS porjonto cholte thake."""
    if pyautogui is None:
        speak("দুঃখিত Antor, mouse-keyboard er library (pyautogui) nai. setup.bat ta abar chalao.")
        return
    if agent_model is None:
        speak("Brain ready na Antor. API key ta check koro.")
        return

    print("\n" + "=" * 55)
    print("AGENT MODE:", goal)
    print("(Thamate chaile confirmation er somoy 'tham' bolo, ba Ctrl+C chap dao,")
    print(" ba mouse ta screen er ekdom konay niye jao)")
    print("=" * 55)
    speak(intro or "ঠিক আছে Antor, kaj ta suru kortesi.")

    history = []   # ager step gular choto hishab (model ke mone koranor jonno)
    fails = 0      # por por koybar fail holo

    try:
        for step in range(1, MAX_STEPS + 1):
            part, _size = get_screen_image()
            if part is None:
                speak("Screen er chobi nite parlam na Antor.")
                return

            hist_text = "\n".join(history[-12:]) if history else "(ekhono kichu kori ni)"
            prompt = (
                f"Antor's goal: {goal}\n\n"
                f"Steps so far:\n{hist_text}\n\n"
                f"This is step {step} of {MAX_STEPS}. Look at the screenshot "
                f"and do the NEXT single step. Reply with ONLY the JSON object."
            )

            try:
                resp = agent_model.generate_content([prompt, part])
                raw = resp.text or ""
            except Exception as e:
                if is_quota_error(e):
                    speak("দুঃখিত Antor, Gemini er free quota sesh hoye geche. "
                          "Screen dekhe kaj ekhon ar hobe na - kintu shohoj command "
                          "(somoy, app khola, gaan) cholte thakbe. Ektu pore ba kalke abar try koro.")
                    return
                fails += 1
                print("(Gemini error:", e, ")")
                if fails >= 3:
                    speak("বারবার সমস্যা হচ্ছে Antor, kaj ta thamiye dilam.")
                    return
                time.sleep(1)
                continue

            st = parse_step(raw)
            if st is None:
                fails += 1
                print("(Model er uttor bujha jay ni:", raw[:150], ")")
                if fails >= 3:
                    speak("Model ultapalta bolche Antor, kaj ta thamiye dilam.")
                    return
                continue
            fails = 0

            tool, args, say = st["tool"], st["args"], st["say"]
            if st["thought"]:
                print(f"Step {step} bhabna:", st["thought"])

            # Kaj sesh?
            if tool == "done":
                final = say or str(args.get("say", "")).strip() or "Kaj sesh Antor."
                print("DONE:", final)
                speak(final)
                return

            # Code-level block: model bollei hobe na, catastrophic kaj atkano thakbei
            blocked_msg = None
            if tool == "run_shell" and shell_is_blocked(str(args.get("command", ""))):
                blocked_msg = "ei command ta catastrophic type (disk format / root delete) - safety rule e atkano."
            if tool in ("delete_path", "write_file"):
                if path_is_blocked(clean_path(args.get("path", "")),
                                    for_write=(tool == "write_file")):
                    blocked_msg = "ei jayga ta protected (Windows folder / drive root / bashar folder er root)."
            if blocked_msg:
                print("⛔ BLOCKED:", tool, "-", blocked_msg)
                speak("Ekta kotha Antor - ei kaj ta ami korte parbo na, jaygata protected.")
                history.append(f"Step {step}: {tool} -> BLOCKED: {blocked_msg}")
                continue

            # Bipodjonok kaj hole mukhe permission
            if tool in DANGEROUS_TOOLS and CONFIRM_DANGEROUS:
                verdict = ask_confirmation(tool, args)
                if verdict == "stop":
                    speak("ঠিক আছে Antor, puropuri thamiye dilam.")
                    return
                if verdict != "yes":
                    res = "Antor 'na' bollo - ei step ta kora holo na. Onno upay thakle chesta koro, na thakle done koro."
                    print("🚫 Antor na bollo, step batil:", tool)
                    history.append(f"Step {step}: {tool} -> {res}")
                    continue

            log_args = json.dumps(args, ensure_ascii=False)[:110]
            print(f"{TOOL_EMOJI.get(tool, '🔧')} {tool}({log_args})")
            # Proti step e mukhe bola na - majhe majhe progress
            if say and (step == 1 or step % 4 == 0):
                speak(say)

            try:
                result = execute_tool(tool, args)
            except pyautogui.FailSafeException:
                # Mouse screen er konay neya mane: sob thamaw!
                speak("Mouse konay neyate sob thamiye dilam Antor.")
                return
            except Exception as e:
                result = f"Error: {e}"
            print("   ->", result[:200])
            history.append(f"Step {step}: {tool} {log_args} -> {result[:180]}")
            time.sleep(0.6)
    except KeyboardInterrupt:
        print("\n(Ctrl+C - agent thamano holo)")
        speak("ঠিক আছে Antor, kaj ta thamiye dilam.")
        return

    speak("Onek chesta korlam Antor, kintu kaj ta sesh korte parlam na. Screen ta ekbar dekhe nao.")

# ------------------ Gemini ke jiggasha (v1 fast path) ------------------

def parse_plan(raw):
    """Gemini r uttor theke JSON khuje ber kore. Vul hole safe default."""
    try:
        text = raw.strip()
        text = re.sub(r"^```(json)?", "", text).strip()
        text = re.sub(r"```$", "", text).strip()
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            plan = json.loads(text[start:end + 1])
            return {
                "say": str(plan.get("say", "")).strip(),
                "action": str(plan.get("action", "none")).strip(),
                "arg": str(plan.get("arg", "")).strip(),
            }
    except Exception:
        pass
    return {"say": raw.strip()[:200] if raw else "", "action": "none", "arg": ""}


def local_fallback(command):
    """Gemini na thakle / fail korle shohoj keyword diye kaj.
    Plan ferot dey, nahoy None."""
    low = command.lower()
    if "time" in low or "সময়" in command or "কয়টা" in command:
        return {"say": "", "action": "time", "arg": ""}
    if "date" in low or "তারিখ" in command:
        return {"say": "", "action": "date", "arg": ""}
    if "screenshot" in low or "স্ক্রিনশট" in command:
        return {"say": "", "action": "screenshot", "arg": ""}
    return None


def handle_command(command):
    """Ekta command niye kaj + jawab. False ferot dile bondho hobe."""
    print("Tumi bolle:", command)

    # Sesh kotha: stop / goodbye
    low = command.lower()
    if low.strip() in ("stop", "goodbye", "bye", "বিদায়", "থামো", "bondho koro"):
        speak("ঠিক আছে Antor, বিদায়! Abar dorkar hole dak dio.")
        return False

    plan = None
    if gemini is not None:
        try:
            response = gemini.generate_content(command)
            plan = parse_plan(response.text or "")
        except Exception as e:
            print("(Gemini error:", e, "- free quota sesh hote pare, ektu pore try koro)")
            plan = None

    if plan is None:
        plan = local_fallback(command)
    if plan is None:
        speak("দুঃখিত Antor, ekhon bujhte parlam na. Internet ba API key ta check koro.")
        return True

    action = plan["action"]
    say = plan["say"]

    if action == "exit":
        speak(say or "ঠিক আছে, বিদায়!")
        return False

    # time/date nijerai bole dey run_action er vitore
    if action in ("time", "date"):
        run_action(action, "")
        return True

    # v2: boro / onek step er kaj hole chokh-wala agent loop
    if action == "agent":
        run_agent_loop(plan["arg"] or command, intro=say)
        return True

    ok = True
    if action != "none":
        ok = run_action(action, plan["arg"])

    if say:
        speak(say)
    elif action != "none":
        speak("হয়ে গেছে!" if ok else "দুঃখিত, kaj ta korte parlam na.")
    return True

# ------------------ Main loop ------------------

def find_command(text):
    """Wake word ache kina dekhe; thakle porer ongsho (command) ferot dey.
    Wake word thakleo command na thakle '' ferot dey. Na thakle None."""
    low = text.lower()
    for w in WAKE_WORDS:
        wl = w.lower()
        idx = low.find(wl)
        if idx != -1:
            rest = text[idx + len(w):].strip(" ,.!?-")
            return rest
    return None


def main():
    print("=" * 55)
    print("   KUTU PC AGENT v2 - Antor er voice assistant")
    print("=" * 55)

    if not API_KEY or gemini is None:
        print()
        print("!! GEMINI_API_KEY pawa jay ni !!")
        print("1) aistudio.google.com theke free API key nao")
        print("2) ei folder er .env file khule GEMINI_API_KEY= er pore paste koro")
        print("3) tarpor abar run.bat chalao")
        print()
        input("Bondho korte Enter chap dao...")
        return

    # Mic er noise mapano (ekbar, shurute)
    try:
        print("Mic thik kora hocche... 1 second chup thako...")
        calibrate_noise(duration=0.6)
    except Exception:
        print("Microphone pawa jay ni! Mic connect kore abar chalao.")
        input("Bondho korte Enter chap dao...")
        return

    speak("আসসালামু আলাইকুম Antor! Ami Kutu, ready achi. Amake daklei hobe.")

    try:
        while True:
            text = listen(timeout=None, phrase_limit=5)
            if not text:
                continue
            command = find_command(text)
            if command is None:
                continue  # wake word sara kotha ignore
            print("\n[Jaglam!] Shunlam:", text)
            if command == "":
                speak("জি Antor, bolo?")
                command = listen(timeout=8, phrase_limit=10)
                if not command:
                    continue
            if not handle_command(command):
                break
    except KeyboardInterrupt:
        print("\n(Ctrl+C chap deya hoyeche - KUTU bondho hocche)")


if __name__ == "__main__":
    main()
