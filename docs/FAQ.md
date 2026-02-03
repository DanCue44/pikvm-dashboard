# PiKVM Dashboard - Frequently Asked Questions

Common questions about the PiKVM Dashboard.

---

## General Questions

### What is PiKVM Dashboard?

PiKVM Dashboard is a custom web interface that extends PiKVM functionality, allowing you to manage multiple PCs from a single, user-friendly interface. It adds features like scheduled power actions, idle shutdown, custom themes, and keyboard shortcuts.

### Is this an official PiKVM project?

No, this is an independent community project that works alongside PiKVM. It uses PiKVM's API to provide additional functionality.

### Does this replace the standard PiKVM interface?

No, the dashboard runs alongside the standard PiKVM interface. You can still access the original interface at `https://<your-pikvm-ip>/` while the dashboard is available at `https://<your-pikvm-ip>/pikvm-dashboard.html`.

### What PiKVM versions are supported?

The dashboard supports:
- PiKVM v2
- PiKVM v3
- PiKVM v4
- DIY PiKVM builds

### Is the dashboard free?

Yes, the dashboard is completely free and open source. If you find it useful, you can support development through [Patreon](https://www.patreon.com/c/DanCue44).

---

## Installation

### How do I install the dashboard?

SSH into your PiKVM and run:
```bash
curl -sSL https://raw.githubusercontent.com/DanCue44/pikvm-dashboard/main/install.sh | sudo bash
```

For first-time installs, the script will prompt you for your PiKVM credentials. For updates, it will use your saved credentials automatically.

### Do I need to be in read-write mode?

No, the installer handles this automatically. It will switch to read-write mode during installation.

### Can I install without internet access?

Yes, but you'll need to manually download the files and transfer them to your PiKVM. See the manual installation section in the README.

### How do I update to the latest version?

Run the same install command - it will detect the existing installation and update files while keeping your data:
```bash
curl -sSL https://raw.githubusercontent.com/DanCue44/pikvm-dashboard/main/install.sh | sudo bash
```

### How do I uninstall?

```bash
sudo systemctl stop pikvm-dashboard
sudo systemctl disable pikvm-dashboard
sudo rm -rf /opt/pikvm-dashboard
sudo rm -rf /var/lib/pikvm-dashboard
sudo rm /etc/systemd/system/pikvm-dashboard.service
sudo systemctl daemon-reload
```

---

## Features

### Can I control multiple PCs?

Yes! With a PiKVM ATX switch, you can control multiple PCs. The dashboard supports up to 20 PCs. Configure the number of PCs in Settings → Hardware.

### What power actions are available?

- **Power On**: Turn on a powered-off PC
- **Power Off**: Graceful shutdown (short power button press)
- **Reset**: Hard reset the PC
- **Force Off**: Force power off (long power button press)

### What keyboard shortcuts can I send?

Built-in shortcuts include:
- Ctrl+Alt+Del
- Ctrl+Alt+Esc
- Alt+F4
- Windows key
- Win+R
- Win+L

### Can I schedule actions?

Yes! You can schedule:
- One-time actions at a specific date/time
- Daily recurring actions
- Weekly recurring actions on specific days

### What are conditional actions?

Conditions let you control when scheduled actions actually execute:
- **Always**: Execute regardless of PC state
- **Smart**: Only execute if it would change the state
- **Only if ON**: Only execute if PC is currently on
- **Only if OFF**: Only execute if PC is currently off

### What are follow-up actions?

Follow-up actions let you chain multiple actions with delays. For example: Power On → wait 5 minutes → Send Win+R.

### Does idle shutdown work when PC is locked?

Idle detection monitors system activity, not just user input. A locked but active PC (running updates, downloads, etc.) won't be considered idle.

---

## Connectivity

### Can I access the dashboard remotely?

Yes, if your PiKVM is accessible remotely, the dashboard will be too. Consider using:
- VPN (recommended for security)
- PiKVM's built-in Tailscale support
- Port forwarding (not recommended without additional security)

### Does the dashboard work over HTTPS?

Yes, it uses whatever protocol your PiKVM is configured for. If you access PiKVM via HTTPS, the dashboard will also use HTTPS.

### Can multiple users access the dashboard simultaneously?

Yes, the dashboard can handle multiple simultaneous users. Settings are stored per-browser, so each user can have their own preferences.

---

## Themes & Customization

### How do I change the theme?

**Quick toggle**: Use the Light Mode switch in the hamburger menu.

**Full customization**: Go to Settings → Appearance to choose presets or customize colors.

### Can I upload a custom logo?

Yes! In Settings → Appearance, you can provide a URL for a custom logo image.

### Can I use custom PC icons?

Yes! In Settings → PCs, you can upload a custom icon for each PC. Supported formats: PNG, JPG, GIF, SVG.

### My custom theme looks wrong after updating

Theme settings are stored in your browser. Try:
1. Clearing browser cache
2. Re-selecting your theme
3. Saving settings again

---

## Troubleshooting

### Why does my PC show "Checking..." status?

This usually means:
1. The dashboard is still connecting to PiKVM
2. There's an authentication issue
3. PiKVM API is not responding

Check your credentials in the Maintenance section.

### Why don't my scheduled actions run?

Common causes:
1. **Timezone mismatch**: Check `timedatectl` on your PiKVM
2. **Service not running**: Check `sudo systemctl status pikvm-dashboard`
3. **Condition not met**: If using "Only if ON/OFF", the PC may be in the wrong state

### Why can't I send keyboard shortcuts?

Ensure:
1. The correct PC is selected in the dropdown
2. The PC is powered on and connected
3. You have KVM access (not just ATX control)

### The dashboard is slow

Try:
1. Reducing the number of enabled features
2. Clearing old action logs
3. Restarting the service: `sudo systemctl restart pikvm-dashboard`

---

## Technical Questions

### What ports does the dashboard use?

- **8080**: Backend API service (internal)
- **80/443**: Served through nginx (same as PiKVM)

### Where is data stored?

- **Configuration**: `/var/lib/pikvm-dashboard/config.json`
- **Schedules**: `/var/lib/pikvm-dashboard/schedules.json`
- **Uploaded icons**: `/var/lib/pikvm-dashboard/icons/`
- **Browser settings**: localStorage in your browser

### What programming languages are used?

- **Frontend**: HTML, CSS, JavaScript (vanilla)
- **Backend**: Python 3 with aiohttp
- **Service**: systemd

### Can I modify the dashboard?

Yes! The dashboard is open source. The main file is `/opt/pikvm-dashboard/pikvm-dashboard.html`. Note that updates may overwrite your changes.

### How does the dashboard communicate with PiKVM?

The dashboard backend uses PiKVM's REST API to:
- Check PC power status via GPIO
- Send power commands via ATX
- Send keyboard input via HID

---

## Security

### Is my password stored securely?

Credentials are stored in your browser's localStorage and in the backend config. For maximum security:
1. Use unique credentials for PiKVM
2. Access via VPN or Tailscale
3. Keep PiKVM software updated

### Can I use this without authentication?

The dashboard requires PiKVM authentication. This cannot be bypassed as it's needed for API access.

### Why does logging in redirect me to the main PiKVM page instead of the dashboard?

This is a known limitation of PiKVM's authentication system — it always redirects to `/` after login rather than back to the page you were trying to access. A feature request has been submitted upstream ([pikvm/pikvm#1631](https://github.com/pikvm/pikvm/issues/1631)). For now, log in to the main PiKVM interface first at `https://<your-pikvm-ip>/`, then navigate to `/pikvm-dashboard.html`. PiKVM sessions stay active for long periods of time, so this is typically only an issue on first use or after clearing your browser data.

### I just installed the dashboard but it looks blank — no setup wizard, missing logo. What's wrong?

You're not logged into PiKVM yet. The dashboard needs an authenticated session to load its configuration and display the setup wizard. Without it, API calls fail silently and the page renders in an empty state. Click the broken logo image in the header (it links to the main PiKVM interface), log in there, then navigate back to the dashboard. PiKVM sessions stay active for long periods of time, so this typically only happens on first use or after clearing your browser data.

### Is the connection encrypted?

Yes, PiKVM uses HTTPS by default, so all dashboard communication is encrypted. PiKVM uses a self-signed certificate, which may trigger a browser warning on first visit - this is normal and safe to accept.

---

## Compatibility

### Does this work on Raspberry Pi 5?

Compatibility depends on PiKVM support for your hardware. If PiKVM works on your Pi 5 setup, the dashboard should work too.

### Does this work with PiKVM without ATX?

Partially. You can use:
- KVM features (if available)
- Keyboard shortcuts
- Some monitoring features

Power control requires ATX hardware.

### Can I use this with other KVM solutions?

No, the dashboard is specifically designed for PiKVM and uses its API. It won't work with other KVM solutions.

### Does this work with BliKVM?

BliKVM uses similar APIs to PiKVM, so it may work with some modifications. This is not officially tested or supported.

---

## Contributing

### How can I contribute?

- **Report bugs**: Open an issue on GitHub
- **Suggest features**: Open an issue with the "enhancement" label
- **Submit code**: Fork the repo and submit a pull request
- **Support development**: [Patreon](https://www.patreon.com/c/DanCue44)

### I found a bug, how do I report it?

1. Check if it's already reported in [GitHub Issues](https://github.com/DanCue44/pikvm-dashboard/issues)
2. If not, create a new issue with:
   - Description of the problem
   - Steps to reproduce
   - Browser and device info
   - Screenshots if applicable

### Can I request a feature?

Yes! Open an issue on GitHub with the "enhancement" label. Describe:
- What you'd like to see
- Why it would be useful
- Any implementation ideas you have

---

## More Questions?

If your question isn't answered here:

1. Check the [User Guide](USER_GUIDE.md)
2. Check the [Troubleshooting Guide](TROUBLESHOOTING.md)
3. Search [GitHub Issues](https://github.com/DanCue44/pikvm-dashboard/issues)
4. Open a new issue if needed

---

*Last updated: February 2026*
