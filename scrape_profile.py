#!/usr/bin/env python3
"""
LinkedIn Profile Scraper - Vollständiges Script
Scrapet ein LinkedIn Profil und speichert die Daten
"""

import os
import json
import sys
from datetime import datetime
from linkedin_scraper import Person, actions
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


def setup_driver():
    """Chrome WebDriver mit optimalen Einstellungen erstellen"""
    chrome_options = Options()
    # Optional: "--headless" für unsichtbares Fenster
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    return driver


def login_to_linkedin(driver):
    """Mit LinkedIn anmelden - MANUELL"""
    print("\n" + "="*50)
    print("LinkedIn Login - MANUELL")
    print("="*50)
    print("\n🔗 Der Browser öffnet sich jetzt...")
    
    try:
        # LinkedIn-Login-Seite öffnen
        driver.get("https://www.linkedin.com/login")
        
        print("\n" + "="*50)
        print("📋 ANLEITUNG:")
        print("="*50)
        print("1. ✏️  Gib deine E-Mail ein")
        print("2. 🔐 Gib dein Passwort ein")
        print("3. 📱 Wenn 2FA kommt: Authenticator App öffnen + Code eingeben")
        print("4. ⏳ Warte bis du auf deinem Profil bist")
        print("5. ⌨️  Drücke Enter im Terminal wenn du fertig bist")
        print("="*50)
        
        input("\n▶️  Drücke Enter wenn du dich erfolgreich angemeldet hast...")
        
        print("✅ Login erfolgreich!")
        return True
    except Exception as e:
        print(f"❌ Fehler: {e}")
        return False


def scrape_profile(driver, profile_url):
    """LinkedIn Profil scrapen"""
    print("\n" + "="*50)
    print("Profil wird gescraped...")
    print("="*50)
    
    try:
        person = Person(profile_url, driver=driver)
        
        # Alle Daten sammeln
        profile_data = {
            "timestamp": datetime.now().isoformat(),
            "linkedin_url": profile_url,
            "name": person.name,
            "job_title": person.job_title,
            "company": person.company,
            "about": person.about,
            "experiences": [
                {
                    "title": exp.get("title"),
                    "company": exp.get("company"),
                    "duration": exp.get("duration"),
                    "location": exp.get("location"),
                }
                for exp in person.experiences
            ] if person.experiences else [],
            "educations": [
                {
                    "school": edu.get("school"),
                    "field_of_study": edu.get("field_of_study"),
                    "degree": edu.get("degree"),
                }
                for edu in person.educations
            ] if person.educations else [],
            "interests": person.interests if person.interests else [],
        }
        
        return profile_data
    
    except Exception as e:
        print(f"❌ Fehler beim Scrapen: {e}")
        return None


def save_data(data, filename=None):
    """Daten als JSON speichern"""
    if filename is None:
        name = data.get("name", "profile").replace(" ", "_")
        filename = f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    filepath = f"scraped_data/{filename}"
    os.makedirs("scraped_data", exist_ok=True)
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return filepath


def print_profile(data):
    """Profildaten schön anzeigen"""
    print("\n" + "="*50)
    print("📋 Profil-Übersicht")
    print("="*50)
    print(f"👤 Name: {data.get('name', 'N/A')}")
    print(f"💼 Job Titel: {data.get('job_title', 'N/A')}")
    print(f"🏢 Unternehmen: {data.get('company', 'N/A')}")
    print(f"📝 About: {(data.get('about', 'N/A')[:100] + '...' if len(data.get('about', '')) > 100 else data.get('about', 'N/A'))}")
    
    if data.get("experiences"):
        print(f"\n💡 Erfahrungen ({len(data['experiences'])} gefunden):")
        for i, exp in enumerate(data["experiences"][:3], 1):
            print(f"   {i}. {exp.get('title')} @ {exp.get('company')}")
        if len(data["experiences"]) > 3:
            print(f"   ... und {len(data['experiences']) - 3} weitere")
    
    if data.get("educations"):
        print(f"\n🎓 Ausbildung ({len(data['educations'])} gefunden):")
        for i, edu in enumerate(data["educations"][:3], 1):
            print(f"   {i}. {edu.get('school')}")
    
    print("\n" + "="*50)


def main():
    """Hauptprogramm"""
    driver = None
    
    try:
        print("\n🚀 LinkedIn Profile Scraper")
        print("="*50)
        
        # WebDriver starten
        print("⏳ Chrome wird gestartet...")
        driver = setup_driver()
        
        # Login
        if not login_to_linkedin(driver):
            return
        
        # Profil-URL eingeben
        print("\n" + "="*50)
        profile_url = input("🔗 LinkedIn Profil-URL eingeben: ").strip()
        
        if not profile_url:
            print("❌ Keine URL eingegeben!")
            return
        
        # Scrapen
        profile_data = scrape_profile(driver, profile_url)
        
        if profile_data:
            # Anzeigen
            print_profile(profile_data)
            
            # Speichern
            filepath = save_data(profile_data)
            print(f"\n✅ Daten gespeichert: {filepath}")
            
            # JSON ausgeben
            print(f"\n📄 Komplette Daten:")
            print(json.dumps(profile_data, indent=2, ensure_ascii=False))
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Abgebrochen vom Benutzer")
    except Exception as e:
        print(f"\n❌ Fehler: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if driver:
            print("\n🛑 Browser wird geschlossen...")
            driver.quit()


if __name__ == "__main__":
    main()
