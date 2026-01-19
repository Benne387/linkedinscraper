import os
import json
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from linkedin_scraper import Person

# Config
COOKIES_DIR = "linkedin_session"
# COOKIES_FILE is now dynamic
SCRAPED_DATA_DIR = "scraped_data"

# Ensure directories exist
os.makedirs(COOKIES_DIR, exist_ok=True)
os.makedirs(SCRAPED_DATA_DIR, exist_ok=True)

def setup_driver():
    """Chrome Setup - New instance per request for safety in container"""
    opts = Options()
    
    # Headless mode only if requested (default True for Docker, likely False for local debug)
    if os.getenv("HEADLESS", "true").lower() == "true":
        opts.add_argument("--headless=new") # Modern headless (more stable)
        
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--remote-debugging-port=9222") # Often helps in docker
    
    # Anti-detect settings
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option('useAutomationExtension', False)

    # Force English Language (Crucial for scraping logic that relies on "Experience", "Education" etc.)
    opts.add_argument("--lang=en-US")
    opts.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})

    return webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=opts
    )

def get_cookie_file(session_id):
    """Returns unique cookie path for a user session"""
    clean_id = "".join(x for x in session_id if x.isalnum() or x in "-_")
    return os.path.join(COOKIES_DIR, f"cookies_{clean_id}.json")

def load_cookies(driver, session_id):
    """Loads saved session cookies for specific user"""
    cookie_file = get_cookie_file(session_id)
    if not os.path.exists(cookie_file):
        return False
    
    try:
        driver.get("https://www.linkedin.com")
        time.sleep(2)
        
        with open(cookie_file, 'r') as f:
            cookies = json.load(f)
        
        for cookie in cookies:
            try:
                # Selenium expects specific keys, and expiry should be int/float
                if 'sameSite' in cookie and cookie['sameSite'] not in ["Strict", "Lax", "None"]:
                     del cookie['sameSite'] 
                driver.add_cookie(cookie)
            except:
                pass
        
        # FORCE ENGLISH LANGUAGE COOKIE (Critical for scraper library)
        try:
            driver.add_cookie({
                'name': 'lang',
                'value': 'v=2&lang=en-us',
                'domain': '.linkedin.com',
                'path': '/'
            })
            print("DEBUG: Injected English language cookie.")
        except Exception as e:
            print(f"DEBUG: Failed to inject language cookie: {e}")

        driver.refresh()
        time.sleep(2)
        return True
    except Exception as e:
        print(f"Error loading cookies: {e}")
        return False


# SINGLETON REMOVED FOR SECURITY/ISOLATION
# Each user needs their own isolated browser instance

def login_to_linkedin(email, password, session_id):
    """Performs automated login and saves cookies for session"""
    driver = None
    try:
        driver = setup_driver()
        driver.get("https://www.linkedin.com/login")
        time.sleep(2)
        
        driver.find_element("id", "username").send_keys(email)
        driver.find_element("id", "password").send_keys(password)
        driver.find_element("css selector", "button[type='submit']").click()
        
        # Wait up to 300 seconds for user to complete captcha/2FA
        # Loop checks for success every second
        for i in range(300):
            time.sleep(1)
            try:
                 # Check if login probably succeeded (url changed or feed visible)
                if "feed" in driver.current_url or "checkpoint" not in driver.current_url:
                    save_cookies(driver, session_id)
                    return {"status": "success", "message": "Login successful"}
            except:
                pass
                
        return {"status": "error", "message": "Login timed out (300s limit)"}
             
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

def save_manual_cookies(cookie_json_str, session_id):
    """Saves manually pasted cookies to session file"""
    try:
        # Validate JSON
        cookies = json.loads(cookie_json_str)
        if isinstance(cookies, list):
            with open(get_cookie_file(session_id), 'w') as f:
                json.dump(cookies, f)
            return {"status": "success", "message": "Cookies imported"}
        else:
            return {"status": "error", "message": "Invalid JSON: Must be a list of cookies"}
    except Exception as e:
        return {"status": "error", "message": f"Invalid JSON: {str(e)}"}

def save_cookies(driver, session_id):
    """Saves session cookies to unique file"""
    try:
        with open(get_cookie_file(session_id), 'w') as f:
            json.dump(driver.get_cookies(), f)
    except Exception as e:
        print(f"Error saving cookies: {e}")

def get_safe_attribute(obj, attr, default="N/A"):
    """Helper to safely get attributes from objects"""
    val = getattr(obj, attr, None)
    return val if val else default

def scrape_profile_logic(url, session_id="default"):
    """Main scraping logic"""
    driver = None
    data = {
        "url": url,
        "status": "error",
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        print("DEBUG: Setting up driver...")
        driver = setup_driver()
        print("DEBUG: Driver setup complete. Loading cookies...")
        load_cookies(driver, session_id)
            
        print(f"DEBUG: Scraping URL: {url}")
        data["url"] = url 

        # Initialize Person with scrape=True
        print("DEBUG: Initializing Person object (Starting scrape)...")
        try:
            person = Person(
                linkedin_url=url,
                driver=driver,
                scrape=True,
                close_on_complete=False 
            )
            print("DEBUG: Person object created. Scrape finished?")
        except Exception as p_err:
             print(f"DEBUG: Person/Scrape FAILED: {p_err}")
             try:
                 print(f"DEBUG: Last URL: {driver.current_url}")
                 print(f"DEBUG: Page Title: {driver.title}")
                 
                 # Save Screenshot for diagnosis
                 screenshot_path = os.path.join(SCRAPED_DATA_DIR, "error_screenshot.png")
                 driver.save_screenshot(screenshot_path)
                 print(f"DEBUG: Saved error screenshot to {screenshot_path}")
                 
                 # Save Page Source
                 source_path = os.path.join(SCRAPED_DATA_DIR, "error_page.html")
                 with open(source_path, "w", encoding="utf-8") as f:
                     f.write(driver.page_source)
                 print(f"DEBUG: Saved error HTML to {source_path}")
             except Exception as shot_err:
                 print(f"DEBUG: Could not capture screenshot/source: {shot_err}")
                 
             raise p_err
        
        save_cookies(driver, session_id)
        
        # Extract Data cleanly
        data["name"] = get_safe_attribute(person, 'name')
        data["job_title"] = get_safe_attribute(person, 'job_title')
        data["company"] = get_safe_attribute(person, 'company')
        data["location"] = get_safe_attribute(person, 'location')
        
        about = get_safe_attribute(person, 'about', [])
        data["about"] = about[0] if about and len(about) > 0 else "N/A"
        
        # Experiences
        data["experiences"] = []
        for exp in get_safe_attribute(person, 'experiences', []):
            data["experiences"].append({
                "position_title": get_safe_attribute(exp, 'position_title'),
                "institution_name": get_safe_attribute(exp, 'institution_name'),
                "from_date": get_safe_attribute(exp, 'from_date'),
                "to_date": get_safe_attribute(exp, 'to_date'),
                "duration": get_safe_attribute(exp, 'duration'),
                "location": get_safe_attribute(exp, 'location')
            })

        # Educations
        data["educations"] = []
        for edu in get_safe_attribute(person, 'educations', []):
            data["educations"].append({
                "institution_name": get_safe_attribute(edu, 'institution_name'),
                "degree": get_safe_attribute(edu, 'degree'),
                "from_date": get_safe_attribute(edu, 'from_date'),
                "to_date": get_safe_attribute(edu, 'to_date')
            })

        # Process generic lists
        data["interests"] = [get_safe_attribute(i, 'institution_name', str(i)) for i in get_safe_attribute(person, 'interests', [])]
        
        # Accomplishments
        data["accomplishments"] = []
        for acc in get_safe_attribute(person, 'accomplishments', []):
            data["accomplishments"].append({
                "category": get_safe_attribute(acc, 'category'),
                "title": get_safe_attribute(acc, 'title')
            })

        # Skills (Try to get if available)
        data["skills"] = [get_safe_attribute(s, 'name', str(s)) for s in get_safe_attribute(person, 'skills', [])]
        
        # Certifications
        data["certifications"] = []
        for cert in get_safe_attribute(person, 'certifications', []):
            data["certifications"].append({
                "name": get_safe_attribute(cert, 'name'),
                "organization": get_safe_attribute(cert, 'organization')
            })

        # Languages
        data["languages"] = []
        for lang in get_safe_attribute(person, 'languages', []):
             data["languages"].append({
                "name": get_safe_attribute(lang, 'name'),
                "proficiency": get_safe_attribute(lang, 'proficiency')
            })

        data["status"] = "success"
        
        # Save to disk
        if data["name"] != "N/A":
            filename = f"{SCRAPED_DATA_DIR}/{data['name'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
    except Exception as e:
        data["error"] = str(e)
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass
                
    return data
