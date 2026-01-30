# macOS Deployment Guide (V1 Reference)

> **REFERENCE ONLY** — V2 deployment differs (Vercel control plane + self-hosted runner).


## Overview

DOMAIN_EXPANSION deployment guide for **macOS** (development, testing, or local production):
- **Hosting**: macOS (local or always-on Mac)
- **Access**: `dashboard.pthwyconnect.com` via Cloudflare Tunnel
- **Security**: Cloudflare Access + app-level authentication
- **Database**: SQLite (migration path to PostgreSQL available)
- **Backups**: Automated backups stored locally or off-machine

## Prerequisites

- macOS 12.0 (Monterey) or later
- Xcode Command Line Tools
- Homebrew
- Python 3.11+
- Git
- Cloudflare account with domain `pthwyconnect.com`

## Step 1: macOS Initial Setup

### 1.1 Install Xcode Command Line Tools

```bash
xcode-select --install
```

### 1.2 Install Homebrew

If not already installed:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 1.3 Install Python and Dependencies

```bash
brew install python@3.11 git
```

Verify Python installation:
```bash
python3.11 --version
```

## Step 2: Application Deployment

### 2.1 Clone Repository

```bash
cd ~/Documents/Dev_Lab/DOM_EXPv1
cd domain_expansion
```

Or if cloning fresh:
```bash
cd ~/Documents
git clone <repository-url> domain_expansion
cd domain_expansion
```

### 2.2 Create Virtual Environment

```bash
python3.11 -m venv venv
source venv/bin/activate
```

### 2.3 Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 2.4 Configure Environment

```bash
cp .env.example .env
open -e .env  # Opens in TextEdit, or use: nano .env
```

**Critical settings for macOS deployment:**
```bash
# Server - bind to localhost only
HOST=127.0.0.1
PORT=8000

# Security - use strong secret key
SECRET_KEY=<generate-strong-32-char-key>
SESSION_COOKIE_SECURE=true  # Set to true when behind HTTPS
SESSION_COOKIE_HTTPONLY=true

# Base URL for the subdomain
BASE_URL=https://dashboard.pthwyconnect.com

# Admin credentials
ADMIN_USERNAME=admin
ADMIN_PASSWORD=<strong-password>
ADMIN_EMAIL=admin@pthwyconnect.com
```

Generate a secure SECRET_KEY:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2.5 Initialize Database

```bash
python smoke_test.py
```

This will create the database and bootstrap the admin user.

## Step 3: Cloudflare Tunnel Setup

### 3.1 Install Cloudflare Tunnel

```bash
brew install cloudflared
```

### 3.2 Authenticate Cloudflare

```bash
cloudflared tunnel login
```

Follow the prompts to authenticate with your Cloudflare account. This will open a browser window.

### 3.3 Create Tunnel

```bash
cloudflared tunnel create domain-expansion
```

This will create a tunnel and save credentials to `~/.cloudflared/<tunnel-id>.json`

### 3.4 Configure Tunnel Route

Create tunnel configuration file:

```bash
mkdir -p ~/.cloudflared
cat > ~/.cloudflared/config.yml << EOF
tunnel: <tunnel-id>
credentials-file: $HOME/.cloudflared/<tunnel-id>.json

ingress:
  - hostname: dashboard.pthwyconnect.com
    service: http://localhost:8000
  - service: http_status:404
EOF
```

Replace `<tunnel-id>` with the actual tunnel ID from step 3.3.

### 3.5 Create DNS Route

```bash
cloudflared tunnel route dns domain-expansion dashboard.pthwyconnect.com
```

### 3.6 Run Tunnel (Manual)

For testing, run tunnel manually:

```bash
cloudflared tunnel run domain-expansion
```

Keep this terminal open. For production, see Step 5 for launchd service setup.

## Step 4: Cloudflare Access Setup

### 4.1 Create Access Application

1. Log into Cloudflare Dashboard
2. Go to **Zero Trust** → **Access** → **Applications**
3. Click **Add an application**
4. Select **Self-hosted**
5. Configure:
   - **Application name**: DOMAIN_EXPANSION
   - **Session duration**: 24 hours
   - **Application domain**: `dashboard.pthwyconnect.com`
6. Add **Policy**:
   - **Policy name**: Staff Only
   - **Action**: Allow
   - **Include**: Email domain `@pthwyconnect.com` (or specific emails)
7. Save application

### 4.2 Update Tunnel Configuration

The tunnel will automatically use Cloudflare Access policies for the configured domain.

## Step 5: Launchd Service (macOS Background Service)

### 5.1 Create Launch Agent for Application

Create a launchd plist file for the application:

```bash
mkdir -p ~/Library/LaunchAgents
cat > ~/Library/LaunchAgents/com.pthwyconnect.domain-expansion.plist << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.pthwyconnect.domain-expansion</string>
    <key>ProgramArguments</key>
    <array>
        <string>$HOME/Documents/Dev_Lab/DOM_EXPv1/domain_expansion/venv/bin/python</string>
        <string>$HOME/Documents/Dev_Lab/DOM_EXPv1/domain_expansion/run.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>$HOME/Documents/Dev_Lab/DOM_EXPv1/domain_expansion</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$HOME/Library/Logs/domain-expansion.log</string>
    <key>StandardErrorPath</key>
    <string>$HOME/Library/Logs/domain-expansion.error.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>$HOME/Documents/Dev_Lab/DOM_EXPv1/domain_expansion/venv/bin:/usr/local/bin:/usr/bin:/bin</string>
    </dict>
</dict>
</plist>
EOF
```

**Important**: Update the paths in the plist file to match your actual installation directory.

### 5.2 Create Launch Agent for Cloudflare Tunnel

```bash
cat > ~/Library/LaunchAgents/com.cloudflare.tunnel.plist << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.cloudflare.tunnel</string>
    <key>ProgramArguments</key>
    <array>
        <string>/opt/homebrew/bin/cloudflared</string>
        <string>tunnel</string>
        <string>run</string>
        <string>domain-expansion</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$HOME/Library/Logs/cloudflared.log</string>
    <key>StandardErrorPath</key>
    <string>$HOME/Library/Logs/cloudflared.error.log</string>
</dict>
</plist>
EOF
```

**Note**: If Homebrew is installed in `/usr/local` (Intel Macs), use `/usr/local/bin/cloudflared` instead.

### 5.3 Load and Start Services

```bash
# Load application service
launchctl load ~/Library/LaunchAgents/com.pthwyconnect.domain-expansion.plist

# Load Cloudflare Tunnel service
launchctl load ~/Library/LaunchAgents/com.cloudflare.tunnel.plist
```

### 5.4 Verify Services

```bash
# Check application service
launchctl list | grep domain-expansion

# Check Cloudflare Tunnel service
launchctl list | grep cloudflare

# View logs
tail -f ~/Library/Logs/domain-expansion.log
tail -f ~/Library/Logs/cloudflared.log
```

### 5.5 Service Management Commands

```bash
# Start service
launchctl start com.pthwyconnect.domain-expansion

# Stop service
launchctl stop com.pthwyconnect.domain-expansion

# Unload service (disable on startup)
launchctl unload ~/Library/LaunchAgents/com.pthwyconnect.domain-expansion.plist

# Reload service (after editing plist)
launchctl unload ~/Library/LaunchAgents/com.pthwyconnect.domain-expansion.plist
launchctl load ~/Library/LaunchAgents/com.pthwyconnect.domain-expansion.plist
```

## Step 6: Backup Strategy

### 6.1 Create Backup Script

```bash
mkdir -p ~/Documents/backups/domain-expansion
cat > ~/Documents/backups/domain-expansion/backup.sh << 'EOF'
#!/bin/bash
# Backup script for DOMAIN_EXPANSION

BACKUP_DIR="$HOME/Documents/backups/domain-expansion"
APP_DIR="$HOME/Documents/Dev_Lab/DOM_EXPv1/domain_expansion"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p "$BACKUP_DIR/$DATE"

# Backup database
if [ -f "$APP_DIR/data/domain_expansion.db" ]; then
    cp "$APP_DIR/data/domain_expansion.db" "$BACKUP_DIR/$DATE/domain_expansion.db"
fi

# Backup data directory (excluding cache)
if [ -d "$APP_DIR/data" ]; then
    rsync -av --exclude='cache' "$APP_DIR/data/" "$BACKUP_DIR/$DATE/data/"
fi

# Create compressed archive
cd "$BACKUP_DIR"
tar -czf "domain_expansion_$DATE.tar.gz" "$DATE"
rm -rf "$DATE"

# Remove backups older than 30 days
find "$BACKUP_DIR" -name "domain_expansion_*.tar.gz" -mtime +30 -delete

echo "Backup completed: domain_expansion_$DATE.tar.gz"
EOF

chmod +x ~/Documents/backups/domain-expansion/backup.sh
```

### 6.2 Schedule Nightly Backups with launchd

Create a launchd plist for scheduled backups:

```bash
cat > ~/Library/LaunchAgents/com.pthwyconnect.domain-expansion.backup.plist << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.pthwyconnect.domain-expansion.backup</string>
    <key>ProgramArguments</key>
    <array>
        <string>$HOME/Documents/backups/domain-expansion/backup.sh</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>2</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>$HOME/Library/Logs/domain-expansion-backup.log</string>
    <key>StandardErrorPath</key>
    <string>$HOME/Library/Logs/domain-expansion-backup.error.log</string>
</dict>
</plist>
EOF

launchctl load ~/Library/LaunchAgents/com.pthwyconnect.domain-expansion.backup.plist
```

This runs backups at 2 AM daily.

### 6.3 Manual Backup

Run backup manually:
```bash
~/Documents/backups/domain-expansion/backup.sh
```

## Step 7: Git-Based Deployment Workflow

### 7.1 Initial Setup

Ensure the repository is cloned and configured:

```bash
cd ~/Documents/Dev_Lab/DOM_EXPv1/domain_expansion
git remote -v  # Verify remote is configured
```

### 7.2 Deployment Script

Create a deployment script:

```bash
cat > ~/Documents/Dev_Lab/DOM_EXPv1/domain_expansion/deploy.sh << 'EOF'
#!/bin/bash
# Deployment script for DOMAIN_EXPANSION

set -e

APP_DIR="$HOME/Documents/Dev_Lab/DOM_EXPv1/domain_expansion"
cd "$APP_DIR"

echo "Pulling latest changes..."
git pull origin main  # or your default branch

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing/updating dependencies..."
pip install -r requirements.txt

echo "Running database migrations (if any)..."
# Add migration commands here when using Alembic

echo "Restarting service..."
launchctl stop com.pthwyconnect.domain-expansion
sleep 2
launchctl start com.pthwyconnect.domain-expansion

echo "Checking service status..."
sleep 2
launchctl list | grep domain-expansion

echo "Deployment complete!"
EOF

chmod +x ~/Documents/Dev_Lab/DOM_EXPv1/domain_expansion/deploy.sh
```

### 7.3 Deploy Updates

To deploy updates:

```bash
~/Documents/Dev_Lab/DOM_EXPv1/domain_expansion/deploy.sh
```

## Step 8: Monitoring and Maintenance

### 8.1 View Logs

```bash
# Application logs
tail -f ~/Library/Logs/domain-expansion.log
tail -f ~/Library/Logs/domain-expansion.error.log

# Cloudflare Tunnel logs
tail -f ~/Library/Logs/cloudflared.log
tail -f ~/Library/Logs/cloudflared.error.log

# Backup logs
tail -f ~/Library/Logs/domain-expansion-backup.log
```

### 8.2 Health Check

The application provides a health endpoint:
```bash
curl http://localhost:8000/health
```

### 8.3 Update Process

1. Pull latest code: `git pull`
2. Run deployment script: `./deploy.sh`
3. Monitor logs: `tail -f ~/Library/Logs/domain-expansion.log`

### 8.4 Check Service Status

```bash
# List all loaded services
launchctl list | grep -E "(domain-expansion|cloudflare)"

# Check if service is running
ps aux | grep "run.py"
ps aux | grep cloudflared
```

## Step 9: Security Hardening

### 9.1 macOS Firewall

Enable macOS built-in firewall:

1. System Settings → Network → Firewall
2. Turn on Firewall
3. Click "Firewall Options"
4. Enable "Block all incoming connections" (optional, may interfere with Cloudflare Tunnel)

**Note**: Cloudflare Tunnel doesn't require opening ports - it uses outbound connections.

### 9.2 File Permissions

Ensure proper file permissions:

```bash
# Make sure data directory is writable
chmod -R u+w ~/Documents/Dev_Lab/DOM_EXPv1/domain_expansion/data

# Protect .env file
chmod 600 ~/Documents/Dev_Lab/DOM_EXPv1/domain_expansion/.env
```

### 9.3 System Updates

Keep macOS and Homebrew packages updated:

```bash
# Update Homebrew packages
brew update && brew upgrade

# Update Python packages
source ~/Documents/Dev_Lab/DOM_EXPv1/domain_expansion/venv/bin/activate
pip list --outdated
pip install --upgrade -r requirements.txt
```

## Troubleshooting

### Service won't start

```bash
# Check logs
tail -50 ~/Library/Logs/domain-expansion.error.log

# Check if service is loaded
launchctl list | grep domain-expansion

# Check file permissions
ls -la ~/Documents/Dev_Lab/DOM_EXPv1/domain_expansion/

# Verify virtual environment
source ~/Documents/Dev_Lab/DOM_EXPv1/domain_expansion/venv/bin/activate
python --version

# Test manual run
cd ~/Documents/Dev_Lab/DOM_EXPv1/domain_expansion
source venv/bin/activate
python run.py
```

### Cloudflare Tunnel issues

```bash
# Check if tunnel service is running
launchctl list | grep cloudflare
ps aux | grep cloudflared

# View tunnel logs
tail -f ~/Library/Logs/cloudflared.error.log

# Test tunnel manually
cloudflared tunnel run domain-expansion

# Verify tunnel configuration
cat ~/.cloudflared/config.yml
```

### Database issues

```bash
# Check database file permissions
ls -la ~/Documents/Dev_Lab/DOM_EXPv1/domain_expansion/data/

# Verify database integrity
sqlite3 ~/Documents/Dev_Lab/DOM_EXPv1/domain_expansion/data/domain_expansion.db "PRAGMA integrity_check;"

# Check database size
du -h ~/Documents/Dev_Lab/DOM_EXPv1/domain_expansion/data/domain_expansion.db
```

### Port already in use

```bash
# Find what's using port 8000
lsof -i :8000

# Kill the process if needed
kill -9 <PID>
```

## Migration to PostgreSQL (Optional)

When ready to migrate from SQLite to PostgreSQL:

### 1. Install PostgreSQL

```bash
brew install postgresql@15
brew services start postgresql@15
```

### 2. Create Database and User

```bash
# Create database
createdb domain_expansion

# Create user (optional, can use your macOS user)
psql postgres
CREATE USER domain_expansion_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE domain_expansion TO domain_expansion_user;
\q
```

### 3. Update `.env`

```bash
DATABASE_URL=postgresql://domain_expansion_user:secure_password@localhost/domain_expansion
```

Or if using your macOS user:
```bash
DATABASE_URL=postgresql://localhost/domain_expansion
```

### 4. Run Migrations

When Alembic is configured, run migrations:
```bash
source venv/bin/activate
alembic upgrade head
```

## Running in Development Mode

For development with auto-reload:

```bash
cd ~/Documents/Dev_Lab/DOM_EXPv1/domain_expansion
source venv/bin/activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Support

For issues or questions:
- Check application logs: `tail -f ~/Library/Logs/domain-expansion.log`
- Review Cloudflare Tunnel logs: `tail -f ~/Library/Logs/cloudflared.log`
- Verify service status: `launchctl list | grep domain-expansion`
- Check macOS Console.app for system-level errors

## Notes

- **Paths**: Update all paths in this guide to match your actual installation directory
- **Homebrew Location**: Intel Macs use `/usr/local`, Apple Silicon (M1/M2) uses `/opt/homebrew`
- **Launchd**: Services run as your user account, not root
- **Sleep Prevention**: If running on a Mac that sleeps, consider using `caffeinate` or preventing sleep during backup windows
- **Backups**: Consider using Time Machine or cloud backup for additional redundancy
