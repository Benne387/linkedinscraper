#!/usr/bin/env python3
"""
LinkedIn Scraper für n8n - API/Webhook Mode
Akzeptiert eine einzelne URL über stdin oder CLI
Gibt JSON aus (perfekt für n8n)
"""

import json
import sys
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time


class LinkedInScraperN8N:
    """Minimales LinkedIn Scraper für n8n Integration"""
    
    COOKIES_DIR = "linkedin_session"
    COOKIES_FILE = os.path.join(COOKIES_DIR, "cookies.json")
    
    def __init__(self):
        self.driver = None
        os.makedirs(self.COOKIES_DIR, exist_ok=True)
    
    def setup_driver(self):
        """Chrome Setup"""
        opts = Options()
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--disable-gpu")
        opts.add_argument("--headless=new")
        opts.binary_location = "/usr/bin/chromium-browser"
        
        self.driver = webdriver.Chrome(options=opts)
    
    def save_cookies(self):
        """Speichert Session"""
        cookies = self.driver.get_cookies()
        with open(self.COOKIES_FILE, 'w') as f:
            json.dump(cookies, f)
    
    def load_cookies(self):
        """Lädt Session"""
        if os.path.exists(self.COOKIES_FILE):
            self.driver.get("https://www.linkedin.com")
            time.sleep(1)
            
            with open(self.COOKIES_FILE, 'r') as f:
                cookies = json.load(f)
            
            for cookie in cookies:
                try:
                    self.driver.add_cookie(cookie)
                except:
                    pass
            
            return True
        return False
    
    def is_logged_in(self):
        """Prüft Loginzustand"""
        try:
            self.driver.get("https://www.linkedin.com/feed/")
            time.sleep(2)
            if "login" in self.driver.current_url.lower():
                return False
            self.driver.find_element(By.TAG_NAME, "main")
            return True
        except:
            return False
    
    def scrape(self, url):
        """Scrapte ein Profil"""
        self.driver.get(url)
        time.sleep(2)
        
        # Wait für Profil laden (longer timeout)
        try:
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.TAG_NAME, "h1"))
            )
        except:
            pass
        
        data = {
            "linkedin_url": url,
            "name": "N/A",
            "job_title": "N/A",
            "company": "N/A",
            "location": "N/A",
            "experiences": [],
            "educations": []
        }
        
        try:
            # Name
            h1 = self.driver.find_element(By.TAG_NAME, "h1")
            data["name"] = h1.text.strip()
            
            # Main Info
            main_text = self.driver.find_element(By.TAG_NAME, "main").text
            lines = main_text.split('\n')
            
            # Job Title (erste relevante Zeile)
            for line in lines[:10]:
                line = line.strip()
                if line and line != data["name"] and len(line) < 150:
                    if any(x in line.lower() for x in ['director', 'manager', 'engineer', 'developer']):
                        data["job_title"] = line
                        break
            
            # Location (Zeile mit Komma)
            for line in lines[:20]:
                line = line.strip()
                if "," in line and 5 < len(line) < 80:
                    data["location"] = line
                    break
            
            # Experiences
            try:
                self.driver.get(url + "/details/experience")
                time.sleep(1)
                items = self.driver.find_element(By.TAG_NAME, "main").find_elements(
                    By.XPATH, "//div[@data-view-name='profile-component-entity']"
                )
                
                for item in items[:5]:
                    lines = [l.strip() for l in item.text.split('\n') if l.strip()]
                    if len(lines) >= 2 and len(lines[0]) > 2:
                        data["experiences"].append({
                            "title": lines[0],
                            "company": lines[1]
                        })
                        if data["company"] == "N/A":
                            data["company"] = lines[1]
            except:
                pass
            
            # Educations
            try:
                self.driver.get(url.split('/details/')[0] + "/details/education")
                time.sleep(1)
                items = self.driver.find_element(By.TAG_NAME, "main").find_elements(
                    By.XPATH, "//div[@data-view-name='profile-component-entity']"
                )
                
                for item in items[:3]:
                    lines = [l.strip() for l in item.text.split('\n') if l.strip()]
                    if lines and len(lines[0]) > 5:
                        data["educations"].append({"school": lines[0]})
            except:
                pass
        
        except Exception as e:
            data["error"] = str(e)
        
        return data
    
    def close(self):
        if self.driver:
            self.driver.quit()


def main():
    """CLI Entry Point für n8n"""
    
    # URL aus Argument oder stdin
    url = None
    
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        # Reads from stdin (n8n kann Daten so übergeben)
        try:
            data = json.loads(sys.stdin.read())
            url = data.get("url") or data.get("linkedin_url")
        except:
            pass
    
    if not url:
        result = {
            "error": "No URL provided",
            "usage": "python scrape_n8n.py <linkedin_url>",
            "example": "python scrape_n8n.py https://linkedin.com/in/someprofile"
        }
        print(json.dumps(result))
        sys.exit(1)
    
    scraper = LinkedInScraperN8N()
    
    try:
        scraper.setup_driver()
        
        # Lade Session
        if scraper.load_cookies():
            if not scraper.is_logged_in():
                raise Exception("SESSION_EXPIRED - Bitte erneut manuell einloggen")
        else:
            raise Exception("NO_SESSION - Führe 'python scrape_batch.py <url>' erst aus um Session zu erstellen")
        
        # Scrape
        data = scraper.scrape(url)
        data["timestamp"] = datetime.now().isoformat()
        data["status"] = "success"
        
    except Exception as e:
        data = {
            "url": url,
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
    
    finally:
        scraper.close()
    
    # Output für n8n
    print(json.dumps(data, ensure_ascii=False, indent=2))
    return 0 if data.get("status") == "success" else 1


if __name__ == "__main__":
    sys.exit(main())
