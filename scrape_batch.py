#!/usr/bin/env python3
"""
LinkedIn Scraper für n8n - Batch Processing
- Speichert Session/Cookies persistent
- Login nur einmalig notwendig
- Akzeptiert URLs als CLI-Argumente
- Nutzt joeyism/linkedin_scraper Library für bessere Datenqualität
"""

import os
import json
import time
import sys
from datetime import datetime
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from linkedin_scraper import Person


class LinkedInScraperBatch:
    """LinkedIn Profile Scraper für Batch-Processing"""
    
    # Speicherpfade
    COOKIES_DIR = "linkedin_session"
    COOKIES_FILE = os.path.join(COOKIES_DIR, "cookies.json")
    
    def __init__(self):
        self.driver = None
        self.name = "N/A"
        self.location = "N/A"
        self.about = "N/A"
        self.job_title = "N/A"
        self.company = "N/A"
        self.experiences = []
        self.educations = []
        
        # Stelle sicher dass Cookies-Verzeichnis existiert
        os.makedirs(self.COOKIES_DIR, exist_ok=True)
    
    def setup_driver(self):
        """Chrome WebDriver Setup"""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        
        self.driver = webdriver.Chrome(options=chrome_options)
    
    def save_cookies(self):
        """Speichert Cookies nach dem Login"""
        try:
            cookies = self.driver.get_cookies()
            with open(self.COOKIES_FILE, 'w') as f:
                json.dump(cookies, f)
            print(f"[OK] Session gespeichert in: {self.COOKIES_FILE}")
        except Exception as e:
            print(f"[ERROR] Fehler beim Speichern der Cookies: {e}")
    
    def load_cookies(self):
        """Lädt gespeicherte Cookies"""
        if os.path.exists(self.COOKIES_FILE):
            try:
                self.driver.get("https://www.linkedin.com")
                time.sleep(1)
                
                with open(self.COOKIES_FILE, 'r') as f:
                    cookies = json.load(f)
                
                for cookie in cookies:
                    try:
                        self.driver.add_cookie(cookie)
                    except:
                        pass  # Ignoriere abgelaufene Cookies
                
                print("[OK] Session geladen")
                return True
            except Exception as e:
                print(f"⚠️  Fehler beim Laden der Cookies: {e}")
                return False
        return False
    
    def check_login(self):
        """Prüft ob man eingeloggt ist"""
        try:
            self.driver.get("https://www.linkedin.com/feed/")
            time.sleep(2)
            
            # Wenn wir auf Login-Seite sind, sind wir nicht eingeloggt
            if "login" in self.driver.current_url.lower():
                return False
            
            # Prüfe ob Feed lädt
            self.driver.find_element(By.TAG_NAME, "main")
            return True
        except:
            return False
    
    def login(self):
        """Mit LinkedIn einloggen - MANUELL"""
        print("\n" + "="*60)
        print("LinkedIn Login erforderlich")
        print("="*60)
        
        self.driver.get("https://www.linkedin.com/login")
        
        print("\n📋 Bitte einloggen im Browser:")
        print("1. ✏️  Gib deine E-Mail ein")
        print("2. [PASS] Gib dein Passwort ein")
        print("3. 📱 Wenn 2FA kommt: Authenticator App öffnen + Code eingeben")
        print("4. [OK] Drücke Enter wenn du eingeloggt bist")
        print("="*60)
        
        input("\n▶️  Drücke Enter wenn du eingeloggt bist...")
        
        # Speichern nach erfolgreicherem Login
        time.sleep(2)
        self.save_cookies()
        print("[OK] Login erfolgreich und Session gespeichert!\n")
    
    def scrape_profile(self, profile_url):
        """Profil scrapen mit joeyism/linkedin_scraper Library"""
        print(f"\n[*] Scrape: {profile_url}")
        
        try:
            person = Person(
                linkedin_url=profile_url,
                driver=self.driver,
                scrape=True,
                close_on_complete=False
            )
            
            # Speichere Cookies
            try:
                with open(self.COOKIES_FILE, 'w') as f:
                    json.dump(self.driver.get_cookies(), f)
            except:
                pass
            
            # Extrahiere Daten - mit sicherer Attribut-Pruefung
            self.name = getattr(person, 'name', None) or "N/A"
            self.job_title = getattr(person, 'job_title', None) or "N/A"
            self.company = getattr(person, 'company', None) or "N/A"
            self.location = getattr(person, 'location', None) or "N/A"
            
            # About - sicher extrahieren
            about = getattr(person, 'about', None)
            self.about = about[0] if about and len(about) > 0 else "N/A"
            
            # Experiences - mit sicherer Attribut-Pruefung
            self.experiences = []
            experiences = getattr(person, 'experiences', None)
            if experiences:
                for exp in experiences:
                    self.experiences.append({
                        "position_title": getattr(exp, 'position_title', None) or "N/A",
                        "institution_name": getattr(exp, 'institution_name', None) or "N/A",
                        "from_date": getattr(exp, 'from_date', None) or "N/A",
                        "to_date": getattr(exp, 'to_date', None) or "N/A",
                        "duration": getattr(exp, 'duration', None) or "N/A",
                        "location": getattr(exp, 'location', None) or "N/A"
                    })
            
            # Educations - mit sicherer Attribut-Pruefung
            self.educations = []
            educations = getattr(person, 'educations', None)
            if educations:
                for edu in educations:
                    self.educations.append({
                        "institution_name": getattr(edu, 'institution_name', None) or "N/A",
                        "degree": getattr(edu, 'degree', None) or "N/A",
                        "from_date": getattr(edu, 'from_date', None) or "N/A",
                        "to_date": getattr(edu, 'to_date', None) or "N/A"
                    })
            
            return True
        
        except Exception as e:
            print(f"[ERROR] Fehler beim Scrapen: {e}")
            return False
    
    def extract_data(self):
        """Legacy Methode - nicht mehr benutzt"""
        pass
    
    def to_dict(self, profile_url):
        """Konvertiert zu Dictionary"""
        return {
            "timestamp": datetime.now().isoformat(),
            "name": self.name,
            "linkedin_url": profile_url,
            "company": self.company,
            "job_title": self.job_title,
            "location": self.location,
            "about": self.about,
            "experiences": self.experiences,
            "educations": self.educations
        }
    
    def close(self):
        """Browser schließen"""
        if self.driver:
            self.driver.quit()


def scrape_url(profile_url):
    """Hauptfunktion für eine URL - kann von außen aufgerufen werden"""
    scraper = LinkedInScraperBatch()
    
    try:
        # Setup
        scraper.setup_driver()
        
        # Versuche gespeicherte Session zu laden
        session_loaded = scraper.load_cookies()
        
        # Prüfe ob Session gültig ist
        if not scraper.check_login():
            if session_loaded:
                print("⚠️  Session abgelaufen - Neu einloggen...")
            else:
                print("⚠️  Keine gespeicherte Session gefunden")
            
            print("[ERROR] Nicht eingeloggt - Bitte manuell einloggen")
            scraper.login()
        
        # Scrape
        if scraper.scrape_profile(profile_url):
            data = scraper.to_dict(profile_url)
            print(f"[OK] Erfolgreich: {data['name']}")
            return data
        else:
            print(f"[ERROR] Scrapen fehlgeschlagen: {profile_url}")
            return None
    
    except Exception as e:
        print(f"[ERROR] Fehler: {e}")
        return None
    
    finally:
        scraper.close()


def main():
    """CLI - Akzeptiert URLs als Argumente"""
    if len(sys.argv) < 2:
        print("[ERROR] Fehler: Keine URLs angegeben!")
        print("\nVerwendung:")
        print("  python scrape_batch.py <url1> <url2> <url3> ...")
        print("\nBeispiel:")
        print("  python scrape_batch.py https://linkedin.com/in/profile1 https://linkedin.com/in/profile2")
        sys.exit(1)
    
    # URLs aus Kommandozeile
    urls = sys.argv[1:]
    
    print("\n" + "="*60)
    print(f"[>>>] LinkedIn Batch Scraper - {len(urls)} URLs")
    print("="*60)
    
    results = []
    
    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] Verarbeite: {url}")
        result = scrape_url(url)
        
        if result:
            results.append(result)
            # Speichern
            os.makedirs("scraped_data", exist_ok=True)
            filename = f"scraped_data/{result['name'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"[SAVE] Gespeichert: {filename}")
    
    # Summary
    print("\n" + "="*60)
    print(f"[DONE] FERTIG: {len(results)}/{len(urls)} Profile gescraped")
    print("="*60)
    
    # Output als JSON für n8n
    output = {
        "timestamp": datetime.now().isoformat(),
        "total": len(urls),
        "success": len(results),
        "results": results
    }
    
    print("\n[JSON] Output:")
    print(json.dumps(output, indent=2, ensure_ascii=False))
    
    return output


if __name__ == "__main__":
    main()
