# iExtract - System Administrator Deployment & Setup Guide

This document outlines the deployment process, system-level dependencies, and source package configuration required for system administrators or advanced users to host, deploy, and configure the iExtract application.

## 1. System-Level Dependencies
Before downloading the source package, the host system must be provisioned with the following environments:

* **Python Runtime**: Python 3.13 or newer is strictly required to support the asynchronous features of the Textual framework.
* **Git**: Required for fetching the source distribution from the version control system.
* **Tkinter (Linux Deployments Only)**: Windows and macOS distributions include Tkinter natively with Python. If deploying on a Linux environment (e.g., Ubuntu, Linux Mint), the system administrator must install the package manager equivalent to enable the GUI folder picker.
  * *Debian/Ubuntu/Mint*: `sudo apt-get install python3-tk`
* **libheif (Linux and macOS Deployments Only)**: Required by `pillow-heif` for HEIC image conversion support.
  * *Debian/Ubuntu/Mint*: `sudo apt install libheif-dev`
  * *macOS (via Homebrew)*: `brew install libheif`

## 2. Downloading the Source Package
Users should pull the latest stable branch from the repository to the host machine:

```bash
git clone https://github.com/Gustakev/cs362-class-project.git
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
* `pillow-heif`: Enables HEIC/HEIF image format support via Pillow for the conversion engine.
* `imageio-ffmpeg`: Provides a bundled ffmpeg binary used by the conversion engine for MOV to MP4 transcoding.
* `pydantic`: Powers the domain model layer, providing data validation and serialization for BackupModel and related objects.
* `requests` (>=2.31.0): Manages outbound HTTP/REST communication for the AI captioning model.
* `pywin32` *(Optional: Windows only)*: Provides enhanced terminal rendering on Windows deployments. Not required for core functionality.

### Deployment Commands
Deploy the environment and install the required third-party libraries:

```bash
# Initialize the virtual environment

# On Windows (PowerShell: run as Administrator)
py -3.13 -m venv venv
.\venv\Scripts\Activate.ps1

# On Mac/Linux
python3.13 -m venv venv
source venv/bin/activate

# Install all third-party dependencies
pip install -r requirements.txt
```

> **Note:** On Windows, running PowerShell as Administrator is required for symbolic link support during extraction. Without it, iExtract will automatically fall back to copying files instead and display a warning.

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
```

> **Note:** Depending on your Python installation, you may need to use `python3` or `python3.13` instead of `python`.

## 6. Running Tests

To run the full test suite locally from the project root:

```bash
python -m unittest discover tests
```

Tests are also run automatically on every push or pull request via GitHub Actions. Results can be viewed in the **Actions** tab of the repository.

To add new tests, create a file in the `/tests/` directory following these conventions:
* Filename must start with `test_` and end with `.py`
* Any test data files must be placed in `/tests/test_data/`
* Test functions within the file must also start with `test_`

## 7. Packaging a Standalone Executable

iExtract can be packaged into a standalone executable for Windows, Linux, and macOS using PyInstaller. Each platform must be built natively: cross-compilation is not supported. Full packaging instructions are provided in the developer documentation (`documentation/iExtract-Developer-Documentation.md`).
