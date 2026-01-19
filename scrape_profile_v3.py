#!/usr/bin/env python3
"""
LinkedIn Profile Scraper V3 - Intelligente Selenium-basierte Extraktion
Nutzt Selenium um echte Profildaten direkt aus dem DOM zu lesen
"""

import os
import json
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


def setup_driver():
    """Chrome WebDriver mit optimalen Einstellungen erstellen"""
    chrome_options = Options()
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


def scrape_profile_direct(driver, profile_url):
    """LinkedIn Profil direkt mit Selenium auslesen"""
    print("\n" + "="*50)
    print("Profil wird gescraped...")
    print("="*50)
    
    try:
        # Profil-Seite öffnen
        print(f"📍 Öffne: {profile_url}")
        driver.get(profile_url)
        
        # Warten bis Profil geladen ist
        print("⏳ Warte auf Profildaten...")
        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        
        # Warte ein bisschen extra für JS Rendering
        time.sleep(2)
        
        print("✅ Profil geladen")
        
        # Scroll zu verschiedenen Abschnitten um JS zu triggern
        print("📜 Lade zusätzliche Inhalte...")
        
        # Scroll ein paar mal
        for i in range(3):
            driver.execute_script("window.scrollBy(0, 500);")
            time.sleep(1)
        
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
        
        # Jetzt die Daten direkt auslesen
        profile_data = extract_profile_data_direct(driver, profile_url)
        
        return profile_data
    
    except Exception as e:
        print(f"❌ Fehler beim Scrapen: {e}")
        import traceback
        traceback.print_exc()
        return None


def extract_profile_data_direct(driver, profile_url):
    """Extrahiert Profildaten direkt mit Selenium"""
    
    # Name
    try:
        name_elem = driver.find_element(By.TAG_NAME, "h1")
        name = name_elem.text.strip()
    except:
        name = "N/A"
    
    # Job Title - ist meist der erste Div nach h1
    job_title = "N/A"
    try:
        # Versuche verschiedene Methoden für Job Title
        # Methode 1: Direkter div nach h1
        try:
            job_elem = driver.find_element(By.CSS_SELECTOR, "h1 + div")
            job_title = job_elem.text.strip()
        except:
            pass
        
        # Methode 2: Suche nach Job-Text in der Seite
        if job_title == "N/A":
            all_text = driver.find_element(By.TAG_NAME, "body").text
            lines = all_text.split('\n')
            # Job Title ist meist eine der ersten 5 Zeilen nach dem Namen
            for i, line in enumerate(lines):
                if name in line and i+1 < len(lines):
                    next_line = lines[i+1].strip()
                    if next_line and len(next_line) < 100 and not any(x in next_line.lower() for x in ['followers', 'connections']):
                        job_title = next_line
                        break
    except:
        pass
    
    # Location
    location = "N/A"
    try:
        # Suche nach "area" Text oder Standort-Info
        body_text = driver.find_element(By.TAG_NAME, "body").text
        lines = body_text.split('\n')
        for line in lines[:30]:
            line = line.strip()
            if (',' in line or 'area' in line.lower()) and len(line) < 50 and len(line) > 3:
                if not any(x in line.lower() for x in ['followers', 'connections', 'react', 'share', 'comment']):
                    location = line
                    break
    except:
        pass
    
    # About - versuche verschiedene Methoden
    about = "N/A"
    try:
        # Methode 1: Suche nach h2 mit "About"
        try:
            about_headers = driver.find_elements(By.XPATH, "//h2[contains(text(), 'About')]")
            if about_headers:
                about_header = about_headers[0]
                parent = about_header.find_element(By.XPATH, "..")
                paragraphs = parent.find_elements(By.TAG_NAME, "p")
                if paragraphs:
                    about = paragraphs[0].text.strip()
        except:
            pass
        
        # Methode 2: Wenn h2 nicht funktioniert, suche nach großem Text-Block nach dem Header
        if about == "N/A":
            body_text = driver.find_element(By.TAG_NAME, "body").text
            lines = body_text.split('\n')
            # Suche nach "About" Text
            for i, line in enumerate(lines):
                if 'About' in line:
                    # Nächste nicht-leere Zeile sollte der About-Text sein
                    for j in range(i+1, min(i+5, len(lines))):
                        potential_about = lines[j].strip()
                        if len(potential_about) > 30:
                            about = potential_about
                            break
                    break
    except:
        pass
    
    # Experiences
    experiences = []
    try:
        # Methode 1: Suche nach h2 "Experience"
        try:
            exp_headers = driver.find_elements(By.XPATH, "//h2[contains(text(), 'Experience')]")
            if exp_headers:
                exp_header = exp_headers[0]
                parent = exp_header.find_element(By.XPATH, "..")
                li_elements = parent.find_elements(By.TAG_NAME, "li")
                
                for li in li_elements[:10]:
                    li_text = li.text.strip()
                    if len(li_text) > 15 and not any(x in li_text.lower() for x in ['feed', 'network', 'message', 'jobs', 'see all']):
                        lines = li_text.split('\n')
                        exp_data = {
                            "title": lines[0] if lines else "N/A",
                            "company": lines[1] if len(lines) > 1 else "N/A",
                            "duration": lines[2] if len(lines) > 2 else "N/A",
                        }
                        experiences.append(exp_data)
        except:
            pass
        
        # Methode 2: Suche aus Body Text
        if not experiences:
            body_text = driver.find_element(By.TAG_NAME, "body").text
            lines = body_text.split('\n')
            for i, line in enumerate(lines):
                if 'Experience' in line:
                    # Sammle die nächsten Zeilen als Jobs
                    j = i + 1
                    while j < min(i + 20, len(lines)) and j < len(lines):
                        job_line = lines[j].strip()
                        if job_line and not any(x in job_line.lower() for x in ['education', 'skills', 'see all', 'followers']):
                            if len(job_line) > 5:
                                experiences.append({
                                    "title": job_line[:100],
                                    "company": "N/A",
                                    "duration": "N/A",
                                })
                        j += 1
                    break
    except:
        pass
    
    # Educations
    educations = []
    try:
        # Methode 1: Suche nach h2 "Education"
        try:
            edu_headers = driver.find_elements(By.XPATH, "//h2[contains(text(), 'Education')]")
            if edu_headers:
                edu_header = edu_headers[0]
                parent = edu_header.find_element(By.XPATH, "..")
                li_elements = parent.find_elements(By.TAG_NAME, "li")
                
                for li in li_elements[:10]:
                    li_text = li.text.strip()
                    if len(li_text) > 5 and not any(x in li_text.lower() for x in ['feed', 'network', 'message', 'jobs']):
                        lines = li_text.split('\n')
                        edu_data = {
                            "school": lines[0] if lines else "N/A",
                            "degree": lines[1] if len(lines) > 1 else "N/A",
                        }
                        educations.append(edu_data)
        except:
            pass
        
        # Methode 2: Suche aus Body Text
        if not educations:
            body_text = driver.find_element(By.TAG_NAME, "body").text
            lines = body_text.split('\n')
            for i, line in enumerate(lines):
                if 'Education' in line:
                    # Sammle die nächsten Zeilen als Schulen
                    j = i + 1
                    while j < min(i + 15, len(lines)) and j < len(lines):
                        edu_line = lines[j].strip()
                        if edu_line and not any(x in edu_line.lower() for x in ['experience', 'skills', 'see all', 'followers']):
                            if len(edu_line) > 3:
                                educations.append({
                                    "school": edu_line[:100],
                                    "degree": "N/A",
                                })
                        j += 1
                    break
    except:
        pass
    
    # Zusammentragen
    profile_data = {
        "timestamp": datetime.now().isoformat(),
        "linkedin_url": profile_url,
        "name": name,
        "job_title": job_title,
        "location": location,
        "about": about,
        "experiences": experiences if experiences else [{"title": "N/A", "company": "N/A", "duration": "N/A"}],
        "educations": educations if educations else [{"school": "N/A", "degree": "N/A"}],
    }
    
    return profile_data


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
    print(f"📍 Standort: {data.get('location', 'N/A')}")
    
    about = data.get('about', 'N/A')
    if len(about) > 100:
        about = about[:100] + "..."
    print(f"📝 About: {about}")
    
    if data.get("experiences"):
        print(f"\n💡 Erfahrungen ({len(data['experiences'])} gefunden):")
        for i, exp in enumerate(data["experiences"][:5], 1):
            print(f"   {i}. {exp.get('title', 'N/A')}")
            if exp.get('company') != 'N/A':
                print(f"      @ {exp.get('company', 'N/A')}")
    
    if data.get("educations"):
        print(f"\n🎓 Ausbildung ({len(data['educations'])} gefunden):")
        for i, edu in enumerate(data["educations"][:5], 1):
            print(f"   {i}. {edu.get('school', 'N/A')}")
    
    print("\n" + "="*50)


def main():
    """Hauptprogramm"""
    driver = None
    
    try:
        print("\n🚀 LinkedIn Profile Scraper V3")
        print("="*50)
        
        print("⏳ Chrome wird gestartet...")
        driver = setup_driver()
        
        if not login_to_linkedin(driver):
            return
        
        profile_url = input("\n🔗 LinkedIn Profil-URL eingeben: ").strip()
        
        if not profile_url:
            print("❌ Keine URL eingegeben!")
            return
        
        print("\n⏳ Daten werden extrahiert (das kann bis zu 30 Sekunden dauern)...")
        profile_data = scrape_profile_direct(driver, profile_url)
        
        if profile_data and profile_data.get('name') != 'N/A':
            print_profile(profile_data)
            
            filepath = save_data(profile_data)
            print(f"✅ Daten gespeichert: {filepath}")
            
            print(f"\n📄 Komplette Daten (JSON):")
            print(json.dumps(profile_data, indent=2, ensure_ascii=False))
        else:
            print("\n⚠️  Konnte keine Profildaten extrahieren.")
            print("Mögliche Gründe:")
            print("- Profil ist privat")
            print("- LinkedIn hat das Seitenlayout geändert")
            print("- Zu schnelle Anfragen (LinkedIn blockiert)")
    
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
