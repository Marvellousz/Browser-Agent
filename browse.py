#!/usr/bin/env python3
"""
Simple Browser Agent for Arch Linux
A user-friendly command-line tool for browsing with support for multiple browsers.
"""

import argparse
import os
import sys
import subprocess
import shutil
import time
import signal

# Define color codes for terminal output
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
RESET = "\033[0m"

def print_info(message):
    print(f"{BLUE}[INFO]{RESET} {message}")

def print_success(message):
    print(f"{GREEN}[SUCCESS]{RESET} {message}")

def print_warning(message):
    print(f"{YELLOW}[WARNING]{RESET} {message}")

def print_error(message):
    print(f"{RED}[ERROR]{RESET} {message}")

def check_browser(browser_name):
    """Check if a browser is installed in the system"""
    browser_commands = {
        'firefox': 'firefox',
        'chrome': 'google-chrome',
        'chromium': 'chromium',
        'brave': 'brave-browser',  
        'opera': 'opera',
        'vivaldi': 'vivaldi',
        'librewolf': 'librewolf',
        'zen': 'zen-browser',      
        'google-chrome': 'google-chrome',
        'brave-browser': 'brave-browser'
    }
    
    if browser_name not in browser_commands:
        return False
    
    # Check the primary name first
    if shutil.which(browser_commands[browser_name]) is not None:
        return True
        
    # Try alternative command names
    alt_commands = {
        'brave': ['brave', '/usr/bin/brave-browser', '/usr/bin/brave'],
        'chrome': ['chrome', '/usr/bin/google-chrome', '/usr/bin/chrome', '/usr/bin/google-chrome-stable', 'google-chrome-stable'],
        'google-chrome': ['chrome', '/usr/bin/google-chrome', '/usr/bin/chrome', '/usr/bin/google-chrome-stable', 'google-chrome-stable'],
        'opera': ['opera-browser', '/usr/bin/opera'],
        'vivaldi': ['vivaldi-stable', '/usr/bin/vivaldi-stable'],
        'zen': ['zen', '/usr/bin/zen']
    }
    
    if browser_name in alt_commands:
        for cmd in alt_commands[browser_name]:
            if shutil.which(cmd) is not None:
                return True
            if os.path.exists(cmd) and os.access(cmd, os.X_OK):
                return True
    
    return False

def detect_browsers():
    """Detect installed browsers"""
    browsers_to_check = [
        'firefox', 'chrome', 'chromium', 'brave', 'opera', 
        'vivaldi', 'librewolf', 'google-chrome', 'zen', 'brave-browser'
    ]
    
    installed_browsers = []
    seen = set()
    
    for browser in browsers_to_check:
        canonical_name = browser
        if browser == 'google-chrome':
            canonical_name = 'chrome'
        elif browser == 'brave-browser':
            canonical_name = 'brave'
            
        if canonical_name not in seen and check_browser(browser):
            installed_browsers.append(canonical_name)
            seen.add(canonical_name)
    
    if not installed_browsers:
        print_error("No supported browsers found. Please install Firefox, Chrome, Chromium, Brave, Opera, Vivaldi, or LibreWolf.")
        sys.exit(1)
    
    return installed_browsers

def get_default_browser(installed_browsers):
    """Get the default browser"""
    priority = ['firefox', 'chromium', 'chrome', 'brave', 'librewolf', 'opera', 'vivaldi']
    
    for browser in priority:
        if browser in installed_browsers:
            return browser
    
    return installed_browsers[0]  

def get_browser_command(browser_name):
    """Get the actual command to run the browser"""
    browser_commands = {
        'firefox': 'firefox',
        'chrome': 'google-chrome',
        'chromium': 'chromium',
        'brave': 'brave-browser',
        'opera': 'opera',
        'vivaldi': 'vivaldi',
        'librewolf': 'librewolf',
        'zen': 'zen-browser',
        'google-chrome': 'google-chrome',
        'brave-browser': 'brave-browser'
    }
    
    if browser_name in browser_commands and shutil.which(browser_commands[browser_name]):
        return browser_commands[browser_name]
    
    
    alt_commands = {
        'brave': ['brave', '/usr/bin/brave-browser', '/usr/bin/brave'],
        'chrome': ['chrome', '/usr/bin/google-chrome', '/usr/bin/chrome', '/usr/bin/google-chrome-stable', 'google-chrome-stable'],
        'google-chrome': ['chrome', '/usr/bin/google-chrome', '/usr/bin/chrome', '/usr/bin/google-chrome-stable', 'google-chrome-stable'],
        'opera': ['opera-browser', '/usr/bin/opera'],
        'vivaldi': ['vivaldi-stable', '/usr/bin/vivaldi-stable'],
        'zen': ['zen', '/usr/bin/zen']
    }
    
    if browser_name in alt_commands:
        for cmd in alt_commands[browser_name]:
            if shutil.which(cmd):
                return cmd
            if os.path.exists(cmd) and os.access(cmd, os.X_OK):
                return cmd
    
    return browser_name

def open_browser(browser_name, url=None, search_term=None, youtube=False):
    """Open a browser with optional URL, search term, or YouTube search"""
    browser_command = get_browser_command(browser_name)
    
    search_urls = {
        'google': 'https://www.google.com/search?q={}',
        'duckduckgo': 'https://duckduckgo.com/?q={}',
        'bing': 'https://www.bing.com/search?q={}'
    }
    
    command = [browser_command]
    
    private_flags = {
        'firefox': ['--private-window'],
        'chrome': ['--incognito'],
        'chromium': ['--incognito'],
        'brave': ['--incognito'],
        'opera': ['--private'],
        'vivaldi': ['--incognito'],
        'librewolf': ['--private-window']
    }
    
    # Add URL or search parameters
    if youtube and search_term:
        # Encode search term for URL
        encoded_term = search_term.replace(' ', '+')
        command.append(f"https://www.youtube.com/results?search_query={encoded_term}")
        print_info(f"Opening YouTube search for '{search_term}' with {browser_name.capitalize()}")
    elif search_term:
        # Default to Google search
        search_engine = 'google'
        encoded_term = search_term.replace(' ', '+')
        command.append(search_urls[search_engine].format(encoded_term))
        print_info(f"Searching for '{search_term}' with {browser_name.capitalize()}")
    elif url:
        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        command.append(url)
        print_info(f"Opening {url} with {browser_name.capitalize()}")
    else:
        print_info(f"Starting {browser_name.capitalize()}")
    
    try:
        # Launch the browser
        subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print_success(f"Browser launched successfully!")
        return True
    except Exception as e:
        print_error(f"Failed to launch {browser_name}: {e}")
        return False

def set_default_browser(browser_name):
    """Set default browser preference by saving to config file"""
    config_dir = os.path.expanduser("~/.config/browse")
    os.makedirs(config_dir, exist_ok=True)
    
    config_file = os.path.join(config_dir, "config")
    with open(config_file, "w") as f:
        f.write(f"default_browser={browser_name}")
    
    print_success(f"Default browser set to {browser_name.capitalize()}")

def get_saved_default_browser():
    """Get saved default browser from config file"""
    config_file = os.path.expanduser("~/.config/browse/config")
    if os.path.exists(config_file):
        try:
            with open(config_file, "r") as f:
                for line in f:
                    if line.startswith("default_browser="):
                        browser = line.strip().split("=")[1]
                        if check_browser(browser):
                            return browser
        except Exception:
            pass
    return None

def main():
    """Main entry point for the script"""
    # Detect installed browsers
    installed_browsers = detect_browsers()
    
    # Get default browser
    saved_default = get_saved_default_browser()
    default_browser = saved_default if saved_default else get_default_browser(installed_browsers)
    
    # Create argument parser
    parser = argparse.ArgumentParser(
        description='Simple Browser Agent for Arch Linux',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  # Open a website
  {sys.argv[0]} archlinux.org
  
  # Search on Google
  {sys.argv[0]} -s "arch linux wiki"
  
  # Search on YouTube
  {sys.argv[0]} -y "arch linux installation"
  
  # Use a specific browser
  {sys.argv[0]} -b firefox archlinux.org
  
  # Set default browser
  {sys.argv[0]} --set-default firefox
        """
    )
    
    # Add arguments
    parser.add_argument('url', nargs='?', help='URL to open (will add https:// if needed)')
    
    # We'll process the browser argument separately
    parser.add_argument('-b', '--browser', help=f'Browser to use (default: {default_browser})')
    
    parser.add_argument('-s', '--search', metavar='TERM', help='Search term')
    parser.add_argument('-y', '--youtube', metavar='TERM', help='Search YouTube')
    
    # We'll process this argument separately too
    parser.add_argument('--set-default', metavar='BROWSER', help='Set default browser')
    
    parser.add_argument('--list', action='store_true', help='List installed browsers')
    
    # Parse arguments
    args = parser.parse_args()
    
    # List installed browsers
    if args.list:
        print_info("Installed browsers:")
        for browser in installed_browsers:
            marker = " (default)" if browser == default_browser else ""
            print(f"  - {browser.capitalize()}{marker}")
        return
    
    # Set default browser (with validation)
    if args.set_default:
        browser_to_set = args.set_default.lower()
        # Check if this is a known browser variant
        canonical_browsers = {
            'google-chrome': 'chrome',
            'brave-browser': 'brave'
        }
        if browser_to_set in canonical_browsers:
            browser_to_set = canonical_browsers[browser_to_set]
            
        if browser_to_set in installed_browsers or check_browser(browser_to_set):
            set_default_browser(browser_to_set)
        else:
            print_error(f"Browser '{args.set_default}' is not installed")
            print_info(f"Available browsers: {', '.join(installed_browsers)}")
        return
    
    # Handle browser selection with validation
    selected_browser = default_browser
    if args.browser:
        browser_choice = args.browser.lower()
        # Check if this is a known browser variant
        canonical_browsers = {
            'google-chrome': 'chrome',
            'brave-browser': 'brave'
        }
        if browser_choice in canonical_browsers:
            browser_choice = canonical_browsers[browser_choice]
            
        if browser_choice in installed_browsers or check_browser(browser_choice):
            selected_browser = browser_choice
        else:
            print_error(f"Browser '{args.browser}' is not installed")
            print_info(f"Available browsers: {', '.join(installed_browsers)}")
            return
    
    # Execute commands
    if args.youtube:
        open_browser(selected_browser, search_term=args.youtube, youtube=True)
    elif args.search:
        open_browser(selected_browser, search_term=args.search)
    elif args.url:
        open_browser(selected_browser, url=args.url)
    else:
        open_browser(selected_browser)

if __name__ == "__main__":
    main()
