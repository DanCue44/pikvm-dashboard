#!/bin/bash
#
# PiKVM Control Dashboard - Automated Installer
# This script installs the complete dashboard including backend service
#
# Usage:
#   curl -sSL https://raw.githubusercontent.com/DanCue44/pikvm-dashboard/main/install.sh | sudo bash
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
GITHUB_USER="DanCue44"
GITHUB_REPO="pikvm-dashboard"
GITHUB_BRANCH="main"
BASE_URL="https://raw.githubusercontent.com/${GITHUB_USER}/${GITHUB_REPO}/${GITHUB_BRANCH}"

DASHBOARD_HTML_URL="${BASE_URL}/pikvm-dashboard.html"
BACKEND_SCRIPT_URL="${BASE_URL}/pikvm_dashboard_service.py"
SYSTEMD_SERVICE_URL="${BASE_URL}/pikvm-dashboard.service"

# File paths
DASHBOARD_PATH="/usr/share/kvmd/web/pikvm-dashboard.html"
BACKEND_PATH="/usr/local/bin/pikvm_dashboard_service.py"
SERVICE_PATH="/etc/systemd/system/pikvm-dashboard.service"
VENV_PATH="/var/lib/pikvm-dashboard/venv"
DATA_PATH="/var/lib/pikvm-dashboard"
BACKUP_PATH="/var/lib/pikvm-dashboard/backup"

# ============ HELPER FUNCTIONS ============

# Detect if a terminal is available for user prompts (works even when piped via curl)
HAS_TTY=false
if [ -e /dev/tty ]; then
    HAS_TTY=true
fi

print_header() {
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════════════════════╗"
    echo "║   PiKVM Control Dashboard - Installer v1.0            ║"
    echo "╚════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Check if filesystem is writable
check_rw_mode() {
    if ! touch /tmp/.pikvm_rw_test 2>/dev/null; then
        echo -e "${RED}Error: Filesystem is not writable!${NC}"
        echo -e "${YELLOW}Please run 'rw' first, then run this installer again.${NC}"
        exit 1
    fi
    rm -f /tmp/.pikvm_rw_test
}

print_step() {
    echo -e "${CYAN}▶ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# ============ DETECTION FUNCTION ============

check_existing_installation() {
    local installed=0
    
    if [ -f "$DASHBOARD_PATH" ]; then
        ((installed++))
    fi
    
    if [ -f "$BACKEND_PATH" ]; then
        ((installed++))
    fi
    
    if [ -f "$SERVICE_PATH" ]; then
        ((installed++))
    fi
    
    if [ -d "$DATA_PATH" ]; then
        ((installed++))
    fi
    
    echo $installed
}

# ============ UNINSTALL FUNCTION ============

uninstall_dashboard() {
    echo
    print_header
    echo -e "${YELLOW}UNINSTALLATION MODE${NC}"
    echo
    
    print_warning "This will remove ALL dashboard files and data."
    echo
    read -p "Are you sure you want to uninstall? (yes/no): " confirm < /dev/tty
    
    if [ "$confirm" != "yes" ]; then
        echo -e "${CYAN}Uninstallation cancelled.${NC}"
        exit 0
    fi
    
    echo
    print_step "Making filesystem writable..."
    rw || true
    
    print_step "Stopping and disabling service..."
    systemctl stop pikvm-dashboard.service 2>/dev/null || true
    systemctl disable pikvm-dashboard.service 2>/dev/null || true
    
    print_step "Removing files..."
    rm -f "$SERVICE_PATH"
    rm -f "$BACKEND_PATH"
    rm -f "$DASHBOARD_PATH"
    
    # Restore original nginx config if backup exists
    if [ -f /etc/kvmd/nginx/kvmd.ctx-server.conf.original ]; then
        cp /etc/kvmd/nginx/kvmd.ctx-server.conf.original /etc/kvmd/nginx/kvmd.ctx-server.conf
        print_success "Nginx config restored"
    fi
    
    systemctl daemon-reload
    systemctl restart kvmd-nginx 2>/dev/null || true
    
    # Ask about data
    echo
    read -p "Do you want to remove all data (configs, logs, schedules, icons, etc.)? (yes/no): " remove_data < /dev/tty
    
    if [ "$remove_data" = "yes" ]; then
        rm -rf "$DATA_PATH"
        rm -rf "/usr/share/kvmd/web/dashboard-images"
        print_success "All data removed (including custom icons)"
    else
        print_warning "Data preserved in $DATA_PATH and /usr/share/kvmd/web/dashboard-images"
    fi
    
    print_step "Making filesystem read-only..."
    ro || true
    
    echo
    print_success "Dashboard uninstalled successfully!"
    echo
    exit 0
}

# ============ BACKUP FUNCTION ============

backup_existing_data() {
    if [ -d "$DATA_PATH" ]; then
        print_step "Backing up existing data..."
        mkdir -p "$BACKUP_PATH"
        local backup_file="$BACKUP_PATH/backup-$(date +%Y%m%d-%H%M%S).tar.gz"
        
        tar -czf "$backup_file" -C "$DATA_PATH" \
            action_log.json preferences.json schedules.json uptime.json config.json .credentials 2>/dev/null || true
        
        if [ -f "$backup_file" ]; then
            print_success "Backup created: $backup_file"
        fi
    fi
}

# ============ MAIN INSTALLATION ============

install_dashboard() {
    print_header
    
    # Check RW mode first
    check_rw_mode
    
    echo -e "${GREEN}INSTALLATION MODE${NC}"
    echo
    echo "This will install:"
    echo "  - Dashboard web interface"
    echo "  - Backend service (Flask API)"
    echo "  - Systemd service for auto-start"
    echo "  - Nginx authentication exception"
    echo
    
    # Check if running interactively
    if [ "$HAS_TTY" = true ]; then
        # Interactive mode - ask for confirmation
        read -p "Do you want to continue? (y/n) " -r < /dev/tty
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo -e "${YELLOW}Installation cancelled.${NC}"
            exit 0
        fi
    else
        # Non-interactive mode - auto-continue
        echo -e "${CYAN}Non-interactive mode: auto-continuing...${NC}"
    fi
    
    echo
    
    # Check for existing credentials from multiple sources
    CREDS_FILE="$DATA_PATH/.credentials"
    CREDS_VALID=false
    
    # Source 1: Dedicated credentials file (created by previous installs)
    if [ "$CREDS_VALID" = false ] && [ -f "$CREDS_FILE" ]; then
        PIKVM_USER=$(grep -o '"username": *"[^"]*"' "$CREDS_FILE" 2>/dev/null | head -1 | cut -d'"' -f4)
        PIKVM_PASS=$(grep -o '"password": *"[^"]*"' "$CREDS_FILE" 2>/dev/null | head -1 | cut -d'"' -f4)
        
        if [ -n "$PIKVM_USER" ] && [ -n "$PIKVM_PASS" ]; then
            echo -e "${CYAN}Found saved credentials. Verifying...${NC}"
            HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -u "${PIKVM_USER}:${PIKVM_PASS}" https://localhost/api/auth/check -k 2>/dev/null)
            
            if [ "$HTTP_CODE" = "200" ]; then
                echo -e "${GREEN}✓ Saved credentials valid${NC}"
                CREDS_VALID=true
            else
                echo -e "${YELLOW}⚠ Saved credentials invalid${NC}"
            fi
        fi
    fi
    
    # Source 2: Extract from existing installed HTML file
    if [ "$CREDS_VALID" = false ] && [ -f "$DASHBOARD_PATH" ]; then
        PIKVM_USER=$(grep -o "EMBEDDED_USERNAME = '[^']*'" "$DASHBOARD_PATH" 2>/dev/null | head -1 | cut -d"'" -f2)
        PIKVM_PASS=$(grep -o "EMBEDDED_PASSWORD = '[^']*'" "$DASHBOARD_PATH" 2>/dev/null | head -1 | cut -d"'" -f2)
        
        # Skip if still has placeholder values
        if [ -n "$PIKVM_USER" ] && [ "$PIKVM_USER" != "PIKVM_USERNAME_PLACEHOLDER" ] && \
           [ -n "$PIKVM_PASS" ] && [ "$PIKVM_PASS" != "PIKVM_PASSWORD_PLACEHOLDER" ]; then
            echo -e "${CYAN}Found credentials in existing dashboard. Verifying...${NC}"
            HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -u "${PIKVM_USER}:${PIKVM_PASS}" https://localhost/api/auth/check -k 2>/dev/null)
            
            if [ "$HTTP_CODE" = "200" ]; then
                echo -e "${GREEN}✓ Existing credentials valid${NC}"
                CREDS_VALID=true
                # Save to credentials file for future updates
                mkdir -p "$DATA_PATH"
                echo "{\"username\": \"$PIKVM_USER\", \"password\": \"$PIKVM_PASS\"}" > "$CREDS_FILE"
                chmod 600 "$CREDS_FILE"
            else
                echo -e "${YELLOW}⚠ Existing credentials invalid${NC}"
            fi
        fi
    fi
    
    # If no valid credentials and no terminal available, fail gracefully
    if [ "$CREDS_VALID" = false ] && [ "$HAS_TTY" != true ]; then
        echo
        echo -e "${RED}ERROR: No saved credentials found and no terminal available for input.${NC}"
        echo
        echo "Please run the installer from an SSH session or terminal:"
        echo "  curl -sSL https://raw.githubusercontent.com/DanCue44/pikvm-dashboard/main/install.sh | sudo bash"
        echo
        exit 1
    fi
    
    # Collect PiKVM credentials if not already valid
    if [ "$CREDS_VALID" = false ]; then
        echo -e "${CYAN}PiKVM Credentials${NC}"
        echo "The dashboard needs your PiKVM credentials to authenticate API requests."
        echo
        
        # Loop until credentials are valid
        while [ "$CREDS_VALID" = false ]; do
            read -p "Enter PiKVM username (default: admin): " PIKVM_USER < /dev/tty
            PIKVM_USER=${PIKVM_USER:-admin}
            
            read -sp "Enter PiKVM password: " PIKVM_PASS < /dev/tty
            echo
            
            if [ -z "$PIKVM_PASS" ]; then
                echo -e "${RED}Error: Password cannot be empty${NC}"
                continue
            fi
            
            # Test credentials
            echo -e "${CYAN}Testing credentials...${NC}"
            HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -u "${PIKVM_USER}:${PIKVM_PASS}" https://localhost/api/auth/check -k)
            
            if [ "$HTTP_CODE" = "200" ]; then
                echo -e "${GREEN}✓ Credentials valid${NC}"
                CREDS_VALID=true
                # Save credentials for future updates
                mkdir -p "$DATA_PATH"
                echo "{\"username\": \"$PIKVM_USER\", \"password\": \"$PIKVM_PASS\"}" > "$CREDS_FILE"
                chmod 600 "$CREDS_FILE"
            else
                echo -e "${RED}✗ Authentication failed (HTTP $HTTP_CODE)${NC}"
                echo -e "${YELLOW}Please try again.${NC}"
                echo
            fi
        done
    fi
    
    echo

# Step 1: Make filesystem writable
echo -e "${BLUE}[1/9] Making filesystem writable...${NC}"
rw || true  # Don't fail if already writable

# Step 2: Install Python dependencies
echo -e "${BLUE}[2/9] Installing Python dependencies...${NC}"
if ! pacman -Q python-requests python-flask python-flask-cors &>/dev/null; then
    echo "Installing packages via pacman..."
    pacman -Sy --noconfirm python-requests python-flask python-flask-cors
else
    echo "Python packages already installed, skipping..."
fi

# Step 3: Create virtual environment
echo -e "${BLUE}[3/9] Creating Python virtual environment...${NC}"
if [ ! -d "$VENV_PATH" ]; then
    python3 -m venv "$VENV_PATH"
    source "$VENV_PATH/bin/activate"
    pip install --quiet requests flask flask-cors
    deactivate
    echo "Virtual environment created successfully"
else
    echo "Virtual environment already exists, updating packages..."
    source "$VENV_PATH/bin/activate"
    pip install --quiet --upgrade requests flask flask-cors
    deactivate
fi

# Step 4: Create data directory
echo -e "${BLUE}[4/9] Creating data directory...${NC}"
mkdir -p "$DATA_PATH"
chmod 755 "$DATA_PATH"

# Create images directory for custom icons
echo -e "${BLUE}[4.5/9] Creating images directory for custom icons...${NC}"
mkdir -p "/usr/share/kvmd/web/dashboard-images"
chmod 755 "/usr/share/kvmd/web/dashboard-images"
echo -e "${GREEN}✓ Images directory created at /usr/share/kvmd/web/dashboard-images${NC}"
echo -e "${YELLOW}ℹ Place custom icon images in this directory${NC}"

# Step 5: Install dashboard HTML
echo -e "${BLUE}[5/11] Installing dashboard HTML...${NC}"
if [ -f "pikvm-dashboard.html" ]; then
    echo "Using local pikvm-dashboard.html file..."
    # Inject credentials into the HTML
    sed "s/PIKVM_USERNAME_PLACEHOLDER/$PIKVM_USER/g; s/PIKVM_PASSWORD_PLACEHOLDER/$PIKVM_PASS/g" \
        pikvm-dashboard.html > "$DASHBOARD_PATH"
else
    echo "Downloading dashboard HTML from GitHub..."
    if curl -fsSL "$DASHBOARD_HTML_URL" -o /tmp/dashboard-temp.html; then
        # Inject credentials into the downloaded HTML
        sed "s/PIKVM_USERNAME_PLACEHOLDER/$PIKVM_USER/g; s/PIKVM_PASSWORD_PLACEHOLDER/$PIKVM_PASS/g" \
            /tmp/dashboard-temp.html > "$DASHBOARD_PATH"
        rm -f /tmp/dashboard-temp.html
        echo -e "${GREEN}✓ Dashboard HTML downloaded successfully${NC}"
    else
        echo -e "${RED}✗ Failed to download dashboard HTML${NC}"
        echo "URL: $DASHBOARD_HTML_URL"
        echo "Please check your GitHub configuration or place file locally."
        exit 1
    fi
fi

# Fix permissions so nginx can read the file
chmod 644 "$DASHBOARD_PATH"
echo -e "${GREEN}✓ Dashboard HTML installed${NC}"

# Step 5.5: Install dashboard images (logo and icons)
echo -e "${BLUE}[5.5/11] Installing dashboard images...${NC}"
WEB_ROOT="/usr/share/kvmd/web"

# Install logo.png
if [ -f "logo.png" ]; then
    echo "Copying local logo.png..."
    cp logo.png "$WEB_ROOT/logo.png"
    chmod 644 "$WEB_ROOT/logo.png"
    echo -e "${GREEN}✓ logo.png installed${NC}"
else
    echo -e "${YELLOW}⚠ logo.png not found locally, will use PiKVM default${NC}"
fi

# Install apple-touch-icon.png
if [ -f "apple-touch-icon.png" ]; then
    echo "Copying local apple-touch-icon.png..."
    cp apple-touch-icon.png "$WEB_ROOT/apple-touch-icon.png"
    chmod 644 "$WEB_ROOT/apple-touch-icon.png"
    echo -e "${GREEN}✓ apple-touch-icon.png installed${NC}"
else
    echo -e "${YELLOW}⚠ apple-touch-icon.png not found locally${NC}"
fi

# Download switch image for wizard
echo "Downloading PiKVM switch image for wizard..."
if curl -fsSL "https://pikvm.org/images/product_switch.webp" -o "$WEB_ROOT/pikvm-switch.webp"; then
    chmod 644 "$WEB_ROOT/pikvm-switch.webp"
    echo -e "${GREEN}✓ Switch image downloaded${NC}"
else
    echo -e "${YELLOW}⚠ Switch image download failed (non-critical)${NC}"
fi

# Step 6: Install backend service script
echo -e "${BLUE}[6/9] Installing backend service script...${NC}"
if [ -f "pikvm_dashboard_service.py" ]; then
    echo "Using local pikvm_dashboard_service.py file..."
    cp pikvm_dashboard_service.py "$BACKEND_PATH"
    chmod +x "$BACKEND_PATH"
else
    echo "Downloading backend script from GitHub..."
    if curl -fsSL "$BACKEND_SCRIPT_URL" -o "$BACKEND_PATH"; then
        chmod +x "$BACKEND_PATH"
        echo -e "${GREEN}✓ Backend script downloaded successfully${NC}"
    else
        echo -e "${RED}✗ Failed to download backend script${NC}"
        echo "URL: $BACKEND_SCRIPT_URL"
        echo "Please check your GitHub configuration or place file locally."
        exit 1
    fi
fi

# Step 7: Install systemd service
echo -e "${BLUE}[7/9] Installing systemd service...${NC}"
if [ -f "pikvm-dashboard.service" ]; then
    echo "Using local pikvm-dashboard.service file..."
    cp pikvm-dashboard.service "$SERVICE_PATH"
else
    echo "Downloading systemd service from GitHub..."
    if curl -fsSL "$SYSTEMD_SERVICE_URL" -o "$SERVICE_PATH" 2>/dev/null; then
        echo -e "${GREEN}✓ Systemd service downloaded successfully${NC}"
    else
        echo "GitHub download failed, creating service file locally..."
        cat > "$SERVICE_PATH" << 'EOF'
[Unit]
Description=PiKVM Dashboard Backend Service
After=network.target kvmd.service

[Service]
Type=simple
User=root
WorkingDirectory=/usr/local/bin
ExecStart=/var/lib/pikvm-dashboard/venv/bin/python /usr/local/bin/pikvm_dashboard_service.py
Restart=always
RestartSec=10

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=pikvm-dashboard

[Install]
WantedBy=multi-user.target
EOF
        echo -e "${GREEN}✓ Service file created${NC}"
    fi
fi

# Step 9: Configure nginx for dashboard access
echo -e "${BLUE}[9/11] Configuring nginx for dashboard access...${NC}"

# Backup original nginx config if not already backed up
if [ ! -f /etc/kvmd/nginx/kvmd.ctx-server.conf.original ]; then
    cp /etc/kvmd/nginx/kvmd.ctx-server.conf /etc/kvmd/nginx/kvmd.ctx-server.conf.original
fi

# Check if our config is already there
if grep -q "# Dashboard - pikvm-dashboard installer" /etc/kvmd/nginx/kvmd.ctx-server.conf; then
    echo "Dashboard nginx config already present, skipping..."
else
    # Create temp file with dashboard config inserted before "location /" block
    awk '
    /^location \/ \{/ && !inserted {
        print "# Dashboard - pikvm-dashboard installer"
        print "location = /pikvm-dashboard.html {"
        print "\troot /usr/share/kvmd/web;"
        print "\tinclude /etc/kvmd/nginx/loc-nocache.conf;"
        print "\tauth_request off;"
        print "}"
        print ""
        print "location /api/dashboard/ {"
        print "\tproxy_pass http://127.0.0.1:5000/api/dashboard/;"
        print "\tproxy_set_header Host $host;"
        print "\tproxy_set_header X-Real-IP $remote_addr;"
        print "\tproxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;"
        print "\tproxy_set_header X-Forwarded-Proto $scheme;"
        print "\tauth_request off;"
        print "}"
        print ""
        inserted=1
    }
    {print}
    ' /etc/kvmd/nginx/kvmd.ctx-server.conf > /tmp/kvmd.ctx-server.conf.new
    
    # Replace the file
    mv /tmp/kvmd.ctx-server.conf.new /etc/kvmd/nginx/kvmd.ctx-server.conf
    echo -e "${GREEN}✓ Nginx config updated${NC}"
fi

# Restart nginx to apply changes
systemctl restart kvmd-nginx
echo -e "${GREEN}✓ Nginx restarted${NC}"

# Step 10: Enable and start service
echo -e "${BLUE}[10/11] Enabling and starting backend service...${NC}"
systemctl daemon-reload
systemctl enable pikvm-dashboard.service
systemctl restart pikvm-dashboard.service

# Wait a moment for service to start
sleep 2

# Check if service is running
if systemctl is-active --quiet pikvm-dashboard.service; then
    echo -e "${GREEN}✓ Backend service started successfully${NC}"
else
    echo -e "${RED}✗ Backend service failed to start${NC}"
    echo "Check logs with: journalctl -u pikvm-dashboard.service -n 50"
fi

# Step 11: Test API
echo -e "${BLUE}[11/11] Testing API...${NC}"
sleep 1
if curl -s http://localhost:5000/api/dashboard/preferences > /dev/null; then
    echo -e "${GREEN}✓ API is responding${NC}"
else
    echo -e "${YELLOW}⚠ API test failed - service may still be starting${NC}"
fi

# Make filesystem read-only
echo
echo -e "${BLUE}Making filesystem read-only...${NC}"
ro || true

# Final status check
echo
echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║            Installation Complete!                      ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo
echo -e "${BLUE}Dashboard URL:${NC} https://your-pikvm-ip/pikvm-dashboard.html"
echo -e "${BLUE}Backend Service:${NC} $(systemctl is-active pikvm-dashboard.service)"
echo
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Navigate to the dashboard URL in your browser"
echo "2. Log in with your PiKVM credentials"
echo "3. Customize PC names if needed (edit $DASHBOARD_PATH)"
echo
echo -e "${BLUE}Useful Commands:${NC}"
echo "  Check service status:  systemctl status pikvm-dashboard.service"
echo "  View logs:             journalctl -u pikvm-dashboard.service -f"
echo "  Restart service:       systemctl restart pikvm-dashboard.service"
echo "  Test API:              curl http://localhost:5000/api/dashboard/preferences"
echo
echo -e "${GREEN}Installation log saved to: /tmp/pikvm-dashboard-install.log${NC}"
echo

# Save installation info
cat > /tmp/pikvm-dashboard-install.log << EOF
PiKVM Control Dashboard Installation
Date: $(date)
Dashboard Path: $DASHBOARD_PATH
Backend Path: $BACKEND_PATH
Service Path: $SERVICE_PATH
Data Path: $DATA_PATH
Virtual Environment: $VENV_PATH
Service Status: $(systemctl is-active pikvm-dashboard.service)
EOF

}  # End of install_dashboard function

# ============ MAIN ENTRY POINT ============

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "This script must be run as root"
    echo "Please run: sudo bash $0"
    exit 1
fi

# Check for existing installation
existing=$(check_existing_installation)

if [ "$existing" -gt 0 ]; then
    print_header
    echo -e "${YELLOW}EXISTING INSTALLATION DETECTED${NC}"
    echo
    echo "Found $existing component(s) already installed."
    echo
    
    # Check if running interactively (stdin is a terminal)
    if [ "$HAS_TTY" = true ]; then
        # Interactive mode - show menu
        echo "What would you like to do?"
        echo "  1) Reinstall (update files, keep data)"
        echo "  2) Fresh Reinstall (update files, delete data)"
        echo "  3) Uninstall (remove everything)"
        echo "  4) Cancel"
        echo
        read -p "Enter your choice (1-4): " choice < /dev/tty
    else
        # No terminal available (e.g., cron job) - default to reinstall
        echo -e "${CYAN}No terminal detected. Defaulting to reinstall (update files, keep data)...${NC}"
        echo
        choice=1
    fi
    
    case $choice in
        1)
            print_step "Making filesystem writable..."
            rw || true
            backup_existing_data
            install_dashboard
            ;;
        2)
            echo -e "${YELLOW}WARNING: This will delete all configuration, logs, and preferences!${NC}"
            read -p "Are you sure? (y/n) " -r < /dev/tty
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                print_step "Making filesystem writable..."
                rw || true
                print_step "Removing old data..."
                rm -rf "$DATA_PATH"
                rm -rf "/usr/share/kvmd/web/dashboard-images"
                print_success "Data removed"
                install_dashboard
            else
                echo -e "${CYAN}Cancelled.${NC}"
                exit 0
            fi
            ;;
        3)
            uninstall_dashboard
            ;;
        4)
            echo -e "${CYAN}Operation cancelled.${NC}"
            exit 0
            ;;
        *)
            print_error "Invalid choice. Exiting."
            exit 1
            ;;
    esac
else
    # Fresh installation
    install_dashboard
fi

exit 0
