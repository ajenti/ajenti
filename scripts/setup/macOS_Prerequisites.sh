#!/bin/bash

# Prerequisites Installer for macOS
# Description: Ensures necessary prerequisites are installed on macOS.

echo "Checking the macOs prerequisites:"

# Function to check if a command is available
command_exists() {
  command -v "$1" >/dev/null 2>&1
}

# Check if Homebrew is installed; if not, install it
if ! command_exists brew; then
  echo "Installing Homebrew..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
  echo "Homebrew is already installed."
fi

# Install Docker if not installed
if ! command_exists docker; then
  echo "Installing Docker..."
  brew install --cask docker
else
  echo "Docker is already installed."
fi

# Install pip3 if not installed
if ! command_exists pip3; then
  echo "Installing pip3..."
  brew install python@3.9
else
  echo "pip3 is already installed."
fi

# Install yarn if not installed
if ! command_exists yarn; then
  echo "Installing yarn..."
  brew install yarn
else
  echo "yarn is already installed."
fi

USERNAME=$(whoami)

# Add custom path to .bash_profile if not already added
path_exists=$(grep -qF "export PATH=\$PATH:/Users/$USERNAME/.local/bin" ~/.bash_profile 2>/dev/null && echo "1" || echo "0")
if [ "$path_exists" -eq "0" ]; then
  echo "export PATH=\$PATH:/Users/$USERNAME/.local/bin" >> ~/.bash_profile
  source ~/.bash_profile
  echo "Path added to .bash_profile."
else
  echo "Path already added to .bash_profile."
fi

# Install Python 3.10 and create a virtual environment if not installed
if ! command_exists python3.10; then
  echo "Installing Python 3.10 and creating a virtual environment..."
  brew install python@3.10
  python3.10 -m venv my-project-env
  source my-project-env/bin/activate
else
  echo "Python 3.10 is already installed."
fi

echo " "
echo "All macOs prerequisites are installed"
echo " "


