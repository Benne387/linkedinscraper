# [>>>] Quick Start - LinkedIn Scraper mit n8n

## WICHTIG: Fehlerbehandlung für fehlende Person-Attribute

Die `joeyism/linkedin_scraper` Library gibt manchmal nicht alle Attribute zurück (z.B. `location`). Das ist normal und wird jetzt automatisch behandelt mit `getattr()` und Fallbacks auf `"N/A"`.

---

## Schritt 1 - Session erstellen (nur 1x notwendig!)

```powershell
cd C:\Users\benedikt.heinen\python\linkedinscraper
python scrape_batch.py https://linkedin.com/in/beliebig
```

- Browser öffnet sich
- Du loggst dich manuell ein
- 2FA Code eingeben (wenn nötig)
- Script speichert Session in `linkedin_session/cookies.json`

**Fertig! Session ist nun gültig für ~30 Tage**

---

## Schritt 2 - Server starten (immer wenn du scrapst!)

```powershell
cd C:\Users\benedikt.heinen\python\linkedinscraper
python scrape_api.py
```

Output sollte sein:
```
[>>>] LinkedIn Scraper API v2.1 (SAFE - joeyism/linkedin_scraper)
[*] API laeuft auf: http://localhost:5000
```

**Terminal offen halten!**

---

## Schritt 3 - ngrok Tunnel starten (in neuem Terminal!)

```powershell
ngrok http 5000
```

Output:
```
Forwarding    https://xxx.ngrok-free.dev -> http://localhost:5000
```

**Diese URL in n8n nutzen!**

---

## Schritt 4 - In n8n verwenden

### Single Profile:
```
POST https://xxx.ngrok-free.dev/scrape
Body: {"url": "https://linkedin.com/in/profil"}
```

### Batch (mehrere):
```
POST https://xxx.ngrok-free.dev/scrape/batch
Body: {"urls": ["https://linkedin.com/in/profil1", "https://linkedin.com/in/profil2"]}
```

---

## ⚠️ Wichtig

- **Session erneuern**: Nach ~30 Tagen → `python scrape_batch.py <url>` erneut ausführen
- **Beide Terminal offen**: Server + ngrok müssen laufen
- **ngrok URL aendert sich**: Nach jedem Neustart neue URL → n8n aktualisieren
- **Rate Limiting**: Nicht zu viele Anfragen (LinkedIn blockiert nach ~100/Stunde)
- **Private Profile**: Manche Felder können "N/A" sein wenn das Profil privat ist

---

## [ERROR] Troubleshooting

### "Verbindung kann nicht hergestellt werden"
→ Sicherstellen dass Terminal mit `python scrape_api.py` noch läuft
→ Chrome braucht Zeit zum Start (30-60 Sekunden bei erstem Request)

### "SESSION_EXPIRED"
→ `python scrape_batch.py https://linkedin.com/in/beliebig` neu ausführen

### "ngrok offline"
→ Terminal mit ngrok neu starten: `ngrok http 5000`

### "API not found"
→ Sicherstellen dass `python scrape_api.py` läuft

### "'Person' object has no attribute 'location'"
→ Das ist normal! Wird jetzt automatisch mit "N/A" ersetzt
→ Passiert bei privaten Profilen oder wenn LinkedIn Daten nicht freigibt

---

**Fertig! Viel Erfolg! [OK]**
