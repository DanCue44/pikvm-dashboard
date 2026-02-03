# PiKVM Dashboard User Guide

A complete guide to using and configuring your PiKVM Dashboard.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Dashboard Overview](#dashboard-overview)
3. [PC Cards](#pc-cards)
4. [Keyboard Shortcuts](#keyboard-shortcuts)
5. [Scheduled Actions](#scheduled-actions)
6. [Follow-up Actions](#follow-up-actions)
7. [Idle Shutdown](#idle-shutdown)
8. [Action Log](#action-log)
9. [Themes & Appearance](#themes--appearance)
10. [Settings & Configuration](#settings--configuration)
11. [Hamburger Menu](#hamburger-menu)
12. [Maintenance](#maintenance)

---

## Getting Started

### First Launch

> **Important**: Log in to the main PiKVM web interface at `https://<your-pikvm-ip>/` first before navigating to the dashboard. PiKVM's authentication currently redirects to its default page after login rather than back to your original URL ([pikvm/pikvm#1631](https://github.com/pikvm/pikvm/issues/1631)), so logging in first ensures you're already authenticated.
>
> If you visit the dashboard without logging in first, you'll see a mostly blank page — the site title and menu button will appear, but the PiKVM logo will be missing and the setup wizard won't launch. If this happens, click the broken logo image in the header to go to the main PiKVM interface, log in, then navigate back to the dashboard. PiKVM sessions stay active for long periods of time, so this is typically only an issue on first use or after clearing your browser data.

When you first access the dashboard at `https://<your-pikvm-ip>/pikvm-dashboard.html`, the Setup Wizard will automatically launch to guide you through the initial configuration.

> **Note**: PiKVM uses HTTPS with a self-signed certificate by default. Your browser may show a security warning - this is normal. Click "Advanced" and proceed to the site.

### Setup Wizard Steps

#### Step 1: Hardware Configuration

- **ATX Switch**: Select whether you have a PiKVM ATX switch installed
  - **Yes**: You have hardware control over multiple PCs
  - **No**: You're using a single PC setup or software-only control
- **PC Count**: If you have an ATX switch, specify how many PCs you want to control (1-20)

#### Step 2: PC Configuration

For each PC, configure:
- **PC Name**: A friendly name (e.g., "Gaming PC", "Work Station")
- **Port Number**: The ATX switch port this PC is connected to (0-19)
- **Custom Icon**: Optionally upload a custom icon for this PC

#### Step 3: Appearance

- **Theme Preset**: Choose from 7 built-in themes
- **Light/Dark Mode**: Set your preferred mode
- **Custom Colors**: Fine-tune individual colors if desired
- **Logo**: Upload a custom logo
- **Dashboard Title**: Change the header title
- **Background Image**: Set a custom background

#### Step 4: Features

Enable or disable optional features:
- ⌨️ Keyboard Shortcuts
- 📅 Scheduled Actions
- 💤 Idle Shutdown
- 📋 Action Log
- ⏱️ Uptime Tracking
- 🔊 Sound Notifications
- 💾 HDD Activity Indicator

#### Step 5: Review & Save

Review your settings and click **Complete Setup** to save.

---

## Dashboard Overview

The main dashboard displays:

- **Header**: Logo, title, and hamburger menu
- **PC Cards**: Status and controls for each configured PC
- **Keyboard Shortcuts**: Quick access to common key combinations
- **Scheduled Actions**: Upcoming and recurring schedules
- **Idle Shutdown**: Automatic shutdown configuration
- **Action Log**: History of performed actions

---

## PC Cards

Each PC card displays:

### Status Indicators

| Indicator | Meaning |
|-----------|---------|
| 🟢 Green | PC is Online |
| 🔴 Red | PC is Offline |
| 🟡 Yellow | Checking status... |

### Information Displayed

- **PC Name**: Your configured name
- **Status**: Online/Offline
- **Uptime**: How long the PC has been running (if online)
- **HDD Activity**: Disk activity indicator (if enabled)

### Power Controls

| Button | Action | Description |
|--------|--------|-------------|
| **Power On** | Short press | Turns on an offline PC |
| **Power Off** | Short press | Graceful shutdown (like pressing power button) |
| **Reset** | Press | Hard reset the PC |
| **Force Off** | Long press | Force power off (hold power button) |

### Using Power Controls

1. Locate the PC card you want to control
2. Click the appropriate power button
3. A confirmation may appear for destructive actions
4. The status will update after the action completes

---

## Keyboard Shortcuts

Send keyboard combinations to your PCs without needing to open the KVM interface.

### Available Shortcuts

| Shortcut | Key Combination | Common Use |
|----------|-----------------|------------|
| Ctrl+Alt+Del | `Ctrl + Alt + Delete` | Open security options, Task Manager |
| Ctrl+Alt+Esc | `Ctrl + Alt + Escape` | Open Task Manager directly |
| Alt+F4 | `Alt + F4` | Close active window |
| Win | `Windows Key` | Open Start menu |
| Win+R | `Windows + R` | Open Run dialog |
| Win+L | `Windows + L` | Lock the computer |

### Using Keyboard Shortcuts

1. **Select the target PC** from the dropdown at the top of the Keyboard Shortcuts section
2. **Click the shortcut button** you want to send
3. The keystroke is immediately sent to the selected PC

---

## Scheduled Actions

Automate power actions at specific times.

### Creating a Schedule

1. In the **Scheduled Actions** section, fill out the form:
   - **PC**: Select which PC this schedule is for
   - **Action Type**: Power or Keyboard
   - **Action**: Specific action (On/Off/Reset or keystroke)
   - **Date & Time**: When to execute
   - **Condition**: When to actually perform the action

2. Click **Add Schedule**

### Schedule Conditions

| Condition | Behavior |
|-----------|----------|
| **Always** | Execute regardless of PC state |
| **Smart** | Only execute if the action would change the state |
| **Only if ON** | Only execute if PC is currently online |
| **Only if OFF** | Only execute if PC is currently offline |

**Example**: Schedule "Power Off" with "Only if ON" - the action will be skipped if the PC is already off.

### Recurring Schedules

1. Check **🔄 Recurring** when creating a schedule
2. Choose frequency:
   - **Daily**: Runs every day at the specified time
   - **Weekly**: Runs on selected days of the week

3. For weekly, select which days (Mon-Sun)

### Managing Schedules

#### List View
- See all schedules in a list format
- Shows time, PC, action, and countdown
- Checkboxes for bulk selection

#### Calendar View
- Visual monthly calendar
- Days with schedules are highlighted
- Click a day to see that day's schedules

#### Bulk Actions
1. Check multiple schedules
2. Use the bulk action bar to:
   - **Select All**: Check all schedules
   - **Clear Selection**: Uncheck all
   - **Delete Selected**: Remove all checked schedules

#### Removing a Schedule
- Click **Remove** on any individual schedule
- Or use bulk delete for multiple schedules

---

## Follow-up Actions

Chain multiple actions together with delays.

### What Are Follow-up Actions?

Follow-up actions execute automatically after the primary scheduled action, with a configurable delay.

**Example Use Case**: 
1. Primary: Power On PC at 8:00 AM
2. Follow-up 1: Send Win+R after 2 minutes (to open Run dialog)
3. Follow-up 2: Power Off after 1 hour

### Adding a Follow-up

1. Find an existing schedule in the list
2. Click **➕ Add Follow-up**
3. Configure:
   - **Delay**: How long to wait (seconds/minutes/hours/days)
   - **Action Type**: Power or Keyboard
   - **Action**: Specific action to perform
4. Click **Add Follow-up**

### Managing Follow-ups

- **Reorder**: Drag and drop follow-ups to change execution order
- **Remove**: Click the ✕ button on any follow-up

---

## Idle Shutdown

Automatically shut down PCs that have been idle for too long.

### How It Works

1. The dashboard monitors PC activity
2. If no activity is detected for the configured duration, a warning appears
3. If still no activity, the PC is automatically shut down

### Configuration

1. Find the **Idle Shutdown** section
2. For each PC:
   - Toggle the switch to enable/disable
   - Set the idle timeout in minutes (5-1440)

### Idle Detection

The system monitors:
- HDD/SSD activity
- User input activity
- System wake events

---

## Action Log

Track all actions performed through the dashboard.

### Log Information

Each entry shows:
- **Timestamp**: When the action occurred
- **PC**: Which PC was affected
- **Action**: What was done
- **Result**: Success or failure

### Managing the Log

- Logs are displayed in chronological order (newest first)
- Click **Clear Log** to remove all entries
- Logs persist across browser sessions

---

## Themes & Appearance

Customize the look and feel of your dashboard.

### Changing Themes

#### Quick Toggle (Light/Dark)
1. Open the hamburger menu (☰)
2. Toggle **Light Mode** on or off

#### Full Theme Customization
1. Open hamburger menu → **Settings**
2. Go to **Step 3: Appearance**
3. Choose a preset theme or customize colors

### Available Preset Themes

| Theme | Description |
|-------|-------------|
| 🎨 Default | Clean gray/blue tones |
| 🌊 Ocean | Cool blue palette |
| 🌅 Sunset | Warm pink/orange tones |
| 🌲 Forest | Natural green palette |
| 🔥 Fire | Bold red/orange tones |
| 💜 Purple | Rich purple palette |
| 🌙 Midnight | Deep blue-gray tones |

### Custom Colors

In Settings → Appearance, you can customize:
- Card Title color
- Card Background
- Input/Status Background
- Button Background
- Site Background
- Text Color

Each color can be set independently for Light and Dark modes.

### Additional Customization

- **Logo**: Upload a custom logo image
- **Dashboard Title**: Change the header text
- **Background Image**: Set a custom background image URL

---

## Settings & Configuration

Access all settings through the hamburger menu → **Settings**.

### Settings Wizard Navigation

- Click step numbers at the top to jump to any step
- Use **Back** and **Next** buttons to navigate sequentially
- Changes are saved when you complete the wizard

### What You Can Configure

1. **Hardware**: ATX switch setup, PC count
2. **PCs**: Names, ports, custom icons
3. **Appearance**: Themes, colors, branding
4. **Features**: Enable/disable dashboard features

---

## Hamburger Menu

Access the hamburger menu by clicking ☰ in the top-right corner.

### Menu Options

| Option | Description |
|--------|-------------|
| **Light Mode** | Toggle between light and dark themes |
| **Sound** | Enable/disable notification sounds |
| **Notifications** | Enable/disable browser notifications |
| **Advanced Features** | Show/hide maintenance section |
| **Settings** | Open the settings wizard |
| **KVM** | Open the main PiKVM interface |
| **Terminal** | Open PiKVM terminal |
| **VNC** | Open VNC interface |
| **About** | View project info, GitHub, Patreon |
| **Logout** | Log out of PiKVM |

---

## Maintenance

Access maintenance features by enabling **Advanced Features** in the hamburger menu.

### Credentials

Your login credentials were saved during installation. To change them:

1. Enable **Advanced Features** in the hamburger menu
2. Scroll to the **Maintenance** section
3. Expand **Change Login Credentials**
4. Enter new credentials
5. Click **Update Credentials**

### Clean Up Icons

Remove unused uploaded icons from the server:

1. Go to Maintenance section
2. Click **Clean Up Unused Icons**
3. Confirm the action

This removes icon files that are no longer assigned to any PC.

---

## Tips & Best Practices

### Scheduling

- Use **Smart** condition to avoid unnecessary actions
- Add follow-up actions for complex workflows
- Use weekly recurring for work/home schedules

### Performance

- Disable features you don't use to reduce clutter
- Clear old action logs periodically
- Use appropriate idle timeout values (not too short)

### Security

- Change default PiKVM credentials
- Use HTTPS if accessing remotely
- Regularly update PiKVM software

---

## Need Help?

- **Troubleshooting Guide**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **FAQ**: [FAQ.md](FAQ.md)
- **GitHub Issues**: [Report a bug](https://github.com/DanCue44/pikvm-dashboard/issues)

---

*Happy computing! 🖥️*
