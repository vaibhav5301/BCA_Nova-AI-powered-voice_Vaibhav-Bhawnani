<div align="center">

# 🌟 NOVA — AI Voice Assistant

**A smart, beautiful, always-listening AI assistant for Windows**  
*Powered by Groq · Llama 3.3 · Built by Anjali Saraswat*

[![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightblue?style=for-the-badge&logo=windows)](https://github.com)
[![AI](https://img.shields.io/badge/AI-Groq%20Llama%203.3-orange?style=for-the-badge)](https://groq.com)

</div>

---

## ✨ What is Nova?

Nova is a **free, open-source AI voice assistant** for Windows that you can run entirely on your own machine. Just say *"wake up Nova"* and start talking — she understands natural speech and can control your PC, search the web, tell you the weather, translate languages, send WhatsApp messages, and much more.

No subscriptions. No cloud sign-ups. Just download and run.

---

## 🚀 Quick Start

### Option A — One-Click Installer (Easiest)
1. Go to the [**Releases**](../../releases) page
2. Download `Nova_Setup.exe`
3. Double-click and install
4. Launch **Nova** from your Desktop shortcut
5. Say **"wake up Nova"** to begin!

### Option B — Run from Source (Developers)

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/Nova-Assistant.git
cd Nova-Assistant

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch the beautiful UI
python nova_ui.py

# OR launch in terminal mode (no UI)
python nova_assistant_v9.py
```

> **Requires Python 3.11+** — download from [python.org](https://python.org)

---

## 🎤 How to Use

| Step | What to do |
|------|-----------|
| 1 | Launch Nova (run `nova_ui.py` or open the app) |
| 2 | Click the **glowing orb** — or say **"wake up Nova"** |
| 3 | Speak any command (see full list below) |
| 4 | Nova replies and keeps listening |
| 5 | Say **"go to sleep"** to pause |

---

## 🌟 Features

| Category | What Nova can do |
|----------|-----------------|
| 🌤 **Weather** | Real-time weather for any city |
| 📰 **News** | Top 5 Indian headlines read aloud |
| 🧮 **Calculator** | Natural spoken math — "what is 15 percent of 200" |
| 🌍 **Translator** | Translates to 18+ languages instantly |
| 🎵 **Music** | Mood playlists, Spotify, YouTube, media keys |
| 💬 **WhatsApp** | Sends messages hands-free via WhatsApp Desktop |
| 📂 **Apps** | Opens & closes any Windows application |
| 🌐 **Browser** | Tabs, scroll, zoom, back/forward |
| 💡 **Brightness** | Controls screen brightness by voice |
| ⇥ **Tab Nav** | Full keyboard navigation by voice |
| 📊 **Excel** | Creates formatted spreadsheets |
| 📁 **Files** | Searches and opens files/folders |
| ⏰ **Reminders** | Sets timed voice reminders |
| 🤖 **AI Chat** | Powered by Groq (Llama 3.3) for anything else |

---

## 🗣 Voice Commands — Quick Reference

```
Wake/Sleep    →  "wake up Nova"  /  "go to sleep"
Weather       →  "what's the weather"  /  "weather in Delhi"
News          →  "read me the news"  /  "latest headlines"
Time/Date     →  "what time is it"  /  "what is today"
Calculator    →  "calculate 25 times 4"  /  "15 percent of 200"
Translator    →  "translate hello to Hindi"  /  "say thanks in French"
Music         →  "play happy music"  /  "play chill music"
WhatsApp      →  "send message to Rahul I will be late"
Open app      →  "open Chrome"  /  "open Notepad"  /  "open Spotify"
Close app     →  "close Chrome"  /  "kill Firefox"
Web search    →  "search Python tutorial"  /  "google machine learning"
Brightness    →  "increase brightness"  /  "set brightness to 70"
Screenshot    →  "take screenshot"
Tab nav       →  "start tab mode" → then say next/back/enter/stop
AI answer     →  Ask anything — "explain black holes"
Exit          →  "goodbye"  /  "exit"
```

📄 **Download the full command reference:** [`Nova_Voice_Commands.docx`](docs/Nova_Voice_Commands.docx)

---

## 📦 Project Structure

```
Nova-Assistant/
│
├── nova_assistant_v9.py   ← Core assistant engine
├── nova_ui.py             ← Beautiful PyQt6 UI
├── requirements.txt       ← All Python dependencies
├── README.md
├── LICENSE
└── docs/
    └── Nova_Voice_Commands.docx
```

---

## 🖥 System Requirements

| Requirement | Minimum |
|-------------|---------|
| OS | Windows 10 / 11 |
| Python | 3.11 or higher |
| RAM | 4 GB |
| Microphone | Any working mic |
| Internet | Required (for weather, news, AI, translation) |

---

## 🔧 Troubleshooting

**Nova can't hear me**
→ Check your mic is set as the default recording device in Windows Sound settings.

**"Module not found" error**
→ Run `pip install -r requirements.txt` again.

**Translator not working**
→ Make sure `deep-translator` is installed: `pip install deep-translator`

**Brightness control not working**
→ Some laptops need `screen-brightness-control` with admin rights. Right-click Nova and choose *Run as administrator*.

**WhatsApp messages not sending**
→ Make sure **WhatsApp Desktop** (not WhatsApp Web) is installed from the Microsoft Store.

---

## 📄 License

MIT License — free to use, modify, and share. See [LICENSE](LICENSE) for details.

---

<div align="center">

Made with ❤️ by **Anjali Saraswat**

*If you like Nova, give it a ⭐ on GitHub!*

</div>
