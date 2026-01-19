# COPY-PASTE IN POWERSHELL!
# Alle Dateien zu Hetzner hochladen

$IP = "188.245.243.159"

Write-Host "📤 Uploading to Hetzner ($IP)..." -ForegroundColor Green

# 1. Python-Dateien hochladen
scp scrape_n8n.py root@${IP}:/opt/linkedinscraper/
scp scrape_batch.py root@${IP}:/opt/linkedinscraper/
scp scrape_api.py root@${IP}:/opt/linkedinscraper/
scp requirements.txt root@${IP}:/opt/linkedinscraper/

# 2. ⭐ WICHTIG: Session-Cookies hochladen!
scp -r linkedin_session root@${IP}:/opt/linkedinscraper/

# 3. Setup-Scripts hochladen
scp hetzner-setup.sh root@${IP}:/opt/linkedinscraper/

Write-Host "`n✅ Upload fertig!" -ForegroundColor Green
Write-Host "`nNächster Schritt:" -ForegroundColor Yellow
Write-Host "ssh root@${IP}"
Write-Host "cd /opt/linkedinscraper"
Write-Host "python3 -m venv venv"
Write-Host "source venv/bin/activate"
Write-Host "pip install selenium webdriver-manager"
