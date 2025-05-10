# Browser Agent

A powerful command-line tool for controlling web browsers from your terminal. Browser Agent allows you to open websites, search the web, and automate browser tasks with simple commands.

## Features

- Launch multiple browsers (Firefox, Chrome, Chromium, Brave, Opera, Vivaldi, LibreWolf, Zen)
- Open websites with automatic protocol handling
- Search Google directly from the terminal
- Search YouTube videos from the command line
- Set and remember your default browser
- Private browsing mode support

## Installation

Clone the repository and run the installer:

```bash
git clone https://github.com/Marvellousz/Browser-Agent
cd browser-agent
chmod +x install.sh
./install.sh
```

The installer will:
- Check for Python and required dependencies
- Install the tool system-wide
- Detect installed browsers
- Create necessary configuration files

## Usage

```bash
# Open a website
browse archlinux.org

# Search on Google
browse -s "arch linux wiki"

# Search on YouTube
browse -y "arch linux installation"

# Use a specific browser
browse -b firefox github.com

# List installed browsers
browse --list

# Set default browser
browse --set-default firefox
```

## Requirements

- Python 3.8+
- Playwright (automatically installed by the installer)
- At least one web browser installed

## Contributing

Contributions are welcome! Feel free to submit a Pull Request.
