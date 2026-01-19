#!/bin/bash
# Hetzner Setup Script - Führe AUF Hetzner aus!
# ssh root@deine-ip
# curl -fsSL https://your-domain/hetzner-setup.sh | bash

set -e  # Exit on error

echo "=================================================="
echo "🚀 LinkedIn Scraper - Hetzner Setup"
echo "=================================================="

# 1. In /opt gehen
cd /opt

# 2. Verzeichnis erstellen falls nicht vorhanden
if [ ! -d "linkedinscraper" ]; then
    mkdir -p linkedinscraper
    echo "✅ Folder /opt/linkedinscraper erstellt"
else
    echo "ℹ️  Folder /opt/linkedinscraper existiert bereits"
fi

cd linkedinscraper

# 3. Virtual Environment erstellen
if [ ! -d "venv" ]; then
    echo "📦 Erstelle Python venv..."
    python3 -m venv venv
    echo "✅ venv erstellt"
else
    echo "ℹ️  venv existiert bereits"
fi

# 4. Dependencies installieren
echo "📥 Installiere Dependencies..."
source venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
pip install selenium webdriver-manager > /dev/null 2>&1
echo "✅ Dependencies installiert"

# 5. Überprüfe ob Dateien vorhanden sind
echo ""
echo "=================================================="
echo "📋 Status Check"
echo "=================================================="

if [ -f "scrape_n8n.py" ]; then
    echo "✅ scrape_n8n.py vorhanden"
else
    echo "❌ scrape_n8n.py FEHLT - Bitte via SCP hochladen"
fi

if [ -f "scrape_batch.py" ]; then
    echo "✅ scrape_batch.py vorhanden"
else
    echo "❌ scrape_batch.py FEHLT - Bitte via SCP hochladen"
fi

if [ -d "linkedin_session" ]; then
    echo "✅ linkedin_session Folder vorhanden (mit Cookies)"
else
    echo "⚠️  linkedin_session FEHLT - Session-Login wird nötig sein"
fi

echo ""
echo "=================================================="
echo "✨ Setup Fertig!"
echo "=================================================="
echo ""
echo "Test starten:"
echo "  cd /opt/linkedinscraper"
echo "  source venv/bin/activate"
echo "  python scrape_n8n.py 'https://linkedin.com/in/test'"
echo ""
echo "n8n Command:"
echo "  /opt/linkedinscraper/venv/bin/python /opt/linkedinscraper/scrape_n8n.py"
echo ""
