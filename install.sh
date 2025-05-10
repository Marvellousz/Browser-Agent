#!/bin/bash
#
# Installer script for the Browse tool
#

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' 

# Header
echo -e "${BLUE}╔═══════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     Browse Tool Installer for Arch    ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════╝${NC}"

# Verify we're on Arch Linux
if [ -f /etc/arch-release ]; then
    echo -e "${GREEN}✓ Arch Linux detected${NC}"
else
    echo -e "${YELLOW}⚠ This doesn't appear to be Arch Linux${NC}"
    echo -e "${YELLOW}⚠ The script may still work, but it's designed for Arch${NC}"
    read -p "Continue anyway? (y/n): " CONTINUE
    if [[ $CONTINUE != "y" && $CONTINUE != "Y" ]]; then
        echo -e "${RED}Installation cancelled.${NC}"
        exit 1
    fi
fi

# Check Python is installed
if command -v python3 &>/dev/null; then
    echo -e "${GREEN}✓ Python 3 is installed${NC}"
    PYTHON_VERSION=$(python3 --version)
    echo -e "  ${BLUE}$PYTHON_VERSION${NC}"
else
    echo -e "${RED}✗ Python 3 is not installed${NC}"
    echo -e "${YELLOW}Installing Python 3...${NC}"
    sudo pacman -S --noconfirm python
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to install Python 3. Please install it manually.${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Python 3 installed successfully${NC}"
fi

# Check for required Python packages
echo -e "${BLUE}Checking for required Python packages...${NC}"
REQUIRED_PACKAGES=("playwright" "argparse")
MISSING_PACKAGES=()

for package in "${REQUIRED_PACKAGES[@]}"; do
    if ! python3 -c "import $package" &>/dev/null; then
        MISSING_PACKAGES+=("$package")
    else
        echo -e "${GREEN}✓ $package is installed${NC}"
    fi
done

if [ ${#MISSING_PACKAGES[@]} -gt 0 ]; then
    echo -e "${YELLOW}Installing missing Python packages: ${MISSING_PACKAGES[*]}${NC}"
    pip install --user "${MISSING_PACKAGES[@]}"
    
    # Verify installation
    for package in "${MISSING_PACKAGES[@]}"; do
        if ! python3 -c "import $package" &>/dev/null; then
            echo -e "${RED}✗ Failed to install $package. Please install it manually.${NC}"
            exit 1
        else
            echo -e "${GREEN}✓ $package installed successfully${NC}"
        fi
    done
fi

# Install Playwright browsers if needed
if python3 -c "import playwright" &>/dev/null; then
    echo -e "${BLUE}Installing Playwright browsers...${NC}"
    python3 -m playwright install
    if [ $? -ne 0 ]; then
        echo -e "${YELLOW}⚠ Failed to install Playwright browsers automatically.${NC}"
        echo -e "${YELLOW}⚠ You may need to run 'playwright install' manually.${NC}"
    else
        echo -e "${GREEN}✓ Playwright browsers installed successfully${NC}"
    fi
fi

# Create installation directory
INSTALL_DIR="/usr/local/bin"
if [ ! -d "$INSTALL_DIR" ]; then
    echo -e "${YELLOW}Creating installation directory...${NC}"
    sudo mkdir -p "$INSTALL_DIR"
fi

# Check if browse.py exists in the current directory
if [ ! -f "browse.py" ]; then
    echo -e "${RED}✗ browse.py not found in the current directory${NC}"
    echo -e "${YELLOW}Please run this script from the directory containing browse.py${NC}"
    exit 1
fi

# Copy the script
echo -e "${BLUE}Installing browse tool...${NC}"
sudo cp browse.py "$INSTALL_DIR/browse"
sudo chmod +x "$INSTALL_DIR/browse"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Installation successful!${NC}"
    echo -e "${BLUE}You can now use the browse tool with these commands:${NC}"
    echo -e "${GREEN}  browse archlinux.org${NC}        ${BLUE}- Open a website${NC}"
    echo -e "${GREEN}  browse -s \"arch linux\"${NC}      ${BLUE}- Search Google${NC}"
    echo -e "${GREEN}  browse -y \"linux tutorial\"${NC}  ${BLUE}- Search YouTube${NC}"
    echo -e "${GREEN}  browse -b firefox github.com${NC} ${BLUE}- Use Firefox specifically${NC}"
    echo -e "${GREEN}  browse --list${NC}                ${BLUE}- Show installed browsers${NC}"
    echo -e "${GREEN}  browse --set-default firefox${NC} ${BLUE}- Set Firefox as default${NC}"
else
    echo -e "${RED}✗ Installation failed${NC}"
    echo -e "${YELLOW}You may need to run this script with sudo.${NC}"
    exit 1
fi

# Detect browsers
echo -e "\n${BLUE}Detecting installed browsers...${NC}"
BROWSERS=("firefox" "chromium" "google-chrome-stable" "google-chrome" "chrome" "brave-browser" "brave" "opera" "vivaldi" "librewolf" "zen")
FOUND=0
FOUND_BROWSERS=()

for browser in "${BROWSERS[@]}"; do
    # Try multiple possible paths and check for executable files
    if command -v $browser &>/dev/null || [ -x "/usr/bin/$browser" ] || [ -x "/usr/local/bin/$browser" ] || [ -x "/opt/google/chrome/google-chrome" ]; then
        # Normalize browser names
        DISPLAY_NAME=$browser
        if [ "$browser" == "google-chrome" ] || [ "$browser" == "google-chrome-stable" ]; then
            DISPLAY_NAME="Chrome"
        elif [ "$browser" == "brave-browser" ] || [ "$browser" == "brave" ]; then
            DISPLAY_NAME="Brave"
        elif [ "$browser" == "chromium" ]; then
            DISPLAY_NAME="Chromium"
        else
            # Capitalize first letter
            DISPLAY_NAME="$(tr '[:lower:]' '[:upper:]' <<< ${browser:0:1})${browser:1}"
        fi

        # Check if we've already found this browser (by different name)
        if [[ ! " ${FOUND_BROWSERS[*]} " =~ " ${DISPLAY_NAME} " ]]; then
            echo -e "${GREEN}✓ Found: ${DISPLAY_NAME}${NC}"
            FOUND_BROWSERS+=("$DISPLAY_NAME")
            FOUND=1
        fi
    fi
done

if [ $FOUND -eq 0 ]; then
    echo -e "${YELLOW}⚠ No supported browsers detected${NC}"
    echo -e "${YELLOW}⚠ You should install at least one of: Firefox, Chromium, Chrome, Brave, Opera, Vivaldi, or LibreWolf${NC}"
    echo -e "${YELLOW}⚠ For Chrome on Arch Linux, install with: yay -S google-chrome${NC}"
fi

# Create a symbolic link for Chrome if needed
if command -v google-chrome-stable &>/dev/null && ! command -v google-chrome &>/dev/null; then
    echo -e "${YELLOW}Creating symbolic link for Google Chrome...${NC}"
    sudo ln -sf /usr/bin/google-chrome-stable /usr/bin/google-chrome
    echo -e "${GREEN}✓ Symbolic link created: google-chrome-stable → google-chrome${NC}"
fi

echo -e "\n${GREEN}Installation complete! Enjoy browsing.${NC}"
