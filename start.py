#!/usr/bin/env python3
"""
LinkedIn Scraper - Starter App
Startet automatisch den Server und ngrok Tunnel
"""

import subprocess
import time
import os
import sys
import signal
import requests
from pathlib import Path

# Farben für Console-Output
class Colors:
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header():
    """Zeigt Welcome-Banner"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("=" * 60)
    print("  🚀 LinkedIn Scraper - Starter")
    print("=" * 60)
    print(f"{Colors.END}\n")

def check_requirements():
    """Prüft ob ngrok und flask installiert sind"""
    print(f"{Colors.YELLOW}📋 Überprüfe Requirements...{Colors.END}")
    
    try:
        import flask
        print(f"  ✅ Flask: {flask.__version__}")
    except ImportError:
        print(f"  {Colors.RED}❌ Flask nicht installiert!{Colors.END}")
        print(f"  {Colors.YELLOW}pip install flask{Colors.END}")
        return False
    
    try:
        import selenium
        print(f"  ✅ Selenium: {selenium.__version__}")
    except ImportError:
        print(f"  {Colors.RED}❌ Selenium nicht installiert!{Colors.END}")
        return False
    
    # Prüfe ob ngrok existiert
    try:
        result = subprocess.run(['ngrok', '--version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0] if result.stdout else "unknown"
            print(f"  ✅ ngrok: {version_line.strip()}")
        else:
            print(f"  {Colors.RED}❌ ngrok nicht gefunden!{Colors.END}")
            print(f"  {Colors.YELLOW}Installiere ngrok von: https://ngrok.com/download{Colors.END}")
            return False
    except FileNotFoundError:
        print(f"  {Colors.RED}❌ ngrok nicht gefunden!{Colors.END}")
        print(f"  {Colors.YELLOW}Installiere ngrok von: https://ngrok.com/download{Colors.END}")
        return False
    except Exception as e:
        print(f"  {Colors.RED}❌ Fehler beim Prüfen von ngrok: {e}{Colors.END}")
        return False
    
    print()
    return True

def start_flask_server():
    """Startet den Flask Server im Hintergrund"""
    print(f"{Colors.YELLOW}🔧 Starte Flask Server...{Colors.END}")
    
    script_path = Path(__file__).parent / "run.py"
    
    if not script_path.exists():
        print(f"  {Colors.RED}❌ run.py nicht gefunden!{Colors.END}")
        return None
    
    try:
        # Run environment with HEADLESS=false for local visibility
        run_env = os.environ.copy()
        run_env["HEADLESS"] = "false"

        # Starte Server als subprocess
        process = subprocess.Popen(
            [sys.executable, str(script_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            env=run_env
        )
        
        # Warte bis Server läuft
        max_attempts = 30
        for attempt in range(max_attempts):
            try:
                response = requests.get('http://localhost:5000/health', timeout=1)
                if response.status_code == 200:
                    print(f"  {Colors.GREEN}✅ Server läuft auf http://localhost:5000{Colors.END}")
                    return process
            except requests.exceptions.RequestException:
                pass
            
            time.sleep(0.2)
            if attempt % 5 == 0:
                print(f"    ⏳ Warte auf Server... ({attempt+1}/{max_attempts})")
        
        print(f"  {Colors.RED}❌ Server konnte nicht gestartet werden!{Colors.END}")
        return None
        
    except Exception as e:
        print(f"  {Colors.RED}❌ Fehler beim Starten des Servers: {e}{Colors.END}")
        return None

def start_ngrok_tunnel():
    """Startet ngrok Tunnel"""
    print(f"\n{Colors.YELLOW}🔗 Starte ngrok Tunnel...{Colors.END}")
    
    try:
        process = subprocess.Popen(
            ['ngrok', 'http', '5000'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        # Lese Output und finde ngrok URL
        max_attempts = 30
        for attempt in range(max_attempts):
            line = process.stdout.readline()
            if line:
                if 'Forwarding' in line and 'http' in line:
                    # Extrakt URL: "Forwarding    https://xxx -> http://localhost:5000"
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part.startswith('https://') or part.startswith('http://'):
                            url = part
                            print(f"  {Colors.GREEN}✅ Tunnel aktiv!{Colors.END}")
                            print(f"\n{Colors.BOLD}{Colors.BLUE}🌐 Öffentliche URL:{Colors.END}")
                            print(f"  {Colors.GREEN}{url}{Colors.END}\n")
                            return process, url
            time.sleep(0.2)
        
        print(f"  {Colors.YELLOW}⏳ Tunnel wird gestartet... (manchmal dauert es){Colors.END}")
        
        # Zusätzlich API abfragen für URL
        max_api_attempts = 20
        for attempt in range(max_api_attempts):
            try:
                api_response = requests.get('http://localhost:4040/api/tunnels', timeout=2)
                if api_response.status_code == 200:
                    tunnels = api_response.json().get('tunnels', [])
                    for tunnel in tunnels:
                        if tunnel.get('proto') == 'https':
                            url = tunnel.get('public_url')
                            print(f"  {Colors.GREEN}✅ Tunnel aktiv!{Colors.END}")
                            print(f"\n{Colors.BOLD}{Colors.BLUE}🌐 Öffentliche URL:{Colors.END}")
                            print(f"  {Colors.GREEN}{url}{Colors.END}\n")
                            return process, url
            except:
                pass
            
            time.sleep(0.3)
        
        return process, None
        
    except FileNotFoundError:
        print(f"  {Colors.RED}❌ ngrok nicht gefunden!{Colors.END}")
        return None, None
    except Exception as e:
        print(f"  {Colors.RED}❌ Fehler beim Starten von ngrok: {e}{Colors.END}")
        return None, None

def print_usage(tunnel_url):
    """Zeigt Nutzungsinformationen"""
    print(f"{Colors.BOLD}{Colors.BLUE}=" * 60)
    print("📖 VERWENDUNG IN N8N")
    print("=" * 60 + f"{Colors.END}\n")
    
    print(f"{Colors.BOLD}API Endpoints:{Colors.END}")
    
    if tunnel_url:
        print(f"\n  {Colors.GREEN}Single Profile:{Colors.END}")
        print(f"    POST {tunnel_url}/scrape")
        print(f"    Body: {{\"url\": \"https://linkedin.com/in/...\"}}\\n")
        
        print(f"  {Colors.GREEN}Batch Scraping:{Colors.END}")
        print(f"    POST {tunnel_url}/scrape/batch")
        print(f"    Body: {{\"urls\": [\"https://linkedin.com/in/...\", \"...\"]}}\n")
    
    print(f"{Colors.YELLOW}⚠️ WICHTIG:{Colors.END}")
    print(f"  • Ngrok URL ändert sich nach Neustart!")
    print(f"  • Halte diesen Terminal offen")
    print(f"  • Drücke Ctrl+C zum Beenden\n")
    
    if not tunnel_url:
        print(f"{Colors.YELLOW}  Lokale URL (nur auf diesem PC):{Colors.END}")
        print(f"    http://localhost:5000/scrape\n")

def main():
    """Hauptfunktion"""
    print_header()
    
    # Prüfe Requirements
    if not check_requirements():
        sys.exit(1)
    
    # Starte Server
    server_process = start_flask_server()
    if not server_process:
        sys.exit(1)
    
    # Starte Tunnel
    ngrok_process, tunnel_url = start_ngrok_tunnel()
    if not ngrok_process:
        print(f"\n{Colors.YELLOW}⚠️ Ngrok konnte nicht gestartet werden.{Colors.END}")
        print(f"  Aber Server läuft auf http://localhost:5000\n")
        tunnel_url = None
    
    # Zeige Informationen
    print_usage(tunnel_url)
    
    print(f"{Colors.GREEN}✅ Alles läuft! Bereit für n8n Integration.{Colors.END}\n")
    print(f"{Colors.BOLD}Dashboard:{Colors.END} http://localhost:4040\n")
    
    # Halte am Leben und warte auf Ctrl+C
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}🛑 Fahre herunter...{Colors.END}")
        
        # Beende Prozesse
        if server_process:
            server_process.terminate()
            try:
                server_process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                server_process.kill()
        
        if ngrok_process:
            ngrok_process.terminate()
            try:
                ngrok_process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                ngrok_process.kill()
        
        print(f"{Colors.GREEN}✅ Beendet!{Colors.END}\n")
        sys.exit(0)

if __name__ == "__main__":
    main()
