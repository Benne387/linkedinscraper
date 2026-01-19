# LinkedIn Scraper - Vollständiges Setup

## 📋 Installation

### 1. Python Abhängigkeiten installieren

```bash
pip install selenium requests lxml webdriver-manager
```

Oder kurz:
```bash
pip install -r requirements.txt
pip install webdriver-manager
```

### 2. ChromeDriver (NICHT notwendig!)
Mit `webdriver-manager` wird der ChromeDriver automatisch heruntergeladen. Du musst nichts manuell installieren!

## 🚀 Verwendung

### Einfach das Script ausführen:

```bash
python scrape_profile.py
```

### Das Script fragt dann nach:
1. **LinkedIn Email** - Deine Email-Adresse
2. **LinkedIn Passwort** - Dein Passwort
3. **Profil-URL** - z.B. `https://www.linkedin.com/in/dein-profil/`

### Beispiel:
```
🚀 LinkedIn Profile Scraper
==================================================
⏳ Chrome wird gestartet...
📧 LinkedIn Email: dein-email@example.com
🔐 LinkedIn Passwort: ••••••••
⏳ Melde dich an...
✅ Login erfolgreich!
🔗 LinkedIn Profil-URL eingeben: https://www.linkedin.com/in/andre-iguodala-65b48ab5
```

## 📁 Output

Die gescrapten Daten werden gespeichert in:
```
scraped_data/profil_name_YYYYMMDD_HHMMSS.json
```

## ⚙️ Umgebungsvariablen (Optional)

Du kannst auch Umgebungsvariablen setzen, um nicht jedes Mal die Anmeldedaten einzugeben:

**Windows (PowerShell):**
```powershell
$env:LINKEDIN_USER = "deine-email@example.com"
$env:LINKEDIN_PASSWORD = "dein-passwort"
python scrape_profile.py
```

**Windows (CMD):**
```cmd
set LINKEDIN_USER=deine-email@example.com
set LINKEDIN_PASSWORD=dein-passwort
python scrape_profile.py
```

**Linux/Mac:**
```bash
export LINKEDIN_USER="deine-email@example.com"
export LINKEDIN_PASSWORD="dein-passwort"
python scrape_profile.py
```

## 🔍 Was wird gescraped?

- ✅ Name
- ✅ Job Titel
- ✅ Unternehmen
- ✅ About-Sektion
- ✅ Berufserfahrungen
- ✅ Ausbildung
- ✅ Interessen

## ⚠️ Wichtig

- LinkedIn ändert ständig seine Website - das Script könnte mal nicht funktionieren
- LinkedIn hat Nutzungsbedingungen - bitte beachten!
- Verwende deine echten Anmeldedaten (nicht speichern in Code!)
- Zu viele Scraping-Anfragen können zum Sperren führen

## 🆘 Probleme?

Falls das Script nicht funktioniert:

1. Browser-Fenster öffnet sich aber nichts passiert?
   - LinkedIn hat möglicherweise das Sicherheits-Pop-up aktiviert
   - Manuell bestätigen oder einmalig einloggen

2. "Element not found" Fehler?
   - LinkedIn hat möglicherweise die Website aktualisiert
   - Das Script muss angepasst werden

3. Zugriff verweigert?
   - Passwort falsch
   - Profil ist privat
   - IP ist geblockt

## 📝 Schnelles Test-Script

Möchtest du zuerst nur testen, ob alles funktioniert?

```python
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
print("✅ Chrome erfolgreich gestartet!")
driver.quit()
```

## 💡 Tipps

- Das Script speichert Daten als JSON - einfach zu verarbeiten
- Du kannst die Daten dann mit Python, Excel, etc. analysieren
- Für mehrere Profile einfach wieder starten
