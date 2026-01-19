#!/usr/bin/env python3
"""
LinkedIn Scraper HTTP API für n8n Webhooks (mit joeyism/linkedin_scraper Library)
Starte mit: python scrape_api.py
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

driver = None


def setup_driver():
    """Chrome Setup"""
    opts = Options()
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    
    return webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=opts
    )


def load_session():
    """Lädt gespeicherte Session"""
    global driver
    
    if driver is None:
        driver = setup_driver()
    
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


def check_login():
    """Prüft Loginzustand"""
    global driver
    if driver is None:
        return False
    
    try:
        driver.get("https://www.linkedin.com/feed/")
        time.sleep(2)
        if "login" in driver.current_url.lower():
            return False
        try:
            WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.CLASS_NAME, "global-nav"))
            )
            return True
        except:
            return False
    except:
        return False


def scrape_profile(url):
    """Scrapte ein Profil mit joeyism/linkedin_scraper Library"""
    global driver
    
    if driver is None:
        driver = setup_driver()
    
    data = {
        "url": url,
        "status": "error",
        "timestamp": datetime.now().isoformat()
    }
    
    try:
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
        
        # Extrahiere Daten
        data["name"] = person.name or "N/A"
        data["job_title"] = person.job_title or "N/A"
        data["company"] = person.company or "N/A"
        data["location"] = person.location or "N/A"
        data["about"] = person.about[0] if person.about and len(person.about) > 0 else "N/A"
        
        # Experiences
        data["experiences"] = []
        if person.experiences:
            for exp in person.experiences:
                data["experiences"].append({
                    "position_title": exp.position_title or "N/A",
                    "institution_name": exp.institution_name or "N/A",
                    "from_date": exp.from_date or "N/A",
                    "to_date": exp.to_date or "N/A",
                    "duration": exp.duration or "N/A",
                    "location": exp.location or "N/A"
                })
        
        # Educations
        data["educations"] = []
        if person.educations:
            for edu in person.educations:
                data["educations"].append({
                    "institution_name": edu.institution_name or "N/A",
                    "degree": edu.degree or "N/A",
                    "from_date": edu.from_date or "N/A",
                    "to_date": edu.to_date or "N/A"
                })
        
        # Interests
        data["interests"] = []
        if person.interests:
            for interest in person.interests:
                data["interests"].append(interest.institution_name or str(interest))
        
        # Accomplishments
        data["accomplishments"] = []
        if person.accomplishments:
            for acc in person.accomplishments:
                data["accomplishments"].append({
                    "category": acc.category or "N/A",
                    "title": acc.title or "N/A"
                })
        
        data["status"] = "success"
        
    except Exception as e:
        data["error"] = str(e)
    
    return data


@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "running",
        "session_exists": os.path.exists(COOKIES_FILE),
        "timestamp": datetime.now().isoformat()
    })


@app.route('/scrape', methods=['POST'])
def scrape():
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({"status": "error", "error": "Missing 'url' parameter"}), 400
        
        if not os.path.exists(COOKIES_FILE):
            return jsonify({"status": "error", "error": "NO_SESSION"}), 401
        
        if not load_session():
            return jsonify({"status": "error", "error": "FAILED_TO_LOAD_SESSION"}), 401
        
        if not check_login():
            return jsonify({"status": "error", "error": "SESSION_EXPIRED"}), 401
        
        result = scrape_profile(url)
        return jsonify(result), 200 if result["status"] == "success" else 500
    
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500


@app.route('/scrape/batch', methods=['POST'])
def scrape_batch():
    try:
        data = request.get_json()
        urls = data.get('urls', [])
        
        if not urls:
            return jsonify({"status": "error", "error": "Missing 'urls' parameter"}), 400
        
        if not load_session():
            return jsonify({"status": "error", "error": "FAILED_TO_LOAD_SESSION"}), 401
        
        if not check_login():
            return jsonify({"status": "error", "error": "SESSION_EXPIRED"}), 401
        
        results = []
        for url in urls:
            try:
                result = scrape_profile(url)
                results.append(result)
                time.sleep(2)
            except Exception as e:
                results.append({"url": url, "status": "error", "error": str(e)})
        
        return jsonify({"status": "success", "total": len(urls), "results": results}), 200
    
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500


@app.route('/status', methods=['GET'])
def status():
    return jsonify({
        "service": "LinkedIn Scraper API (joeyism library)",
        "version": "2.0",
        "session_exists": os.path.exists(COOKIES_FILE)
    })


if __name__ == '__main__':
    print("\n" + "="*60)
    print("LinkedIn Scraper API v2.0 (joeyism/linkedin_scraper)")
    print("="*60)
    print("\nAPI laeuft auf: http://localhost:5000")
    print("\nEndpoints:")
    print("  POST /scrape       - Einzelnes Profil scrapen")
    print("  POST /scrape/batch - Mehrere Profile scrapen")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False)
