#!/usr/bin/env python3
"""
Debug Script - Speichert HTML der LinkedIn-Seite um Selektoren zu finden
"""

import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


def setup_driver():
    """Chrome WebDriver"""
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    return driver


def main():
    driver = None
    
    try:
        print("\n🚀 LinkedIn Debug HTML Saver")
        print("="*50)
        
        driver = setup_driver()
        
        driver.get("https://www.linkedin.com/login")
        
        print("\n📋 Anleitung:")
        print("1. Logge dich ein")
        print("2. Navigiere zu einem LinkedIn Profil")
        print("3. Drücke Enter wenn du bereit bist")
        input("\n▶️  Drücke Enter...")
        
        # Warte auf Profil
        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        
        time.sleep(2)
        
        # Scroll
        for i in range(3):
            driver.execute_script("window.scrollBy(0, 500);")
            time.sleep(1)
        
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
        
        # HTML speichern
        html = driver.page_source
        
        # Speichern
        os.makedirs("debug", exist_ok=True)
        with open("debug/linkedin_profile.html", "w", encoding="utf-8") as f:
            f.write(html)
        
        print("\n✅ HTML gespeichert in: debug/linkedin_profile.html")
        print(f"📊 Größe: {len(html)} bytes")
        
        # Quick Stats
        print("\n📋 Quick Analysis:")
        print(f"   - Enthält 'Experience': {'Experience' in html}")
        print(f"   - Enthält 'About': {'About' in html}")
        print(f"   - Enthält 'Education': {'Education' in html}")
        print(f"   - H1-Tags: {html.count('<h1')}")
        print(f"   - H2-Tags: {html.count('<h2')}")
        
    except Exception as e:
        print(f"❌ Fehler: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if driver:
            driver.quit()


if __name__ == "__main__":
    main()
