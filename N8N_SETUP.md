# LinkedIn Scraper für n8n - Setup Guide

## 🎯 Wie es funktioniert

### 1️⃣ **Erste Nutzung - Session erstellen**
```powershell
python scrape_batch.py https://linkedin.com/in/profile1 https://linkedin.com/in/profile2
```

Das Script wird:
- Browser öffnen
- Dich auffordern manuell einzuloggen (inklusive 2FA)
- Session/Cookies in `linkedin_session/cookies.json` speichern
- Profile scrapen und in `scraped_data/` speichern

### 2️⃣ **n8n Integration**

#### Option A: Über CLI (einfacher)
```powershell
python scrape_n8n.py "https://linkedin.com/in/someprofile"
```

**n8n Workflow Setup:**
1. "Execute Command" Node mit:
   ```
   cmd /c python scrape_n8n.py "{{$json.profile_url}}"
   ```
2. Output ist JSON:
   ```json
   {
     "status": "success",
     "name": "John Doe",
     "company": "Tech Corp",
     "job_title": "Software Engineer",
     "location": "Berlin",
     "experiences": [...],
     "educations": [...]
   }
   ```

#### Option B: Über HTTP/Webhook (für Hetzner)
```bash
# Installiere Flask wenn nicht vorhanden
pip install flask

# Starte Server
python scrape_api.py
# Läuft auf http://localhost:5000/scrape
```

n8n HTTP Request:
```
POST http://deine-hetzner-ip:5000/scrape
Body: {"url": "https://linkedin.com/in/profile"}
```

---

## 🔑 Wichtig: Login & 2FA

### Erste Session erstellen (einmalig):
```powershell
python scrape_batch.py https://linkedin.com/in/test
```
→ Browser öffnet sich → **Du loggst mich manuell ein** → Script speichert Session

### Weitere Scrapes (automatisch):
```powershell
python scrape_n8n.py https://linkedin.com/in/profile1
python scrape_n8n.py https://linkedin.com/in/profile2
python scrape_n8n.py https://linkedin.com/in/profile3
```
→ Alle verwenden die **gleiche gespeicherte Session** → **Kein Login nötig!**

---

## 📁 Dateistruktur

```
linkedinscraper/
├── scrape_batch.py          ← Mehrere URLs auf einmal (CLI)
├── scrape_n8n.py            ← Einzelne URL für n8n (CLI)
├── scrape_api.py            ← HTTP API für Webhooks (optional)
├── linkedin_session/
│   └── cookies.json         ← Gespeicherte Session (AUTO)
└── scraped_data/
    ├── John_Doe_20251221_195341.json
    ├── Jane_Smith_20251221_195342.json
    └── ...
```

---

## 🚀 n8n Workflow Beispiel

### Einfache Batch-Verarbeitung:

```
┌─────────────────────────────┐
│  Start - URL Liste          │
│  (z.B. aus CSV oder DB)     │
└──────────────┬──────────────┘
               │
       ┌───────▼────────┐
       │  For Each URL  │
       └───────┬────────┘
               │
       ┌───────▼─────────────────┐
       │  Execute Command:       │
       │  python scrape_n8n.py   │
       │  "{{$json.url}}"        │
       └───────┬─────────────────┘
               │
       ┌───────▼────────────────┐
       │  Parse JSON Output     │
       │  (name, company, etc)  │
       └───────┬────────────────┘
               │
       ┌───────▼────────────────┐
       │  Speichern in DB       │
       │  oder Export zu CSV    │
       └────────────────────────┘
```

---

## ⚠️ Wichtige Hinweise

### Session-Ablauf
- Sessions halten ~30 Tage
- Wenn Session abläuft: Erneut `scrape_batch.py` mit einer URL ausführen → neu einloggen
- Session wird automatisch erneuert

### LinkedIn Limits
- ⚠️ LinkedIn blockiert aggressive Scraper
- **Empfehlung:** 1-2 Sekunden Pause zwischen Profilen
- Verwende **Delays** in n8n: `Wait` Node mit 2-3 Sekunden

### Fehlerbehandlung
```json
{
  "status": "error",
  "error": "SESSION_EXPIRED - Bitte erneut manuell einloggen",
  "url": "https://linkedin.com/in/profile"
}
```

---

## 🔄 Workflow-Beispiele

### CSV mit URLs durchgehen:
```
URL
https://linkedin.com/in/profile1
https://linkedin.com/in/profile2
https://linkedin.com/in/profile3
```

n8n:
1. Read CSV
2. For Each Row
3. Execute Command: `python scrape_n8n.py "{{$json.URL}}"`
4. Write to CSV/DB

### Mit Hetzner Automation:
```
Hetzner Console → Cloud Init Script
```

---

## 🐛 Troubleshooting

### "NO_SESSION - Führe scrape_batch.py aus"
→ Erste Nutzung? Führe `python scrape_batch.py <url>` aus und melde dich an

### "SESSION_EXPIRED"
→ Session ist älter als 30 Tage. Wiederhole `scrape_batch.py` zum neu einloggen

### Browser öffnet nicht
→ Prüfe ob Chrome installiert ist: `chrome --version`

### Selenium Timeout
→ LinkedIn ist langsam. Erhöhe Waits in scrape_n8n.py

---

## 📞 Support

Fehlermeldung mit:
```powershell
python scrape_batch.py <url> 2>&1 | Out-File debug.log
```

---

**Viel Erfolg mit n8n! 🚀**
