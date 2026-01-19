#!/usr/bin/env python3
"""
LinkedIn Profile Scraper - Basierend auf joeyism/linkedin_scraper Library
Nutzt die gleiche Approach wie die echte Library
"""

import os
import json
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service


class LinkedInScraper:
    """LinkedIn Profile Scraper - Vereinfachte Version"""
    
    def __init__(self):
        self.driver = None
        self.name = "N/A"
        self.location = "N/A"
        self.about = "N/A"
        self.job_title = "N/A"
        self.experiences = []
        self.educations = []
    
    def setup_driver(self):
        """Chrome WebDriver Setup"""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
    
    def login(self):
        """Mit LinkedIn einloggen - MANUELL"""
        print("\n" + "="*60)
        print("LinkedIn Login - MANUELL")
        print("="*60)
        
        self.driver.get("https://www.linkedin.com/login")
        
        print("\n📋 ANLEITUNG:")
        print("1. ✏️  Gib deine E-Mail ein")
        print("2. 🔐 Gib dein Passwort ein")
        print("3. 📱 Wenn 2FA kommt: Authenticator App öffnen + Code eingeben")
        print("4. ⏳ Warte bis du auf LinkedIn bist")
        print("5. ⌨️  Drücke Enter im Terminal wenn du fertig bist")
        print("="*60)
        
        input("\n▶️  Drücke Enter wenn du eingeloggt bist...")
        print("✅ Login erkannt!\n")
    
    def scrape_profile(self, profile_url):
        """Profil scrapen"""
        print("="*60)
        print("Profil wird gescraped...")
        print("="*60)
        
        print(f"📍 Öffne: {profile_url}")
        self.driver.get(profile_url)
        
        # Warten auf Profil
        print("⏳ Warte auf Profildaten...")
        try:
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "h1"))
            )
            print("✅ Profil geladen")
        except:
            print("⚠️  Timeout beim Warten auf Profil")
        
        time.sleep(2)
        
        # Scroll
        print("📜 Lade weitere Inhalte...")
        for _ in range(3):
            self.driver.execute_script("window.scrollBy(0, 500);")
            time.sleep(1)
        
        self.driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
        
        # Scrape
        self.extract_profile_data()
    
    def extract_profile_data(self):
        """Extrahiert die Profil-Daten"""
        
        # 1. Name
        try:
            name_elem = self.driver.find_element(By.TAG_NAME, "h1")
            self.name = name_elem.text.strip()
            print(f"✓ Name: {self.name}")
        except Exception as e:
            print(f"✗ Name: {e}")
        
        # 2. Job Title - Suche nach Berufstitel  
        try:
            # Hole den kompletten Text vom Top-Card
            top_card_text = self.driver.find_element(By.TAG_NAME, "main").text
            lines = top_card_text.split('\n')
            
            # Job Title ist normalerweise die 2. oder 3. Zeile (nach Name)
            for i, line in enumerate(lines[:10]):
                line = line.strip()
                # Skip Name und leere Zeilen
                if line and line != self.name and len(line) < 150:
                    # Ignoriere typische Navigation/UI Elemente
                    if not any(x in line.lower() for x in ['connections', 'followers', 'edit', 'open to']):
                        # Könnte Job Title sein
                        if any(x in line.lower() for x in ['director', 'manager', 'engineer', 'developer', 'analyst', 'specialist', 'coordinator', 'consultant', 'officer', 'head']):
                            self.job_title = line
                            print(f"✓ Job Title: {self.job_title}")
                            break
        except Exception as e:
            print(f"✗ Job Title: {e}")
        
        # 3. Location
        try:
            # Suche nach Text mit Komma (typisch für Orte)
            top_card_text = self.driver.find_element(By.TAG_NAME, "main").text
            lines = top_card_text.split('\n')
            
            for i, line in enumerate(lines[:20]):
                line = line.strip()
                # Location hat normalerweise ein Komma und ist nicht zu lang
                # Und sollte NICHT der Job Title sein
                if ("," in line and 5 < len(line) < 80 and 
                    line != self.job_title and 
                    not any(x in line.lower() for x in ['followers', 'connections', 'react', 'comment', 'share', 'director', 'manager', 'engineer', 'developer'])):
                    self.location = line
                    print(f"✓ Location: {self.location}")
                    break
        except Exception as e:
            print(f"✗ Location: {e}")
        
        # 4. About
        try:
            # Suche nach "About" Section
            about_labels = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'About')]")
            if about_labels:
                parent = about_labels[0].find_element(By.XPATH, "../..")
                paragraphs = parent.find_elements(By.TAG_NAME, "p")
                if paragraphs:
                    self.about = paragraphs[0].text.strip()
                    if self.about:
                        print(f"✓ About: {self.about[:50]}...")
        except Exception as e:
            print(f"✗ About: {e}")
        
        # 5. Experiences - navigiere zu Details/Experience
        try:
            exp_url = self.driver.current_url.rstrip('/') + "/details/experience"
            self.driver.get(exp_url)
            time.sleep(2)
            
            # Suche nach Experience Items
            main = self.driver.find_element(By.TAG_NAME, "main")
            exp_items = main.find_elements(By.XPATH, "//div[@data-view-name='profile-component-entity']")
            
            print(f"✓ Experiences: {len(exp_items)} gefunden")
            
            for item in exp_items[:10]:  # Erhöhe Limit auf 10
                try:
                    text = item.text.strip()
                    lines = [l.strip() for l in text.split('\n') if l.strip()]
                    
                    # Erste Zeile = Job Title, Zweite = Company
                    if len(lines) >= 2:
                        title = lines[0]
                        company = lines[1]
                        
                        # Nur basische Längen-Checks, keine zu strikte Filterung
                        if len(title) > 2 and len(company) > 2:
                            self.experiences.append({
                                "title": title,
                                "company": company,
                            })
                except Exception as err:
                    pass
        except Exception as e:
            print(f"✗ Experiences: {e}")
        
        # 6. Educations - navigiere zu Details/Education
        try:
            edu_url = self.driver.current_url.split('/details/')[0] + "/details/education"
            self.driver.get(edu_url)
            time.sleep(2)
            
            # Suche nach Education Items
            main = self.driver.find_element(By.TAG_NAME, "main")
            edu_items = main.find_elements(By.XPATH, "//div[@data-view-name='profile-component-entity']")
            
            print(f"✓ Educations: {len(edu_items)} gefunden")
            
            for item in edu_items[:5]:
                try:
                    text = item.text.strip()
                    lines = [l.strip() for l in text.split('\n') if l.strip()]
                    
                    # Erste Zeile sollte die Schule sein
                    if lines and len(lines[0]) > 3:
                        school = lines[0]
                        
                        # Ignoriere Namen von Personen (typisch < 30 Zeichen, keine Universität-Keywords)
                        if not any(keyword in school.lower() for keyword in ['university', 'schule', 'college', 'hochschule', 'school', 'institute', 'akademie', 'gymnasium']):
                            # Wahrscheinlich eine Person, skip
                            if len(school) > 50 or any(uni in school.lower() for uni in ['universität', 'university', 'hochschule', 'college', 'technische', 'ingenieur']):
                                self.educations.append({
                                    "school": school,
                                })
                        else:
                            # Hat University-Keyword, nehme es
                            self.educations.append({
                                "school": school,
                            })
                except Exception as err:
                    pass
        except Exception as e:
            print(f"✗ Educations: {e}")
    
    def to_dict(self):
        """Konvertiert zu Dictionary"""
        # Aktuelle Company = erste Experience (aktuelle Position)
        current_company = "N/A"
        if self.experiences:
            current_company = self.experiences[0].get("company", "N/A")
        
        return {
            "timestamp": datetime.now().isoformat(),
            "name": self.name,
            "linkedin_url": "",  # Wird später gesetzt
            "company": current_company,
            "job_title": self.job_title,
            "location": self.location,
            "about": self.about,
            "experiences": self.experiences,
            "educations": self.educations,
        }
    
    def save_data(self, profile_url):
        """Speichert Daten als JSON"""
        data = self.to_dict()
        data["linkedin_url"] = profile_url
        
        os.makedirs("scraped_data", exist_ok=True)
        filename = f"scraped_data/{self.name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return filename, data
    
    def close(self):
        """Browser schließen"""
        if self.driver:
            self.driver.quit()


def print_profile(data):
    """Zeigt Profil schön an"""
    print("\n" + "="*60)
    print("📋 PROFIL-ZUSAMMENFASSUNG")
    print("="*60)
    print(f"👤 Name: {data.get('name', 'N/A')}")
    print(f"� LinkedIn URL: {data.get('linkedin_url', 'N/A')}")
    print(f"🏢 Company: {data.get('company', 'N/A')}")
    print(f"💼 Job Titel: {data.get('job_title', 'N/A')}")
    print(f"📍 Location: {data.get('location', 'N/A')}")
    
    about = data.get('about', 'N/A')
    if len(about) > 100:
        about = about[:100] + "..."
    print(f"📝 About: {about}")
    
    if data.get('experiences'):
        print(f"\n💡 Erfahrungen ({len(data['experiences'])}):")
        for i, exp in enumerate(data['experiences'][:5], 1):
            print(f"   {i}. {exp.get('title', 'N/A')} @ {exp.get('company', 'N/A')}")
    
    if data.get('educations'):
        print(f"\n🎓 Ausbildung ({len(data['educations'])}):")
        for i, edu in enumerate(data['educations'][:3], 1):
            print(f"   {i}. {edu.get('school', 'N/A')}")
    
    print("\n" + "="*60)


def main():
    """Hauptprogramm"""
    scraper = LinkedInScraper()
    
    try:
        print("\n" + "="*60)
        print("🚀 LinkedIn Profile Scraper")
        print("   (Basierend auf joeyism/linkedin_scraper)")
        print("="*60)
        
        # Setup
        print("\n⏳ Chrome wird gestartet...")
        scraper.setup_driver()
        
        # Login
        scraper.login()
        
        # Loop für mehrere Profile
        while True:
            # Profil-URL
            profile_url = input("\n🔗 LinkedIn Profil-URL eingeben (oder 'exit' zum Beenden): ").strip()
            if profile_url.lower() == 'exit':
                break
            
            if not profile_url:
                print("❌ Keine URL eingegeben!")
                continue
            
            # Scrape
            scraper.scrape_profile(profile_url)
            
            # Speichern
            filename, data = scraper.save_data(profile_url)
            
            # Anzeigen
            print_profile(data)
            
            print(f"\n✅ Daten gespeichert in: {filename}")
            
            # JSON
            print("\n📄 Komplette Daten (JSON):")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # Reset für nächstes Profil
            scraper = LinkedInScraper()
            scraper.driver = scraper.driver  # Behalte denselben Browser
            
            print("\n" + "="*60)
            print("Bereit für nächstes Profil!")
            print("="*60)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Abgebrochen vom Benutzer")
    except Exception as e:
        print(f"\n❌ Fehler: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n🛑 Browser wird geschlossen...")
        scraper.close()


if __name__ == "__main__":
    main()
