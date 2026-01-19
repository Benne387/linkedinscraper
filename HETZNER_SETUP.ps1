# Hetzner Deployment Script (Automated)
# Usage: ./HETZNER_SETUP.ps1

Write-Host "🚀 Starting Deployment to Hetzner..." -ForegroundColor Green

# 1. Ask for IP
$HetznerIP = Read-Host "Please enter your Hetzner Server IP (e.g., 123.45.67.89)"
$User = "root"

if ([string]::IsNullOrWhiteSpace($HetznerIP)) {
    Write-Host "❌ IP required!" -ForegroundColor Red
    exit
}

# 2. Cleanup local temp files (optional)
# (none needed, we use .dockerignore for the build, but for SCP we need to be careful)

# 3. Create a clean deployment folder locally? 
# No, we just scp the current folder but exclude junk
# Windows scp does not support --exclude well, so we create a tar or just copy everything and let user ignore venv
# Better approach: Create a temp "deploy" folder, copy only what we need, then scp THAT.

$DeployFolder = ".\deploy_package"
if (Test-Path $DeployFolder) { Remove-Item $DeployFolder -Recurse -Force }
New-Item -ItemType Directory -Path $DeployFolder | Out-Null

Write-Host "📦 Preparing files..." -ForegroundColor Cyan
# Copy core files
Copy-Item "Dockerfile" -Destination $DeployFolder
Copy-Item "docker-compose.yml" -Destination $DeployFolder
Copy-Item "requirements.txt" -Destination $DeployFolder
Copy-Item "run.py" -Destination $DeployFolder
Copy-Item "start.py" -Destination $DeployFolder

# Copy folders
Copy-Item "app" -Destination $DeployFolder -Recurse
Copy-Item "linkedin_session" -Destination $DeployFolder -Recurse
# check if scraped_data exists
if (Test-Path "scraped_data") { Copy-Item "scraped_data" -Destination $DeployFolder -Recurse }

Write-Host "📤 Uploading to $HetznerIP..." -ForegroundColor Cyan
# Create remote directory
ssh ${User}@${HetznerIP} "mkdir -p /root/scraper"

# Copy contents
# Using scp -r deploy_package/* to remote
scp -r example_placeholder ${User}@${HetznerIP}:/root/scraper
# Actual command needs to use the variable properly. PowerShell escaping is tricky with scp.
# scp -r .\deploy_package\* root@ip:/root/scraper is hard in one go.
# Easiest: Copy the folder itself.
# Copy the deployment package
Write-Host "  → Uploading package... (Password might be requested)"
scp -r $DeployFolder "${User}@${HetznerIP}:/root/"

# Move and Run on Server
Write-Host "  → Installing on Server..."
$RemoteCommands = "
    mv /root/deploy_package /root/scraper_new
    rm -rf /root/scraper
    mv /root/scraper_new /root/scraper
    cd /root/scraper
    echo '� Building Docker Container...'
    docker-compose up -d --build
"
ssh ${User}@${HetznerIP} $RemoteCommands

Write-Host "`n✅ Deployment Complete!" -ForegroundColor Green
Write-Host "🌍 App is live at: http://${HetznerIP}"
