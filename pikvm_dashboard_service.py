#!/usr/bin/env python3
"""
PiKVM Dashboard Backend Service
Handles uptime tracking, action logs, user preferences, and scheduled actions
"""

import json
import time
import threading
import subprocess
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from werkzeug.utils import secure_filename
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS

# Configuration
DATA_DIR = Path("/var/lib/pikvm-dashboard")
ACTION_LOG_FILE = DATA_DIR / "action_log.json"
PREFERENCES_FILE = DATA_DIR / "preferences.json"
SCHEDULES_FILE = DATA_DIR / "schedules.json"
UPTIME_FILE = DATA_DIR / "uptime.json"
CONFIG_FILE = DATA_DIR / "config.json"

# Default settings
DEFAULT_ACTION_LOG_LIMIT = 100
DEFAULT_PREFERENCES = {
    "soundEnabled": True,
    "theme": "dark",
    "advancedFeaturesExpanded": False,
    "idleEnabled": [False] * 20,  # Support up to 20 PCs
    "idleMinutes": [30] * 20,
    "actionLogLimit": DEFAULT_ACTION_LOG_LIMIT
}

DEFAULT_CONFIG = {
    "version": "1.0",
    "firstRun": True,
    "hardware": {
        "hasSwitch": False,
        "pcCount": 1
    },
    "pcs": [
        {
            "id": 0,
            "name": "PC 1",
            "port": 0,
            "icon": "🖥️",
            "iconType": "emoji"
        }
    ],
    "appearance": {
        "theme": "dark",
        "primaryColor": "#667eea",
        "secondaryColor": "#764ba2",
        "backgroundColor": "#1e1e1e",
        "backgroundImage": "",
        "logo": "/logo.png",
        "dashboardTitle": "Control Dashboard"
    },
    "features": {
        "keyboardShortcuts": True,
        "scheduledActions": True,
        "idleShutdown": True,
        "actionLog": True,
        "uptimeTracking": True,
        "soundNotifications": True,
        "hddActivity": True
    },
    "advanced": {
        "statusCheckInterval": 30000,
        "hddCheckInterval": 1000,
        "actionLogLimit": 100,
        "requireConfirmation": True,
        "safeMode": False,
        "customCSS": ""
    }
}

# PiKVM API configuration
PIKVM_API_BASE = "http://localhost"

app = Flask(__name__)
CORS(app)

# Ensure data directory exists
DATA_DIR.mkdir(parents=True, exist_ok=True)


# ============ HELPER FUNCTIONS ============

def load_json_file(filepath: Path, default: dict) -> dict:
    """Load JSON file with fallback to default"""
    if filepath.exists():
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return default.copy()
    return default.copy()


def save_json_file(filepath: Path, data: dict) -> bool:
    """Save data to JSON file"""
    import subprocess
    try:
        # Make filesystem writable
        subprocess.run(['/usr/bin/rw'], check=False)
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        # Make filesystem read-only again
        subprocess.run(['/usr/bin/ro'], check=False)
        
        return True
    except Exception as e:
        print(f"Error saving JSON file: {e}")
        # Try to restore read-only even if save failed
        subprocess.run(['/usr/bin/ro'], check=False)
        return False


def get_pikvm_status() -> Optional[dict]:
    """Get current status from PiKVM API"""
    try:
        response = requests.get(f"{PIKVM_API_BASE}/api/switch", timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except requests.RequestException:
        return None


# ============ ACTION LOG API ============

@app.route('/api/dashboard/actions', methods=['GET'])
def get_actions():
    """Get action log history"""
    actions = load_json_file(ACTION_LOG_FILE, {"actions": []})
    return jsonify(actions)


@app.route('/api/dashboard/actions', methods=['POST'])
def add_action():
    """Add new action to log"""
    data = request.get_json()
    
    if not data or 'pcName' not in data or 'action' not in data:
        return jsonify({"error": "Missing required fields"}), 400
    
    # Load existing actions
    action_data = load_json_file(ACTION_LOG_FILE, {"actions": []})
    actions = action_data.get("actions", [])
    
    # Get action log limit from preferences
    prefs = load_json_file(PREFERENCES_FILE, DEFAULT_PREFERENCES)
    limit = prefs.get("actionLogLimit", DEFAULT_ACTION_LOG_LIMIT)
    
    # Add new action
    new_action = {
        "pcName": data['pcName'],
        "action": data['action'],
        "method": data.get('method', 'unknown'),
        "timestamp": datetime.now().isoformat()
    }
    
    actions.insert(0, new_action)  # Add to beginning
    
    # Trim to limit
    if len(actions) > limit:
        actions = actions[:limit]
    
    # Save
    action_data["actions"] = actions
    save_json_file(ACTION_LOG_FILE, action_data)
    
    return jsonify({"success": True, "action": new_action})


@app.route('/api/dashboard/actions', methods=['DELETE'])
def clear_actions():
    """Clear all actions"""
    save_json_file(ACTION_LOG_FILE, {"actions": []})
    return jsonify({"success": True})


# ============ PREFERENCES API ============

@app.route('/api/dashboard/preferences', methods=['GET'])
def get_preferences():
    """Get user preferences"""
    prefs = load_json_file(PREFERENCES_FILE, DEFAULT_PREFERENCES)
    return jsonify(prefs)


@app.route('/api/dashboard/preferences', methods=['POST'])
def update_preferences():
    """Update user preferences"""
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # Load existing preferences
    prefs = load_json_file(PREFERENCES_FILE, DEFAULT_PREFERENCES)
    
    # Update with new values
    prefs.update(data)
    
    # Save
    if save_json_file(PREFERENCES_FILE, prefs):
        return jsonify({"success": True, "preferences": prefs})
    else:
        return jsonify({"error": "Failed to save preferences"}), 500


# ============ SCHEDULED ACTIONS API ============

@app.route('/api/dashboard/schedules', methods=['GET'])
def get_schedules():
    """Get scheduled actions"""
    schedules = load_json_file(SCHEDULES_FILE, {"schedules": []})
    return jsonify(schedules)


@app.route('/api/dashboard/schedules', methods=['POST'])
def add_schedule():
    """Add new scheduled action (one-time or recurring) with optional secondary actions"""
    data = request.get_json()
    
    required_fields = ['port', 'action', 'time', 'pcName']
    if not data or not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400
    
    # Load existing schedules
    schedule_data = load_json_file(SCHEDULES_FILE, {"schedules": []})
    schedules = schedule_data.get("schedules", [])
    
    # Create new schedule
    new_schedule = {
        "id": int(time.time() * 1000),  # Timestamp in ms as ID
        "port": data['port'],
        "action": data['action'],  # "on", "off", "reset", "keyboard"
        "time": data['time'],
        "pcName": data['pcName'],
        "isRecurring": data.get('isRecurring', False)
    }
    
    # Add keyboard shortcut if action is keyboard
    if new_schedule['action'] == 'keyboard':
        new_schedule['keyboardShortcut'] = data.get('keyboardShortcut', 'ctrl-alt-del')
    
    # Add recurring fields if applicable
    if new_schedule['isRecurring']:
        new_schedule['frequency'] = data.get('frequency', 'daily')
        # Store days as array for weekly/biweekly, single value otherwise
        if data.get('frequency') in ['weekly', 'biweekly']:
            new_schedule['daysOfWeek'] = data.get('daysOfWeek', [])  # Array of day numbers
        new_schedule['lastExecuted'] = None
    
    # Initialize empty follow-up actions array
    new_schedule['followUpActions'] = []
    
    # Add secondary action if specified
    if data.get('hasSecondaryAction'):
        new_schedule['hasSecondaryAction'] = True
        new_schedule['secondaryDelay'] = data.get('secondaryDelay', 60)
        new_schedule['secondaryDelayUnit'] = data.get('secondaryDelayUnit', 'seconds')
        new_schedule['secondaryAction'] = data.get('secondaryAction', 'on')
        
        if new_schedule['secondaryAction'] == 'keyboard':
            new_schedule['secondaryKeyboardShortcut'] = data.get('secondaryKeyboardShortcut', 'ctrl-alt-del')
    
    schedules.append(new_schedule)
    
    # Save
    schedule_data["schedules"] = schedules
    save_json_file(SCHEDULES_FILE, schedule_data)
    
    return jsonify({"success": True, "schedule": new_schedule})


@app.route('/api/dashboard/schedules/<int:schedule_id>', methods=['DELETE'])
def delete_schedule(schedule_id):
    """Delete a scheduled action"""
    schedule_data = load_json_file(SCHEDULES_FILE, {"schedules": []})
    schedules = schedule_data.get("schedules", [])
    
    # Filter out the schedule to delete
    schedules = [s for s in schedules if s.get('id') != schedule_id]
    
    schedule_data["schedules"] = schedules
    save_json_file(SCHEDULES_FILE, schedule_data)
    
    return jsonify({"success": True})


@app.route('/api/dashboard/schedules/<int:schedule_id>/followup', methods=['POST'])
def add_followup_action(schedule_id):
    """Add a follow-up action to a schedule"""
    data = request.get_json()
    
    if not data or 'delay' not in data or 'delayUnit' not in data or 'action' not in data:
        return jsonify({"error": "Missing required fields"}), 400
    
    schedule_data = load_json_file(SCHEDULES_FILE, {"schedules": []})
    schedules = schedule_data.get("schedules", [])
    
    # Find the schedule
    schedule = next((s for s in schedules if s['id'] == schedule_id), None)
    if not schedule:
        return jsonify({"error": "Schedule not found"}), 404
    
    # Initialize followUpActions if it doesn't exist
    if 'followUpActions' not in schedule:
        schedule['followUpActions'] = []
    
    # Create follow-up action
    followup = {
        "delay": data['delay'],
        "delayUnit": data['delayUnit'],
        "action": data['action']
    }
    
    if data['action'] == 'keyboard':
        followup['keyboardShortcut'] = data.get('keyboardShortcut', 'ctrl-alt-del')
    
    schedule['followUpActions'].append(followup)
    
    # Save
    save_json_file(SCHEDULES_FILE, schedule_data)
    
    return jsonify({"success": True, "followup": followup})


@app.route('/api/dashboard/schedules/<int:schedule_id>/followup/<int:followup_index>', methods=['DELETE'])
def delete_followup_action(schedule_id, followup_index):
    """Delete a follow-up action from a schedule"""
    schedule_data = load_json_file(SCHEDULES_FILE, {"schedules": []})
    schedules = schedule_data.get("schedules", [])
    
    # Find the schedule
    schedule = next((s for s in schedules if s['id'] == schedule_id), None)
    if not schedule:
        return jsonify({"error": "Schedule not found"}), 404
    
    if 'followUpActions' not in schedule or followup_index >= len(schedule['followUpActions']):
        return jsonify({"error": "Follow-up not found"}), 404
    
    # Remove the follow-up
    schedule['followUpActions'].pop(followup_index)
    
    # Save
    save_json_file(SCHEDULES_FILE, schedule_data)
    
    return jsonify({"success": True})


# ============ CONFIGURATION API ============

@app.route('/api/dashboard/config', methods=['GET'])
def get_config():
    """Get dashboard configuration"""
    config = load_json_file(CONFIG_FILE, DEFAULT_CONFIG)
    return jsonify(config)


@app.route('/api/dashboard/config', methods=['POST'])
def save_config():
    """Save/update dashboard configuration"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        print(f"Received config data: {data}")
        
        # Load existing config
        config = load_json_file(CONFIG_FILE, DEFAULT_CONFIG)
        print(f"Loaded existing config: {config}")
        
        # Update with new values (deep merge for nested objects)
        def deep_merge(base, updates):
            for key, value in updates.items():
                if isinstance(value, dict) and key in base and isinstance(base[key], dict):
                    deep_merge(base[key], value)
                else:
                    base[key] = value
        
        deep_merge(config, data)
        print(f"Merged config: {config}")
        
        # Mark as no longer first run if completing setup
        if 'firstRun' in data:
            config['firstRun'] = data['firstRun']
        
        # Save
        print(f"Attempting to save to: {CONFIG_FILE}")
        if save_json_file(CONFIG_FILE, config):
            print("Config saved successfully")
            
            # Automatically cleanup unused icons
            try:
                cleanup_icons_internal(config)
            except Exception as cleanup_error:
                print(f"Warning: Icon cleanup failed: {cleanup_error}")
                # Don't fail the save if cleanup fails
            
            return jsonify({"success": True, "config": config})
        else:
            print("save_json_file returned False")
            return jsonify({"error": "Failed to save configuration"}), 500
    
    except Exception as e:
        print(f"ERROR in save_config: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/dashboard/config/reset', methods=['POST'])
def reset_config():
    """Reset configuration to defaults"""
    if save_json_file(CONFIG_FILE, DEFAULT_CONFIG):
        return jsonify({"success": True, "config": DEFAULT_CONFIG})
    else:
        return jsonify({"error": "Failed to reset configuration"}), 500


# ============ ICON UPLOAD API ============

UPLOAD_FOLDER = Path('/usr/share/kvmd/web/dashboard-images')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg', 'webp'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/dashboard/upload-icon', methods=['POST'])
def upload_icon():
    """Upload a custom icon image"""
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({"success": False, "error": "No file provided"}), 400
        
        file = request.files['file']
        
        # Check if file was actually selected
        if file.filename == '':
            return jsonify({"success": False, "error": "No file selected"}), 400
        
        # Validate file type
        if not allowed_file(file.filename):
            return jsonify({"success": False, "error": "Invalid file type. Use PNG, JPG, SVG, GIF, or WebP"}), 400
        
        # Secure the filename
        filename = secure_filename(file.filename)
        
        # Ensure upload directory exists
        UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
        
        # Make filesystem writable
        subprocess.run(['/usr/bin/rw'], check=False)
        
        try:
            # Save the file
            filepath = UPLOAD_FOLDER / filename
            file.save(str(filepath))
            
            # Set proper permissions
            os.chmod(str(filepath), 0o644)
            
            # Make filesystem read-only again
            subprocess.run(['/usr/bin/ro'], check=False)
            
            return jsonify({
                "success": True,
                "filename": filename,
                "path": f"/dashboard-images/{filename}"
            })
            
        except Exception as e:
            # Ensure filesystem is read-only even on error
            subprocess.run(['/usr/bin/ro'], check=False)
            raise e
            
    except Exception as e:
        print(f"Error uploading icon: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/dashboard/cleanup-icons', methods=['POST'])
def cleanup_unused_icons():
    """Remove icon files that aren't referenced in config"""
    try:
        config = load_json_file(CONFIG_FILE, DEFAULT_CONFIG)
        result = cleanup_icons_internal(config)
        return jsonify(result)
    except Exception as e:
        subprocess.run(['/usr/bin/ro'], check=False)
        print(f"Error cleaning up icons: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


def cleanup_icons_internal(config):
    """Internal function to cleanup unused icons (can be called from other endpoints)"""
    # Get all icons currently in use
    used_icons = set()
    for pc in config.get('pcs', []):
        if pc.get('iconType') == 'image':
            icon_path = pc.get('icon', '')
            if icon_path.startswith('/dashboard-images/'):
                filename = icon_path.split('/')[-1]
                used_icons.add(filename)
    
    # Get all files in upload folder
    if not UPLOAD_FOLDER.exists():
        return {"success": True, "deleted": [], "message": "Upload folder doesn't exist"}
    
    all_files = set(f.name for f in UPLOAD_FOLDER.iterdir() if f.is_file())
    
    # Determine unused files
    unused = all_files - used_icons
    
    if not unused:
        return {"success": True, "deleted": [], "message": "No unused icons found"}
    
    # Delete unused files
    subprocess.run(['/usr/bin/rw'], check=False)
    
    deleted = []
    try:
        for filename in unused:
            filepath = UPLOAD_FOLDER / filename
            if filepath.exists():
                filepath.unlink()
                deleted.append(filename)
                print(f"Deleted unused icon: {filename}")
    finally:
        subprocess.run(['/usr/bin/ro'], check=False)
    
    return {
        "success": True,
        "deleted": deleted,
        "message": f"Deleted {len(deleted)} unused icon(s)"
    }


# ============ UPTIME TRACKING API ============

@app.route('/api/dashboard/uptime', methods=['GET'])
def get_uptime():
    """Get uptime statistics for all configured PCs"""
    # Load config to see how many PCs we have
    config = load_json_file(CONFIG_FILE, DEFAULT_CONFIG)
    pc_count = config.get('hardware', {}).get('pcCount', 2)
    
    # Initialize uptime data for all ports
    uptime_data = load_json_file(UPTIME_FILE, {
        str(i): {"totalUptime": 0, "bootTime": None, "lastCheck": None}
        for i in range(pc_count)
    })
    
    # Get current status
    status = get_pikvm_status()
    
    if status:
        power_array = status.get('result', {}).get('atx', {}).get('leds', {}).get('power', [])
        
        for port in range(pc_count):
            port_str = str(port)
            is_on = power_array[port] if port < len(power_array) else False
            
            if port_str not in uptime_data:
                uptime_data[port_str] = {"totalUptime": 0, "bootTime": None, "lastCheck": None}
            
            port_data = uptime_data[port_str]
            
            if is_on:
                current_time = time.time()
                
                # If PC just booted (was off, now on)
                if port_data.get('bootTime') is None:
                    port_data['bootTime'] = current_time
                
                # Calculate current session uptime
                boot_time = port_data.get('bootTime', current_time)
                current_uptime = current_time - boot_time
                
                port_data['currentUptime'] = int(current_uptime)
                port_data['lastCheck'] = current_time
            else:
                # PC is off
                if port_data.get('bootTime') is not None:
                    # PC was on, now off - add session to total
                    last_check = port_data.get('lastCheck', time.time())
                    boot_time = port_data.get('bootTime', last_check)
                    session_uptime = last_check - boot_time
                    
                    port_data['totalUptime'] = port_data.get('totalUptime', 0) + session_uptime
                    port_data['bootTime'] = None
                
                port_data['currentUptime'] = 0
                port_data['lastCheck'] = time.time()
        
        save_json_file(UPTIME_FILE, uptime_data)
    
    return jsonify(uptime_data)


# ============ SCHEDULED ACTIONS EXECUTOR ============

def execute_scheduled_action(schedule: dict):
    """Execute a scheduled action via PiKVM API"""
    port = schedule.get('port', 0)
    action = schedule['action']
    
    # Load config to determine if we have a switch
    config = load_json_file(CONFIG_FILE, DEFAULT_CONFIG)
    has_switch = config.get('hardware', {}).get('hasSwitch', False)
    
    try:
        # Execute primary action
        if action == 'keyboard':
            # Execute keyboard shortcut
            shortcut = schedule.get('keyboardShortcut', 'ctrl-alt-del')
            execute_keyboard_shortcut(shortcut, port, has_switch)
        else:
            # Execute power action
            if has_switch:
                # Switch mode - include port parameter
                if action == 'on':
                    requests.post(f"{PIKVM_API_BASE}/api/switch/atx/power?port={port}&action=on", timeout=5)
                elif action == 'off':
                    requests.post(f"{PIKVM_API_BASE}/api/switch/atx/click?port={port}&button=power", timeout=5)
                elif action == 'reset':
                    requests.post(f"{PIKVM_API_BASE}/api/switch/atx/click?port={port}&button=reset", timeout=5)
            else:
                # Non-switch mode - no port parameter
                if action == 'on':
                    requests.post(f"{PIKVM_API_BASE}/api/atx/power?action=on", timeout=5)
                elif action == 'off':
                    requests.post(f"{PIKVM_API_BASE}/api/atx/click?button=power", timeout=5)
                elif action == 'reset':
                    requests.post(f"{PIKVM_API_BASE}/api/atx/click?button=reset", timeout=5)
        
        # Log the primary action
        action_type = "Recurring" if schedule.get('isRecurring') else "Scheduled"
        action_desc = schedule.get('keyboardShortcut', action) if action == 'keyboard' else action
        requests.post(f"http://localhost:5000/api/dashboard/actions", 
                     json={
                         "pcName": schedule['pcName'],
                         "action": f"{action_type} {action_desc}",
                         "method": "scheduled"
                     }, timeout=5)
        
        print(f"Executed {action_type.lower()} action: {action_desc} on {schedule['pcName']}")
        
        # Execute follow-up actions if configured
        if schedule.get('followUpActions') and len(schedule['followUpActions']) > 0:
            threading.Thread(
                target=execute_followup_chain,
                args=(schedule,),
                daemon=True
            ).start()
        
        # Legacy: Schedule secondary action if configured (backwards compatibility)
        elif schedule.get('hasSecondaryAction'):
            threading.Thread(
                target=execute_secondary_action,
                args=(schedule,),
                daemon=True
            ).start()
        
    except requests.RequestException as e:
        print(f"Failed to execute scheduled action: {e}")


def execute_followup_chain(schedule: dict):
    """Execute chain of follow-up actions with delays"""
    try:
        port = schedule.get('port', 0)
        config = load_json_file(CONFIG_FILE, DEFAULT_CONFIG)
        has_switch = config.get('hardware', {}).get('hasSwitch', False)
        
        for followup in schedule.get('followUpActions', []):
            # Calculate delay in seconds
            delay = followup.get('delay', 60)
            unit = followup.get('delayUnit', 'seconds')
            
            if unit == 'minutes':
                delay *= 60
            elif unit == 'hours':
                delay *= 3600
            elif unit == 'days':
                delay *= 86400
            
            print(f"Waiting {delay} seconds before executing follow-up action for {schedule['pcName']}")
            time.sleep(delay)
            
            # Execute the follow-up action
            action = followup.get('action')
            
            if action == 'keyboard':
                shortcut = followup.get('keyboardShortcut', 'ctrl-alt-del')
                execute_keyboard_shortcut(shortcut, port, has_switch)
                action_desc = shortcut
            else:
                # Execute power action
                if has_switch:
                    if action == 'on':
                        requests.post(f"{PIKVM_API_BASE}/api/switch/atx/power?port={port}&action=on", timeout=5)
                    elif action == 'off':
                        requests.post(f"{PIKVM_API_BASE}/api/switch/atx/click?port={port}&button=power", timeout=5)
                    elif action == 'reset':
                        requests.post(f"{PIKVM_API_BASE}/api/switch/atx/click?port={port}&button=reset", timeout=5)
                else:
                    if action == 'on':
                        requests.post(f"{PIKVM_API_BASE}/api/atx/power?action=on", timeout=5)
                    elif action == 'off':
                        requests.post(f"{PIKVM_API_BASE}/api/atx/click?button=power", timeout=5)
                    elif action == 'reset':
                        requests.post(f"{PIKVM_API_BASE}/api/atx/click?button=reset", timeout=5)
                action_desc = action
            
            # Log the follow-up action
            requests.post(f"http://localhost:5000/api/dashboard/actions", 
                         json={
                             "pcName": schedule['pcName'],
                             "action": f"Follow-up {action_desc}",
                             "method": "scheduled"
                         }, timeout=5)
            
            print(f"Executed follow-up action: {action_desc} on {schedule['pcName']}")
            
    except Exception as e:
        print(f"Failed to execute follow-up action: {e}")


def execute_keyboard_shortcut(shortcut: str, port: int, has_switch: bool):
    """Execute a keyboard shortcut via PiKVM HID API"""
    # Map shortcuts to PiKVM key sequences
    shortcuts = {
        'ctrl-alt-del': 'ControlLeft+AltLeft+Delete',
        'ctrl-alt-esc': 'ControlLeft+AltLeft+Escape',
        'alt-f4': 'AltLeft+F4',
        'win': 'MetaLeft',
        'win-r': 'MetaLeft+KeyR',
        'win-l': 'MetaLeft+KeyL'
    }
    
    key_sequence = shortcuts.get(shortcut, 'ControlLeft+AltLeft+Delete')
    
    # If switch mode, we may need to select the port first (depends on PiKVM setup)
    # For now, we'll just send the keyboard command
    requests.post(f"{PIKVM_API_BASE}/api/hid/print?limit=0&text={key_sequence}", timeout=5)


def execute_secondary_action(schedule: dict):
    """Execute secondary action after delay"""
    try:
        # Calculate delay in seconds
        delay = schedule.get('secondaryDelay', 60)
        unit = schedule.get('secondaryDelayUnit', 'seconds')
        
        if unit == 'minutes':
            delay *= 60
        elif unit == 'hours':
            delay *= 3600
        elif unit == 'days':
            delay *= 86400
        
        print(f"Waiting {delay} seconds before executing secondary action for {schedule['pcName']}")
        time.sleep(delay)
        
        # Execute secondary action
        port = schedule.get('port', 0)
        secondary_action = schedule.get('secondaryAction', 'on')
        
        config = load_json_file(CONFIG_FILE, DEFAULT_CONFIG)
        has_switch = config.get('hardware', {}).get('hasSwitch', False)
        
        if secondary_action == 'keyboard':
            # Execute keyboard shortcut
            shortcut = schedule.get('secondaryKeyboardShortcut', 'ctrl-alt-del')
            execute_keyboard_shortcut(shortcut, port, has_switch)
            action_desc = shortcut
        else:
            # Execute power action
            if has_switch:
                if secondary_action == 'on':
                    requests.post(f"{PIKVM_API_BASE}/api/switch/atx/power?port={port}&action=on", timeout=5)
                elif secondary_action == 'off':
                    requests.post(f"{PIKVM_API_BASE}/api/switch/atx/click?port={port}&button=power", timeout=5)
                elif secondary_action == 'reset':
                    requests.post(f"{PIKVM_API_BASE}/api/switch/atx/click?port={port}&button=reset", timeout=5)
            else:
                if secondary_action == 'on':
                    requests.post(f"{PIKVM_API_BASE}/api/atx/power?action=on", timeout=5)
                elif secondary_action == 'off':
                    requests.post(f"{PIKVM_API_BASE}/api/atx/click?button=power", timeout=5)
                elif secondary_action == 'reset':
                    requests.post(f"{PIKVM_API_BASE}/api/atx/click?button=reset", timeout=5)
            action_desc = secondary_action
        
        # Log the secondary action
        requests.post(f"http://localhost:5000/api/dashboard/actions", 
                     json={
                         "pcName": schedule['pcName'],
                         "action": f"Secondary {action_desc}",
                         "method": "scheduled"
                     }, timeout=5)
        
        print(f"Executed secondary action: {action_desc} on {schedule['pcName']}")
        
    except Exception as e:
        print(f"Failed to execute secondary action: {e}")


def calculate_next_execution(schedule: dict) -> int:
    """Calculate next execution time for a recurring schedule (returns ms timestamp)"""
    if not schedule.get('isRecurring'):
        return schedule['time']
    
    frequency = schedule.get('frequency', 'daily')
    current_time = datetime.now()
    
    # Parse the original schedule time to get hour and minute
    schedule_dt = datetime.fromtimestamp(schedule['time'] / 1000)
    target_hour = schedule_dt.hour
    target_minute = schedule_dt.minute
    
    # Start from today at the target time
    next_exec = current_time.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
    
    # If we've already passed today's time, move to tomorrow
    if next_exec <= current_time:
        next_exec += timedelta(days=1)
    
    if frequency == 'daily':
        # Already set to next occurrence
        pass
    
    elif frequency == 'weekly':
        # Find next occurrence of any target day of week
        days_of_week = schedule.get('daysOfWeek', [schedule.get('dayOfWeek', 0)])  # Support both formats
        if not isinstance(days_of_week, list):
            days_of_week = [days_of_week]
        
        # Find the nearest upcoming day from the list
        min_days_ahead = 8  # Start with impossible value
        for target_day in days_of_week:
            days_ahead = target_day - next_exec.weekday()
            if days_ahead <= 0:  # Target day already happened this week
                days_ahead += 7
            if days_ahead < min_days_ahead:
                min_days_ahead = days_ahead
        
        next_exec += timedelta(days=min_days_ahead)
    
    elif frequency == 'biweekly':
        # Find next occurrence of any target day, then ensure it's 2 weeks from last execution
        days_of_week = schedule.get('daysOfWeek', [schedule.get('dayOfWeek', 0)])
        if not isinstance(days_of_week, list):
            days_of_week = [days_of_week]
        
        # Find the nearest upcoming day from the list
        min_days_ahead = 8
        for target_day in days_of_week:
            days_ahead = target_day - next_exec.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            if days_ahead < min_days_ahead:
                min_days_ahead = days_ahead
        
        next_exec += timedelta(days=min_days_ahead)
        
        # If we have a last execution, ensure we're at least 14 days from it
        if schedule.get('lastExecuted'):
            last_exec_dt = datetime.fromtimestamp(schedule['lastExecuted'] / 1000)
            while (next_exec - last_exec_dt).days < 14:
                next_exec += timedelta(days=7)
    
    elif frequency == 'monthly':
        # Same day of month, next month
        if next_exec.month == 12:
            next_exec = next_exec.replace(year=next_exec.year + 1, month=1)
        else:
            next_exec = next_exec.replace(month=next_exec.month + 1)
    
    elif frequency == 'quarterly':
        # Add 3 months
        new_month = next_exec.month + 3
        new_year = next_exec.year
        if new_month > 12:
            new_month -= 12
            new_year += 1
        next_exec = next_exec.replace(year=new_year, month=new_month)
    
    elif frequency == 'annually':
        # Same date, next year
        next_exec = next_exec.replace(year=next_exec.year + 1)
    
    return int(next_exec.timestamp() * 1000)


def schedule_checker():
    """Background thread to check and execute scheduled actions"""
    print("="*50, flush=True)
    print("SCHEDULE CHECKER THREAD STARTED", flush=True)
    print("="*50, flush=True)
    
    while True:
        try:
            schedule_data = load_json_file(SCHEDULES_FILE, {"schedules": []})
            schedules = schedule_data.get("schedules", [])
            
            if len(schedules) > 0:
                print(f"[Schedule Checker] Checking {len(schedules)} schedule(s)", flush=True)
            
            current_time = int(time.time() * 1000)
            modified = False
            
            for schedule in schedules:
                # Calculate current execution time (handles recurring schedules)
                exec_time = calculate_next_execution(schedule)
                
                time_until = (exec_time - current_time) / 1000  # seconds
                if time_until < 60:  # Log if within 1 minute
                    print(f"[Schedule] {schedule['pcName']} - {schedule['action']} in {time_until:.0f}s (exec_time: {datetime.fromtimestamp(exec_time/1000)})", flush=True)
                
                # If it's time to execute
                if exec_time <= current_time:
                    print(f"[EXECUTING] {schedule['pcName']} - {schedule['action']}", flush=True)
                    execute_scheduled_action(schedule)
                    
                    if schedule.get('isRecurring'):
                        # Update last executed time and calculate next execution
                        schedule['lastExecuted'] = current_time
                        schedule['time'] = calculate_next_execution(schedule)
                        modified = True
                        print(f"Recurring schedule updated: next execution at {datetime.fromtimestamp(schedule['time']/1000)}", flush=True)
                    else:
                        # Remove one-time schedules after execution
                        schedules.remove(schedule)
                        modified = True
                        print(f"One-time schedule completed and removed", flush=True)
            
            # Save if anything changed
            if modified:
                schedule_data["schedules"] = schedules
                save_json_file(SCHEDULES_FILE, schedule_data)
        
        except Exception as e:
            print(f"Error in schedule checker: {e}", flush=True)
            import traceback
            traceback.print_exc()
        
        time.sleep(5)  # Check every 5 seconds


def uptime_tracker():
    """Background thread to track uptime"""
    while True:
        try:
            # Update uptime data
            get_uptime()
        except Exception as e:
            print(f"Error in uptime tracker: {e}")
        
        time.sleep(30)  # Update every 30 seconds


# ============ MAIN ============

if __name__ == '__main__':
    print("="*60, flush=True)
    print("PIKVM DASHBOARD SERVICE STARTING", flush=True)
    print("="*60, flush=True)
    
    # Start background threads
    print("Starting schedule checker thread...", flush=True)
    schedule_thread = threading.Thread(target=schedule_checker, daemon=True)
    schedule_thread.start()
    
    print("Starting uptime tracker thread...", flush=True)
    uptime_thread = threading.Thread(target=uptime_tracker, daemon=True)
    uptime_thread.start()
    
    print(f"Data directory: {DATA_DIR}", flush=True)
    print("API endpoints available at http://localhost:5000/api/dashboard/", flush=True)
    print("="*60, flush=True)
    
    # Run Flask app
    app.run(host='0.0.0.0', port=5000, debug=False)
