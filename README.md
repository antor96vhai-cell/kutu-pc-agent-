# 🤖 KUTU PC Agent

Tomar nijer voice assistant — reels e je rokom **Max / Nova agent** dekho, thik oirokom!
Mic e bolba **"Kutu"** — se jagbe, tomar kotha shunbe, kaj korbe, ar mukhe jawab debe. (Recognizer majhe majhe "Kutu" ke "কুটুক" / "কটু" emon shune — shegulo bolleo jagbe, chinta nai.)
Bangla ar English — dui tai bujhe. Owner: **Antor**.

---

## Ki ki korte pare?

- 🎬 "Kutu, YouTube kholo" — YouTube / Facebook / Instagram / Gmail / Discord khule debe
- 🎵 "Kutu, [gaan er naam] chalao" — YouTube e search kore video chaliye debe
- 🔍 "Kutu, Google e [jinish] search koro"
- 🖥️ Notepad, Calculator, File Explorer, VS Code khulte pare
- 🔊 Volume barano / komano / mute
- 📸 "Screenshot nao" — Pictures folder e save kore debe
- ⌨️ "Type ..." bolle likhe debe
- 🕐 Somoy ar tarikh bolte pare
- 💬 Jekono proshno — Gemini AI diye choto kore jawab (mone rekho, voice e bole bole!)

---

## 🆕 v2 — Ekhon "ja bolba tai korbe" (Agent Mode)

Age KUTU sudhu fixed command bujhto. **v2 theke se screen DEKHE nije nije kaj korte pare** —
mouse chalabe, click korbe, type korbe, file banabe/muchbe, command chalabe.
Mane reels e je rokom dekho "PC, eta kore dao" — thik oirokom!

### Example — egulo age partona, ekhon pare:

| Bolo | Ki korbe |
|---|---|
| Kutu, **Discord er call ta kete dao** | Discord khule call er disconnect button nije khuje chap debe |
| Kutu, **Downloads e 'movies' name ekta folder banao** | File Explorer / command diye folder baniye debe |
| Kutu, **amar site ta Chrome e kholo** | Chrome khule tomar site (antorbio.qzz.io) khule debe |
| Kutu, **screen e ja dekhteso bolo** | Screen dekhe mukhe bole debe ekhane ki ki ache |
| Kutu, **Notepad e ekta note likhe save koro** | Notepad khule, likhe, file save kore debe |
| Kutu, **ei app ta bondho koro** | App ta puropuri close kore debe (age jiggesh kore!) |

### Kivabe kaj kore?

1. Tumi bolo → KUTU **screenshot** niye screen ta "dekhe"
2. Ekta step kore (click / type / scroll...) → abar screenshot niye check kore thik holo kina
3. Eivabe step by step kaj sesh kore, seshe mukhe bole result

Kalo window tay **proti step er log** dekhte parba — jemon `🖱️ click(...)`, `⌨️ type_text(...)` —
mane se ki kortese sob chokher samne, lukano kichu nai.

### ⚠️ Bipodjonok kaj e age jiggesh korbe (Confirmation)

Kichu kaj ulta kora jay na — egular age KUTU **mukhe bole jiggesh korbe**: *"Korbo?"*

- App puropuri bondho kora (close)
- Computer command chalano (PowerShell)
- File lekha / save kora
- **File delete kora**

Tokhon mic e bolo:
- **"Ha" / "Koro"** → kaj ta korbe ✅
- **"Na"** → oi step ta batil, korbe na ❌
- Kichu na bolle / bujha na gele → **safety r jonno korbei na**

Ar kichu kaj **kokhonoi korbe na** — tumi bolleo na: Windows er system folder e kichu delete,
puro drive format, eisob catastrophic kaj code diyei atkano ache.

### 🛑 Majhkhane thamate chaile

- Confirmation er somoy **"Tham"** bolo → puropuri theme jabe
- Na hoy kalo window te **Ctrl+C** chap dao
- Na hoy **mouse ta screen er ekdom konay** (uporer bam corner) niye jao → sob theme jabe sathe sathe

### 💸 Ekta honest kotha (quota)

Agent mode e **proti step e ekta kore screenshot Gemini ke pathate hoy** — tai free quota
shohoj command er cheye **tarahura sesh hoy**. Quota sesh hoye gele KUTU mukhei bole debe,
tokhon boro kaj hobe na — kinto shohoj command (somoy, app khola, gaan chalano) choltei thakbe.
Porer din quota abar full hoye jay.

---

## Setup — Step by Step (10 minute lagbe)

### Step 0: GitHub theke Download koro

1. GitHub e project er page e jao
2. Sobuj **`< > Code`** button e click koro
3. **Download ZIP** click koro
4. ZIP file ta **Extract / Unzip** koro (right-click → Extract All)
5. Folder ta emon jaygay rakho jekhane thakbe (jemon Desktop)

### Step 1: Python install koro

1. [python.org/downloads](https://www.python.org/downloads/) theke Python download kore install koro
2. ⚠️ **SOBCHEYE IMPORTANT:** Install er prothom screen e niche
   **"Add python.exe to PATH"** lekha ekta box thakbe — **oitay obosshoi tick (✓) dio!**
   Na dile kichui cholbe na.

### Step 2: setup.bat chalao

1. Unzip kora folder ta kholo
2. **setup.bat** file e **double-click** koro
3. Ekta kalo window khulbe, library install hobe — **2-5 minute** lagte pare, wait koro
4. "SETUP SESH!" dekhle bujhba hoye geche

> Windows jodi "Windows protected your PC" warning dey → **More info** → **Run anyway** click koro. Eta nijer banano file, safe.

### Step 3: Free Gemini API key nao

Brain er jonno Google Gemini er ekta **free** key lagbe. Taka lage na!

1. Browser e jao: [aistudio.google.com](https://aistudio.google.com)
2. Google account diye sign in koro
3. **"Get API key"** button e click koro → **"Create API key"**
4. Ekta lomba key dekhabe — **copy** koro
5. Ekhon project folder er **`.env`** file ta **Notepad** diye kholo
   (dekhte na pele: folder er upore **View → Show → File name extensions / Hidden items** on koro)
6. Ei line tay key ta boshao:
   ```
   GEMINI_API_KEY=ekhane_tomar_key_paste_koro
   ```
7. **Save** koro (Ctrl+S)

> 🔐 Key ta **karo sathe share koro na** — eta tomar personal key. GitHub eo eta kokhono upload hobe na (`.gitignore` diye atkano ache).

### Step 4: run.bat chalao — KUTU jinda!

1. **run.bat** double-click koro
2. Window e KUTU greeting bolbe: *"Assalamu Alaikum Antor! Ami Kutu, ready achi."*
3. Ekhon mic e bolo: **"Kutu, YouTube kholo"** 🎉

Bondho korte: bolo **"Kutu, goodbye"** — othoba window ta cross (X) diye bondho kore dao.

---

## Kivabe kotha bolba (Example commands)

| Bangla | English |
|---|---|
| Kutu, YouTube kholo | Kutu, open YouTube |
| Kutu, Arijit Singh er gaan chalao | Kutu, play Arijit Singh songs |
| Kutu, ekhon koyta baje? | Kutu, what time is it? |
| Kutu, ajke koto tarikh? | Kutu, what's the date today? |
| Kutu, volume barao | Kutu, volume up |
| Kutu, screenshot nao | Kutu, take a screenshot |
| Kutu, notepad kholo | Kutu, open notepad |
| Kutu, Bangladesh er rajdhani ki? | Kutu, tell me a joke |
| Kutu, goodbye | Kutu, stop |

Age **"Kutu"** bole jagate hobe — na jagale se kichu shunbe na (eta iccha korei, jate ultapalta kothay kaj na kore).

---

## Setting bodlate chaile

`agent.py` file er ekdom upore **CONFIG** ongsho te sob ache:

- `LANG = "bn-BD"` — shona r language. Sudhu English bolle `"en-US"` kore dio
- `VOICE_BN` / `VOICE_EN` — mukhe jawab dewar voice. Onno voice dekhte: [Microsoft Edge voices list](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/language-support)
  - Voice niye note: Bangla reply Bangla voice e, English reply English voice e nije nijei select hoy — kichu korte hobe na!
- `APPS = {...}` — notun app/website jog korte chaile ek line add koro:
  ```python
  "spotify": ("url", "https://open.spotify.com"),
  ```

---

## Troubleshooting (Somossa hole)

### ❌ setup.bat e "Python pawa jay ni"
Python install koro ni, othoba install er somoy **"Add python.exe to PATH"** tick dao ni.
Python abar install koro, ebar tick diye. Tarpor setup.bat abar chalao.

### ❌ Prothom setup majhkhane theme gesilo? (purono pygame / PyAudio error)
Chinta nai — notun version e oi problem tai thik kore deya hoyeche. Ekhon mic ar
speaker er library gula **ready-made (wheel)** — kichui compile hobe na, tai
**notun Python (3.14) eo setup arame cholbe**.

Thik korar step:
1. GitHub theke **notun ZIP** ta download koro ar **ager folder er upor-ei Extract (overwrite)** koro.
   Tomar `.env` file (jekhane API key ache) ZIP er vitore nai — tai ota muche jabe na,
   jemon chilo thik temon-i thakbe.
2. Chaile folder er vitore `venv` folder ta delete kore dao.
   (Na korleo cholbe — notun setup.bat adha-setup er purono venv nijei muche notun kore banay.)
3. Abar **setup.bat** double-click koro — ebar "SETUP SESH!" porjonto jabe.

### ❌ setup.bat e "pyautogui" step e error ashle
PyAutoGUI library tar kono ready-made wheel nai — tai setup.bat e ota **alada ekta
step e** (Step B) install hoy. Chinta nai, eta pure Python, compile kichu lage na.
Step B fail korle internet connection ta check kore **setup.bat abar chalao**.

### ❌ "GEMINI_API_KEY pawa jay ni"
`.env` file e key bosau ni, othoba save koro ni. Step 3 abar dekho.
File er naam sudhu `.env` hote hobe — `env.txt` hole cholbe na!

### ❌ Gemini "quota exceeded" / jawab dicche na
Free key te protidin ekta limit thake. Sesh hoye gele **porer din** abar hobe.
Beshi use korle aistudio.google.com theke notun key baniye nite paro.

### ❌ "Model no longer available" error ashle
Bhoy nai — program chalu howar somoy nijei ekhonkar model khuje ney.
Google kokhono purono model bondho kore dile KUTU nijei notun model
bechhe nibe (kalo window te `🧠 Model:` line e kon model cholche dekha jay).
Code e kichu bodlate hobe na.

### ❌ Command diye atke thake / kichu hoy na
Notun version e common kaj (YouTube/app khola, time, screenshot, volume)
**local-ei** hoye jay — Gemini lagena. Baki command eo Gemini r jonno
sorboccho 45 second wait kore, tarpore nijei chara peye jay —
age r moto jhule thake na.

### ❌ Mic shune na / kichu bole na

Ekhon kalo window te nijei dekha jay KUTU ki shunlo:

- `🎧 Shunlam: "..."` — ei line asha mane mic kaj korche, KUTU tomar kotha
  shuneche. Ei line-tai na ashle bujhba mic thekei awaz dhukche na.
- `🎧 (kotha bujhlam na)` — awaz hoyeche, kintu kotha clear bujha jay ni.
  Mic er kache giye ektu poriskar kore bolo.
- Program chalu howar somoy **mic device er list** print hoy — jekhane **⭐**
  mark ache setai Windows er default mic. Screenshot pathale oi list dekhei
  bujha jabe kon mic ta select hoye ache.
- `(Mic ready - ghore r noise: 0, ...)` — **noise 0** mane mic theke **kono
  signal-i asche na** (puro digital silence). Mic lagano thakleo emon hoy
  jokhon Windows bhul input device select kore rakhe, othoba **mic privacy
  setting** diye desktop app er mic access bondho thake. Niche r 2 ta
  check koro:

**Check 1 — Windows mic privacy (sobcheye common karon):**
1. Settings → **Privacy & security** → **Microphone**
2. **"Microphone access"** → **On** koro
3. **"Let desktop apps access your microphone"** → **On** koro

**Check 2 — Thik mic ta default select kora ache kina:**
1. Settings → **System** → **Sound** → **Input**
2. List theke tomar **asol mic** ta select koro (laptop er built-in mic /
   headphone er mic)
3. Oikhane mic test er ekta **bar** ache — kotha bolle bar ta **norbe**.
   Bar na norle bujhba oi device diye awaz dhukche na, onno mic select koro

- Laptop er **Fn + mic-mute** key chaap poreche kinao dekho (kichu laptop e thake)
- Chupchap jaygay bolo, mic er kache bolo
- Speaker/headphone er volume on ache kina dekho

### ❌ Internet chara cholbe?
Na. Voice shona (Google), bolа (edge-tts), ar brain (Gemini) — tintai online service. Internet lagbei.

---

## File gula ki ki

| File | Kaj |
|---|---|
| `agent.py` | Asol program — sob kaj ekhanei |
| `setup.bat` | Prothom bar double-click — sob install kore |
| `run.bat` | Protidin double-click — KUTU chalu hoy |
| `.env` | Tomar secret API key (tumi banaba) |
| `.env.example` | .env er khali copy |
| `requirements.txt` | Library er list |
| `README.md` | Ei file tai |

---

*Banaise KUTU, Antor er jonno. Moja koro! 🎧*
