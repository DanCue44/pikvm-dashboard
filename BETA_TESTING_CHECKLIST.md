# PiKVM Dashboard - Beta Testing Checklist

## 📦 Installation

### Prerequisites
- PiKVM device with network access
- SSH access to your PiKVM
- PiKVM login credentials (default: admin/admin)

### Install via Command Line

SSH into your PiKVM and run:

```bash
curl -sSL https://raw.githubusercontent.com/DanCue44/pikvm-dashboard/main/install.sh | sudo bash
```

The installer will prompt you for credentials on first install, or use saved credentials for updates.

### Access the Dashboard

After installation, access the dashboard at:
```
https://<your-pikvm-ip>/pikvm-dashboard.html
```

> **Note**: PiKVM uses HTTPS with a self-signed certificate. Your browser may show a security warning - click "Advanced" and proceed to accept the certificate.

---

## 🧪 Testing Checklist

Please test each feature and note any issues. Mark each item as:
- ✅ **Pass** - Works as expected
- ⚠️ **Partial** - Works with issues (describe in notes)
- ❌ **Fail** - Does not work (describe in notes)

---

### 1. Installation & Setup

| Test | Steps | Expected Result | Status | Notes |
|------|-------|-----------------|--------|-------|
| 1.1 Fresh Install | Run install script on fresh PiKVM | Script completes without errors | | |
| 1.2 Setup Wizard Launch | Access dashboard for first time | Setup wizard appears automatically | | |
| 1.3 Hardware Config | Select ATX switch yes/no, set PC count | Options save and proceed to next step | | |
| 1.4 PC Configuration | Name PCs, set ports, upload custom icons | All settings save correctly | | |
| 1.5 Appearance Settings | Select theme, customize colors | Preview updates in real-time | | |
| 1.6 Feature Toggles | Enable/disable optional features | Features show/hide on dashboard | | |
| 1.7 Wizard Completion | Complete all steps and save | Dashboard loads with all settings applied | | |

---

### 2. Theme System

| Test | Steps | Expected Result | Status | Notes |
|------|-------|-----------------|--------|-------|
| 2.1 Light/Dark Toggle | Toggle theme in hamburger menu | All elements switch colors appropriately | | |
| 2.2 Preset Themes | Try each preset (Ocean, Sunset, Forest, Fire, Purple, Midnight) | Colors apply consistently across all elements | | |
| 2.3 Custom Colors | Modify individual color pickers | Changes apply and persist after refresh | | |
| 2.4 Header Text | Check site title visibility in light mode | Text is clearly readable | | |
| 2.5 Hamburger Menu Colors | Open menu in light/dark modes | Menu background and text match theme | | |
| 2.6 Input/Status Boxes | Check status indicators in light themes | Background color provides sufficient contrast | | |
| 2.7 Schedule List Text | View scheduled actions in light mode | All text is readable | | |
| 2.8 Wizard Text | Open Settings wizard in light mode | All wizard text remains readable (not affected by theme) | | |

---

### 3. PC Cards & Status

| Test | Steps | Expected Result | Status | Notes |
|------|-------|-----------------|--------|-------|
| 3.1 Status Display | View PC cards | Shows Online/Offline/Checking status correctly | | |
| 3.2 Status Dot Colors | Observe status indicators | Green=Online, Red=Offline, Yellow=Checking | | |
| 3.3 Custom Icons | Upload custom PC icon in settings | Icon displays on PC card | | |
| 3.4 Power On | Click Power On for offline PC | PC powers on, status updates | | |
| 3.5 Power Off | Click Power Off for online PC | PC powers off, status updates | | |
| 3.6 Reset | Click Reset for online PC | PC resets | | |
| 3.7 Force Off | Long-press power off | PC force shuts down | | |
| 3.8 Uptime Display | Check online PC | Shows uptime duration | | |

---

### 4. Keyboard Shortcuts

| Test | Steps | Expected Result | Status | Notes |
|------|-------|-----------------|--------|-------|
| 4.1 Ctrl+Alt+Del | Click shortcut button | Keystroke sent to selected PC | | |
| 4.2 Win Key | Click shortcut button | Windows key sent | | |
| 4.3 Win+R | Click shortcut button | Run dialog opens on target PC | | |
| 4.4 Win+L | Click shortcut button | PC locks | | |
| 4.5 Alt+F4 | Click shortcut button | Active window closes | | |
| 4.6 PC Selection | Change PC selector | Shortcuts target correct PC | | |

---

### 5. Scheduled Actions

| Test | Steps | Expected Result | Status | Notes |
|------|-------|-----------------|--------|-------|
| 5.1 Add Schedule | Create new scheduled action | Schedule appears in list | | |
| 5.2 One-time Schedule | Schedule action for specific date/time | Executes at scheduled time | | |
| 5.3 Recurring Daily | Set daily recurring schedule | Executes every day | | |
| 5.4 Recurring Weekly | Set weekly schedule with specific days | Executes on selected days only | | |
| 5.5 List View | Click List button | Shows list of all schedules | | |
| 5.6 Calendar View | Click Calendar button | Shows calendar with scheduled days highlighted | | |
| 5.7 List/Calendar Toggle | Switch between views | Both buttons same width, text visible in light mode | | |
| 5.8 Remove Schedule | Click Remove on a schedule | Schedule deleted | | |
| 5.9 Bulk Select | Check multiple schedules | Bulk action bar appears | | |
| 5.10 Bulk Delete | Select multiple and delete | All selected schedules removed | | |

---

### 6. Conditional Actions

| Test | Steps | Expected Result | Status | Notes |
|------|-------|-----------------|--------|-------|
| 6.1 Smart Condition | Schedule with "Smart" condition | Only executes if state change needed | | |
| 6.2 Only if ON | Schedule power off "Only if ON" | Skips if PC already off | | |
| 6.3 Only if OFF | Schedule power on "Only if OFF" | Skips if PC already on | | |
| 6.4 Always | Schedule with "Always" condition | Executes regardless of state | | |

---

### 7. Follow-up Actions

| Test | Steps | Expected Result | Status | Notes |
|------|-------|-----------------|--------|-------|
| 7.1 Add Follow-up | Click "Add Follow-up" on schedule | Modal opens | | |
| 7.2 Power Follow-up | Add power action follow-up | Executes after delay | | |
| 7.3 Keyboard Follow-up | Add keyboard shortcut follow-up | Keystroke sent after delay | | |
| 7.4 Multiple Follow-ups | Add 2+ follow-ups to one schedule | All execute in sequence | | |
| 7.5 Drag Reorder | Drag follow-ups to reorder | Order changes and saves | | |
| 7.6 Remove Follow-up | Click X on follow-up | Follow-up removed | | |

---

### 8. Idle Shutdown

| Test | Steps | Expected Result | Status | Notes |
|------|-------|-----------------|--------|-------|
| 8.1 Enable Idle Shutdown | Toggle on for a PC | Idle monitoring starts | | |
| 8.2 Idle Detection | Leave PC idle past threshold | Warning appears then shutdown | | |
| 8.3 Activity Reset | Use PC during idle countdown | Timer resets | | |
| 8.4 Custom Duration | Set custom idle minutes | Uses specified duration | | |
| 8.5 Disable | Toggle off | Idle monitoring stops | | |

---

### 9. Action Log

| Test | Steps | Expected Result | Status | Notes |
|------|-------|-----------------|--------|-------|
| 9.1 Log Display | Perform actions | Actions appear in log | | |
| 9.2 Timestamps | Check log entries | Correct times displayed | | |
| 9.3 Action Types | Various actions | All types logged correctly | | |
| 9.4 Clear Log | Clear action log | Log empties | | |

---

### 10. Hamburger Menu

| Test | Steps | Expected Result | Status | Notes |
|------|-------|-----------------|--------|-------|
| 10.1 Open/Close | Click hamburger icon | Menu slides in/out | | |
| 10.2 Theme Toggle | Toggle light/dark | Theme switches, toggle turns orange when ON | | |
| 10.3 Sound Toggle | Toggle sound | Notification sounds enable/disable | | |
| 10.4 Notifications Toggle | Toggle notifications | Browser notifications enable/disable | | |
| 10.5 Advanced Toggle | Toggle advanced features | Maintenance section shows/hides | | |
| 10.6 Settings | Click Settings | Wizard opens | | |
| 10.7 KVM Link | Click KVM | Opens PiKVM main interface | | |
| 10.8 Terminal Link | Click Terminal | Opens PiKVM terminal | | |
| 10.9 VNC Link | Click VNC | Opens VNC interface | | |
| 10.10 About | Click About | About modal opens with GitHub/Patreon links | | |
| 10.11 Logout | Click Logout | Logs out of PiKVM | | |

---

### 11. Maintenance Section

| Test | Steps | Expected Result | Status | Notes |
|------|-------|-----------------|--------|-------|
| 11.1 Visibility | Enable Advanced Features toggle | Maintenance section appears | | |
| 11.2 Credentials Status | View section | Shows "Credentials Configured" message | | |
| 11.3 Expand Credentials | Click "Change Login Credentials" | Form expands | | |
| 11.4 Update Credentials | Change and save credentials | Toast confirms update | | |
| 11.5 Clear Credentials | Click Clear Credentials | Confirmation modal, then clears | | |
| 11.6 Clean Up Icons | Click "Clean Up Unused Icons" | Removes orphaned icon files | | |

---

### 12. About Modal

| Test | Steps | Expected Result | Status | Notes |
|------|-------|-----------------|--------|-------|
| 12.1 Open Modal | Click About in menu | Modal appears | | |
| 12.2 GitHub Link | Click "Follow Me on GitHub" | Opens GitHub profile in new tab | | |
| 12.3 Patreon Link | Click "Support on Patreon" | Opens Patreon page in new tab | | |
| 12.4 Close Modal | Click Close or outside modal | Modal closes | | |
| 12.5 Button Visibility | Check GitHub button | Button visible on dark background | | |

---

### 13. Notifications

| Test | Steps | Expected Result | Status | Notes |
|------|-------|-----------------|--------|-------|
| 13.1 Sound on Action | Perform power action with sound ON | Sound plays | | |
| 13.2 Sound Muted | Perform action with sound OFF | No sound | | |
| 13.3 Browser Notification | Enable notifications, trigger action | Browser notification appears | | |
| 13.4 Permission Request | First enable notifications | Browser asks permission | | |

---

### 14. Persistence & Refresh

| Test | Steps | Expected Result | Status | Notes |
|------|-------|-----------------|--------|-------|
| 14.1 Settings Persist | Configure settings, refresh page | All settings retained | | |
| 14.2 Theme Persist | Set theme, refresh | Theme retained | | |
| 14.3 Schedules Persist | Add schedules, refresh | Schedules still present | | |
| 14.4 Toggles Persist | Set menu toggles, refresh | Toggle states retained | | |

---

### 15. Responsive Design

| Test | Steps | Expected Result | Status | Notes |
|------|-------|-----------------|--------|-------|
| 15.1 Desktop | View on desktop browser | Layout displays correctly | | |
| 15.2 Tablet | View on tablet or resize window | Layout adapts | | |
| 15.3 Mobile | View on phone | Layout stacks vertically, still usable | | |
| 15.4 Wizard Mobile | Open settings on mobile | Wizard usable on small screen | | |

---

### 16. Edge Cases & Error Handling

| Test | Steps | Expected Result | Status | Notes |
|------|-------|-----------------|--------|-------|
| 16.1 Network Disconnect | Disconnect PiKVM network briefly | Graceful error, reconnects | | |
| 16.2 Invalid Credentials | Enter wrong password | Clear error message | | |
| 16.3 Rapid Actions | Click buttons rapidly | No crashes or duplicates | | |
| 16.4 Empty States | View with no schedules | "No scheduled actions" message visible | | |
| 16.5 Long PC Names | Use very long PC name | Truncates or wraps appropriately | | |

---

## 📝 Bug Report Template

If you encounter issues, please report them using this format:

```
**Bug Title:** [Brief description]

**Environment:**
- PiKVM Model: [v3/v4/DIY]
- Browser: [Chrome/Firefox/Safari/Edge + version]
- Device: [Desktop/Tablet/Mobile]

**Steps to Reproduce:**
1. 
2. 
3. 

**Expected Behavior:**
[What should happen]

**Actual Behavior:**
[What actually happens]

**Screenshots:**
[If applicable]

**Console Errors:**
[Press F12, go to Console tab, paste any red errors]
```

---

## 📬 Submitting Feedback

Please submit your completed checklist and any bug reports via:

1. **GitHub Issues:** https://github.com/DanCue44/pikvm-dashboard/issues
2. **Email:** [Your preferred contact method]

---

## 🙏 Thank You!

Thank you for helping test the PiKVM Dashboard! Your feedback is invaluable in making this tool better for everyone.

If you find this project useful, consider supporting its development:
- ⭐ Star the repo on GitHub
- 💖 Support on Patreon: https://www.patreon.com/c/DanCue44
