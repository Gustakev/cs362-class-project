# iExtract - System Administrator Deployment & Setup Guide

This document outlines the deployment process, system-level dependencies, and source package configuration required for system administrators or advanced users to host, deploy, and configure the iExtract application.

## 1. System-Level Dependencies
Before downloading the source package, the host system must be provisioned with the following environments:

* **Python Runtime**: Python 3.13 or newer is strictly required to support the asynchronous features of the Textual framework.
* **Git**: Required for fetching the source distribution from the version control system.
* **Tkinter (Linux Deployments Only)**: Windows and macOS distributions include Tkinter natively with Python. If deploying on a Linux environment (e.g., Ubuntu, Linux Mint), the system administrator must install the package manager equivalent to enable the GUI folder picker.
  * *Debian/Ubuntu/Mint*: `sudo apt-get install python3-tk`

## 2. Downloading the Source Package
Users should pull the latest stable branch from the repository to the host machine:

```bash
git clone [https://github.com/Gustakev/cs362-class-project.git](https://github.com/Gustakev/cs362-class-project.git)
cd cs362-class-project


```

## 3. Environment Deployment & Libraries

To prevent dependency conflicts with system-level Python packages, iExtract must be deployed within an isolated virtual environment. 

### Required Software Libraries
The application relies on the following libraries. 

**Standard Python Libraries (Pre-installed with Python 3.13+):**
* `os` & `sys`: Core system operations and path resolutions.
* `pathlib`: Object-oriented filesystem path manipulation.
* `tkinter`: Invokes native OS file dialogs for GUI folder selection. *(Note: Linux systems require the `python3-tk` system package).*
* `webbrowser`: Routes help documentation links to the system's default browser.
* `sqlite3`: Parses the local Apple iOS `Manifest.db` backup database.

**Third-Party Libraries (Installed via pip):**
* `textual` (>=0.50.0): Powers the asynchronous terminal user interface (TUI) and background thread management.
* `Pillow` (>=10.0.0): Handles image loading and OS-native display for the Photo Descriptor.
* `requests` (>=2.31.0): Manages outbound HTTP/REST communication for the AI captioning model.
* `pywin32`: Specific to Windows deployments for enhanced terminal rendering.

### Deployment Commands
Deploy the environment and install the required third-party libraries:

# Initialize the virtual environment
```python3 -m venv venv

# Activate the environment (Mac/Linux)
source venv/bin/activate

# Activate the environment (Windows)
venv\Scripts\activate

# Install all third-party dependencies
pip install -r requirements.txt
```
## 4. Configuration & Architecture
iExtract is designed as a standalone, localized extraction tool. It does not require a traditional database server to be hosted or configured. The application relies entirely on parsing the local `Manifest.db` SQLite file generated natively by Apple's iOS backup process. 

**Beta Features Setup (Photo Descriptor):**
If deploying the Photo Descriptor feature for testing, ensure the following network and file-system configurations are met:
1. **Network Access**: The host system must have outbound network access to reach external AI APIs via the `requests` library.
2. **File Permissions**: The `functional_components/photo_caption/data/` directory must have proper read/write permissions for the application user to allow image processing.

## 5. Execution & Hosting
Once deployed and configured, the application can be launched via the main routing script. 

**Local Deployment:**
```bash
python iExtract.py
