#!/usr/bin/env python3
"""
LinkedIn Scraper HTTP API für n8n Webhooks (mit joeyism/linkedin_scraper Library)
SICHERE VERSION - Browser wird bei jedem Request neu erstellt
Starte mit: python scrape_api_safe.py
"""

from flask import Flask, request, jsonify
from datetime import datetime
import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from linkedin_scraper import Person
import time

app = Flask(__name__)

# Config
COOKIES_DIR = "linkedin_session"
COOKIES_FILE = os.path.join(COOKIES_DIR, "cookies.json")
os.makedirs(COOKIES_DIR, exist_ok=True)
os.makedirs("scraped_data", exist_ok=True)


def setup_driver():
    """Chrome Setup - Neue Instanz pro Request"""
    opts = Options()
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    
    return webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=opts
    )


def load_cookies(driver):
    """Lädt gespeicherte Session"""
    if not os.path.exists(COOKIES_FILE):
        return False
    
    try:
        driver.get("https://www.linkedin.com")
        time.sleep(1)
        
        with open(COOKIES_FILE, 'r') as f:
            cookies = json.load(f)
        
        for cookie in cookies:
            try:
                driver.add_cookie(cookie)
            except:
                pass
        
        driver.refresh()
        time.sleep(2)
        return True
    except:
        return False


def scrape_profile(url):
    """Scrapte ein Profil mit joeyism/linkedin_scraper Library"""
    driver = None
    
    data = {
        "url": url,
        "status": "error",
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        driver = setup_driver()
        load_cookies(driver)
        
        person = Person(
            linkedin_url=url,
            driver=driver,
            scrape=True,
            close_on_complete=False
        )
        
        # Speichere Cookies
        try:
            with open(COOKIES_FILE, 'w') as f:
                json.dump(driver.get_cookies(), f)
        except:
            pass
        
        # Extrahiere Daten - mit sicherer Attribut-Pruefung
        data["name"] = getattr(person, 'name', None) or "N/A"
        data["job_title"] = getattr(person, 'job_title', None) or "N/A"
        data["company"] = getattr(person, 'company', None) or "N/A"
        data["location"] = getattr(person, 'location', None) or "N/A"
        
        # About - sicher extrahieren
        about = getattr(person, 'about', None)
        data["about"] = about[0] if about and len(about) > 0 else "N/A"
        
        # Experiences - mit sicherer Attribut-Pruefung
        data["experiences"] = []
        experiences = getattr(person, 'experiences', None)
        if experiences:
            for exp in experiences:
                data["experiences"].append({
                    "position_title": getattr(exp, 'position_title', None) or "N/A",
                    "institution_name": getattr(exp, 'institution_name', None) or "N/A",
                    "from_date": getattr(exp, 'from_date', None) or "N/A",
                    "to_date": getattr(exp, 'to_date', None) or "N/A",
                    "duration": getattr(exp, 'duration', None) or "N/A",
                    "location": getattr(exp, 'location', None) or "N/A"
                })
        
        # Educations - mit sicherer Attribut-Pruefung
        data["educations"] = []
        educations = getattr(person, 'educations', None)
        if educations:
            for edu in educations:
                data["educations"].append({
                    "institution_name": getattr(edu, 'institution_name', None) or "N/A",
                    "degree": getattr(edu, 'degree', None) or "N/A",
                    "from_date": getattr(edu, 'from_date', None) or "N/A",
                    "to_date": getattr(edu, 'to_date', None) or "N/A"
                })
        
        # Interests - mit sicherer Attribut-Pruefung
        data["interests"] = []
        interests = getattr(person, 'interests', None)
        if interests:
            for interest in interests:
                data["interests"].append(getattr(interest, 'institution_name', None) or str(interest))
        
        # Accomplishments - mit sicherer Attribut-Pruefung
        data["accomplishments"] = []
        accomplishments = getattr(person, 'accomplishments', None)
        if accomplishments:
            for acc in accomplishments:
                data["accomplishments"].append({
                    "category": getattr(acc, 'category', None) or "N/A",
                    "title": getattr(acc, 'title', None) or "N/A"
                })
        
        data["status"] = "success"
        
    except Exception as e:
        data["error"] = str(e)
        # Beim Fehler: Leere aber valide Response
        data["name"] = "N/A"
        data["experiences"] = []
        data["educations"] = []
        data["interests"] = []
        data["accomplishments"] = []
    
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass
    
    return data


@app.route('/health', methods=['GET'])
def health():
    """Health Check"""
    return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()})


@app.route('/status', methods=['GET'])
def status():
    """Status Endpoint"""
    return jsonify({
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "session_exists": os.path.exists(COOKIES_FILE)
    })


@app.route('/scrape', methods=['POST'])
def scrape():
    """Scrapte ein einzelnes Profil"""
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({"status": "error", "error": "URL erforderlich"}), 400
        
        result = scrape_profile(url)
        
        # Speichere Result nur wenn erfolgreich
        if result['status'] == 'success' and result.get('name') and result.get('name') != 'N/A':
            try:
                os.makedirs("scraped_data", exist_ok=True)
                filename = f"scraped_data/{result.get('name', 'unknown').replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
            except Exception as e:
                # Fehler beim Speichern - nicht kritisch
                pass
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500


@app.route('/scrape/batch', methods=['POST'])
def scrape_batch():
    """Scrapte mehrere Profile"""
    try:
        data = request.get_json()
        urls = data.get('urls', [])
        
        if not urls:
            return jsonify({"status": "error", "error": "URLs erforderlich"}), 400
        
        results = []
        for url in urls:
            result = scrape_profile(url)
            results.append(result)
            
            # Speichere Result nur wenn erfolgreich und Name existiert
            if result['status'] == 'success' and result.get('name') and result.get('name') != 'N/A':
                try:
                    os.makedirs("scraped_data", exist_ok=True)
                    filename = f"scraped_data/{result.get('name', 'unknown').replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(result, f, indent=2, ensure_ascii=False)
                except Exception as e:
                    # Fehler beim Speichern - nicht kritisch
                    pass
        
        return jsonify({
            "status": "success",
            "total": len(urls),
            "success": sum(1 for r in results if r['status'] == 'success'),
            "results": results,
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500


if __name__ == '__main__':
    print("\n" + "="*60)
    print("[>>>] LinkedIn Scraper API v2.1 (SAFE - joeyism/linkedin_scraper)")
    print("="*60)
    print("\n[*] API laeuft auf: http://localhost:5000")
    print("\n[API] Endpoints:")
    print("  GET  /health")
    print("  GET  /status")
    print("  POST /scrape       - Einzelnes Profil scrapen")
    print("  POST /scrape/batch - Mehrere Profile scrapen")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=False)
