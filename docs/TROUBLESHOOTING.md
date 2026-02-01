# PiKVM Dashboard Troubleshooting Guide

Common issues and their solutions.

---

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Dashboard Not Loading](#dashboard-not-loading)
3. [Connection & Authentication](#connection--authentication)
4. [Power Controls Not Working](#power-controls-not-working)
5. [Scheduled Actions Issues](#scheduled-actions-issues)
6. [Theme & Display Issues](#theme--display-issues)
7. [Performance Issues](#performance-issues)
8. [Service & Backend Issues](#service--backend-issues)
9. [Browser-Specific Issues](#browser-specific-issues)
10. [Getting Debug Information](#getting-debug-information)

---

## Installation Issues

### Installation script fails with "filesystem not writable"

**Symptom**: Error message about read-only filesystem

**Solution**:
```bash
# Enter read-write mode first
rw

# Then run the installer
curl -sSL https://raw.githubusercontent.com/DanCue44/pikvm-dashboard/main/install.sh | sudo bash

# Return to read-only mode after (optional, for security)
ro
```

### "Permission denied" errors

**Symptom**: Script fails with permission errors

**Solution**:
```bash
# Make sure to run with sudo
sudo bash install.sh

# Or use sudo with curl
curl -sSL https://raw.githubusercontent.com/DanCue44/pikvm-dashboard/main/install.sh | sudo bash
```

### Download fails / Network errors

**Symptom**: curl fails to download files

**Solution**:
1. Check network connectivity:
   ```bash
   ping google.com
   ```

2. Check DNS resolution:
   ```bash
   ping github.com
   ```

3. Try with explicit DNS:
   ```bash
   echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf
   ```

### Python dependencies fail to install

**Symptom**: pip install errors during installation

**Solution**:
```bash
# Update pip
sudo pip3 install --upgrade pip

# Manually install dependencies
sudo pip3 install aiohttp aiofiles

# Restart installation
sudo bash install.sh
```

---

## Dashboard Not Loading

### Blank page or 404 error

**Symptom**: Browser shows blank page or "Not Found"

**Solutions**:

1. **Check if service is running**:
   ```bash
   sudo systemctl status pikvm-dashboard
   ```

2. **Start the service if stopped**:
   ```bash
   sudo systemctl start pikvm-dashboard
   ```

3. **Check nginx configuration**:
   ```bash
   sudo nginx -t
   sudo systemctl restart nginx
   ```

4. **Verify files exist**:
   ```bash
   ls -la /opt/pikvm-dashboard/
   ```

### "502 Bad Gateway" error

**Symptom**: Nginx returns 502 error

**Solution**:
```bash
# Check if backend is running
sudo systemctl status pikvm-dashboard

# Check backend logs
sudo journalctl -u pikvm-dashboard -n 50

# Restart the service
sudo systemctl restart pikvm-dashboard
```

### Dashboard loads but shows errors

**Symptom**: Dashboard appears but shows JavaScript errors

**Solution**:
1. Open browser Developer Tools (F12)
2. Check Console tab for errors
3. Try hard refresh: `Ctrl + Shift + R`
4. Clear browser cache and cookies for this site

---

## Connection & Authentication

### "Configuration not loaded" error

**Symptom**: Dashboard shows configuration error

**Solutions**:

1. **Re-enter credentials**:
   - Enable Advanced Features in hamburger menu
   - Expand "Change Login Credentials"
   - Enter your PiKVM username and password
   - Click "Update Credentials"

2. **Check PiKVM is accessible**:
   ```bash
   curl -k https://localhost/api/info
   ```

3. **Verify credentials work**:
   - Try logging into main PiKVM interface
   - Ensure username/password are correct

### "401 Unauthorized" errors

**Symptom**: API calls fail with authentication errors

**Solution**:
1. Clear credentials and re-enter:
   - Go to Maintenance section
   - Click "Clear Credentials"
   - Re-enter correct username/password

2. Check if PiKVM password was changed:
   - Log into PiKVM directly
   - Verify your password still works

### Can't connect to PiKVM API

**Symptom**: Status always shows "Checking..."

**Solutions**:

1. **Check PiKVM service**:
   ```bash
   sudo systemctl status kvmd
   ```

2. **Restart PiKVM services**:
   ```bash
   sudo systemctl restart kvmd
   sudo systemctl restart kvmd-nginx
   ```

3. **Check API directly**:
   ```bash
   curl -k -u admin:yourpassword https://localhost/api/info
   ```

---

## Power Controls Not Working

### Power buttons don't respond

**Symptom**: Clicking power buttons does nothing

**Solutions**:

1. **Check ATX connection**:
   - Verify ATX cables are properly connected
   - Check ATX board LEDs

2. **Test ATX directly**:
   ```bash
   # In PiKVM terminal
   kvmd-atx click power
   ```

3. **Check GPIO permissions**:
   ```bash
   sudo systemctl status kvmd
   ```

### Wrong PC responds to commands

**Symptom**: Different PC powers on/off than expected

**Solution**:
1. Go to Settings → Step 2 (PCs)
2. Verify port numbers match physical connections
3. Port 0 = first ATX port, Port 1 = second, etc.

### Force off doesn't work

**Symptom**: PC doesn't respond to force power off

**Solutions**:
1. Verify physical ATX connections
2. Try holding physical power button on PC
3. Check if PC power supply switch is on

---

## Scheduled Actions Issues

### Schedules don't execute

**Symptom**: Scheduled actions are missed

**Solutions**:

1. **Check backend service**:
   ```bash
   sudo systemctl status pikvm-dashboard
   sudo journalctl -u pikvm-dashboard -f
   ```

2. **Verify timezone**:
   ```bash
   timedatectl
   ```
   
   Set correct timezone:
   ```bash
   sudo timedatectl set-timezone America/New_York
   ```

3. **Check schedule data**:
   ```bash
   cat /var/lib/pikvm-dashboard/schedules.json
   ```

### Recurring schedules skip days

**Symptom**: Weekly schedules don't run on some days

**Solution**:
1. Edit the schedule
2. Verify correct days are selected
3. Re-save the schedule

### Timezone issues

**Symptom**: Actions execute at wrong times

**Solution**:
```bash
# Check current timezone
timedatectl

# List available timezones
timedatectl list-timezones | grep America

# Set your timezone
sudo timedatectl set-timezone America/New_York

# Restart service
sudo systemctl restart pikvm-dashboard
```

---

## Theme & Display Issues

### Text not visible in light mode

**Symptom**: Some text is hard to read

**Solutions**:
1. Try a different preset theme
2. Customize text color in Settings → Appearance
3. Report the issue with a screenshot

### Theme doesn't save

**Symptom**: Theme resets after refresh

**Solution**:
1. Check browser allows localStorage
2. Try a different browser
3. Clear cache and reconfigure

### Wizard text affected by theme

**Symptom**: Settings wizard text changes with theme

**Solution**: This was fixed in recent versions. Update to latest:
```bash
curl -sSL https://raw.githubusercontent.com/DanCue44/pikvm-dashboard/main/install.sh | sudo bash
```

### Custom icons not displaying

**Symptom**: Uploaded icons don't appear

**Solutions**:
1. Verify icon was uploaded successfully
2. Check supported formats: PNG, JPG, GIF, SVG
3. Try re-uploading the icon
4. Check file size (keep under 1MB)

---

## Performance Issues

### Dashboard is slow

**Symptom**: Interface is laggy or unresponsive

**Solutions**:

1. **Check PiKVM resources**:
   ```bash
   top
   free -h
   ```

2. **Restart services**:
   ```bash
   sudo systemctl restart pikvm-dashboard
   sudo systemctl restart kvmd
   ```

3. **Check for many schedules**:
   - Delete old/unnecessary schedules
   - Reduce polling frequency

### High CPU usage

**Symptom**: PiKVM running hot or slow

**Solution**:
```bash
# Check what's using CPU
top

# Restart dashboard service
sudo systemctl restart pikvm-dashboard

# Check for runaway processes
ps aux | grep python
```

### Memory issues

**Symptom**: Out of memory errors

**Solution**:
```bash
# Check memory
free -h

# Restart services to free memory
sudo systemctl restart pikvm-dashboard
sudo systemctl restart kvmd

# Reboot if necessary
sudo reboot
```

---

## Service & Backend Issues

### Service won't start

**Symptom**: pikvm-dashboard service fails to start

**Solution**:
```bash
# Check status and errors
sudo systemctl status pikvm-dashboard
sudo journalctl -u pikvm-dashboard -n 100

# Check for Python errors
sudo /var/lib/pikvm-dashboard/venv/bin/python /opt/pikvm-dashboard/pikvm_dashboard_service.py
```

### Service keeps restarting

**Symptom**: Service starts then stops repeatedly

**Solution**:
```bash
# Check logs for crash reason
sudo journalctl -u pikvm-dashboard -f

# Common fixes:
# 1. Check Python syntax errors
# 2. Verify all files exist
# 3. Check permissions
sudo chown -R root:root /opt/pikvm-dashboard
```

### API endpoints return errors

**Symptom**: Dashboard shows API errors

**Solution**:
```bash
# Test API directly
curl http://localhost:8080/api/health

# Check backend logs
sudo journalctl -u pikvm-dashboard -f
```

---

## Browser-Specific Issues

### Chrome: Notifications not working

**Solution**:
1. Click lock icon in address bar
2. Set Notifications to "Allow"
3. Reload the page

### Firefox: Storage issues

**Solution**:
1. Go to Settings → Privacy
2. Ensure "Delete cookies when Firefox closes" is off for this site
3. Or add an exception for the dashboard URL

### Safari: Features not working

**Solution**:
1. Safari has limited notification support
2. Try Chrome or Firefox for full functionality
3. Check Safari → Preferences → Websites

### Mobile browsers: Layout issues

**Solution**:
1. Ensure you're using landscape mode for complex sections
2. Try "Desktop site" option if available
3. Use a tablet or desktop for configuration

---

## Getting Debug Information

When reporting issues, include:

### 1. Browser Console Logs
```
1. Open Developer Tools (F12)
2. Go to Console tab
3. Copy any red error messages
```

### 2. Service Logs
```bash
sudo journalctl -u pikvm-dashboard -n 100 --no-pager
```

### 3. System Information
```bash
# PiKVM version
cat /etc/kvmd/version

# OS info
uname -a

# Service status
sudo systemctl status pikvm-dashboard
```

### 4. Configuration Files
```bash
# Dashboard config (remove sensitive data before sharing)
cat /var/lib/pikvm-dashboard/config.json

# Check file permissions
ls -la /opt/pikvm-dashboard/
ls -la /var/lib/pikvm-dashboard/
```

---

## Still Need Help?

If your issue isn't covered here:

1. **Search existing issues**: [GitHub Issues](https://github.com/DanCue44/pikvm-dashboard/issues)
2. **Create a new issue** with:
   - Description of the problem
   - Steps to reproduce
   - Debug information from above
   - Screenshots if applicable

---

*Last updated: February 2026*
