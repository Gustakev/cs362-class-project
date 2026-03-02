<h1 align="center"><b>iExtract iOS Album to Folder Conversion Tool</b></h1>

<p align="center">
  <strong>iExtract Version 0.1.0-alpha.1</strong>
</p>
<p align="center">
  <img src="https://img.shields.io/badge/Python-3.13-blue?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Version-0.1.0--alpha.1-red">
  <img src="https://github.com/Gustakev/cs362-class-project/actions/workflows/ci.yml/badge.svg">

</p>

## Project Overview
iExtract makes it easy for iPhone users to extract their photos and videos from a local backup to somewhere else on their local storage without breaking album and collection structure or metadata. Instead of having to rely on expensive cloud subscriptions or confusing export workflows, iExtract preserves the original organization of a user's photos, without the bloat or cost of other monolithic apps.

## Table of Contents
- [Goal of Our App](#Goal-of-Our-App)
- [Repository Layout](#Repository-Layout)
- [Install](#Install)
- [Usage](#Usage)

## Goal of Our App
* Provide a fast and intuitive export process for iOS media using a backup as the source
* Preserve album/collection structure during exports
* Maintain metadata (dates, locations, file types, etc.)
* Reduce dependency on iCloud storage
* Avoid quality loss that typically occurs through compression of files during exports using other tools

## Repository Layout
- iExtract.py: The launcher for iExtract. In the future, this will include the ability to launch the app in CLI or Textual-based GUI mode. As of now, it just launches the CLI mode.

- README.md: The README file for iExtract.

- requirements.txt: The requirements file for iExtract, which makes it easy to install all the correct dependencies before running the program.

- team-resources.md: Describes the resources that the team uses, including relevant artifacts, libraries, etc.

- /.github/workflows/: Stores the workflow '.yml' file describing how continuous integration testing will be conducted.

- /cli_components/: Stores the code that runs the CLI for the application, accepting user interaction and calling logic from the 'functional_components' directory to accomplish a given goal.

- /dist/: (Coming Soon: Will be the location of releases, like 'iExtract.exe' for Windows.)

- /documentation/: Stores the user and developer documentation for iExtract.

- /functional_components/: Stores all our backend logic with all the features of our app.
  - /backup_locator_and_validator/:
    - /app/: Contains code relevant to the Application Layer of iExtract, the code that executes program logic, like value processing.
    - /data/: Contains code relevant to the Data Layer of iExtract, the code that reads/writes data.
    - /domain/: Contains the code relevant to the Domain Layer of iExtract, the data structures and definitions primarily utilized by this module.
  - /conversion_engine/:
    - /app/: Contains code relevant to the Application Layer of iExtract, the code that executes program logic, like value processing.
    - /data/: Contains code relevant to the Data Layer of iExtract, the code that reads/writes data.
    - /domain/: Contains the code relevant to the Domain Layer of iExtract, the data structures and definitions primarily utilized by this module.
  - /file_extraction_engine/:
    - /app/: Contains code relevant to the Application Layer of iExtract, the code that executes program logic, like value processing.
    - /data/: Contains code relevant to the Data Layer of iExtract, the code that reads/writes data.
    - /domain/: Contains the code relevant to the Domain Layer of iExtract, the data structures and definitions primarily utilized by this module.
  - /sql_cmd_facilitator/:
    - /app/: Contains code relevant to the Application Layer of iExtract, the code that executes program logic, like value processing.
    - /data/: Contains code relevant to the Data Layer of iExtract, the code that reads/writes data.
    - /domain/: Contains the code relevant to the Domain Layer of iExtract, the data structures and definitions primarily utilized by this module.

- /living_documents/: Stores each version of the project proposal document for our app that explains our app idea, along with all the requirements.

- /reports/: Holds weekly progress reports for our project. Each report contains a weekly status update from our TA and the individual contributions of each team member for that week.

- /tests/: Stores the test cases that are being used against the program.
  - /test_data/: Stores data for tests, if needed.

## Install

### **Build**
```bash
git clone https://github.com/Gustakev/cs362-class-project.git
cd cs362-class-project/
python -m venv venv

# If windows run:
source venv/Scripts/activate

# If Mac/Linux run:
source venv/bin/activate

pip install -r requirements.txt
```

### **Testing**
Tests are automatically run via GitHub Actions on every push and pull request.

To run tests locally:
```bash
python -m unittest discover tests
```

## Usage

**Use Case:** User exports all albums

Steps:
- Ensure that iCloud for your camera roll is not enabled (if it is enabled, your camera roll items won't be backed up), and then make an unencrypted backup of your iPhone using one of the following methods:
  - Windows:
    - Download and open iTunes.
    - Plug in your iPhone to your computer running Windows.
    - Ensure that your iPhone has "**Trust this computer**" enabled when prompted.
    - Approve access to the iPhone within iTunes when prompted (you may need to unlock the phone when iTunes states it is waiting for a response).
    - Click "**File**" in the toobar at the top of the screen.
    - Click "**Devices**".
    - Click "**Back Up**".
    - Wait for the backup to finish being made.
    - **Note the location of the backup** (the default location on Windows can be found by pressing ((Windows Key) + R) and entering `%AppData%`, and then entering `Roaming\Apple Computer\MobileSync\Backup`).
      - The folder that contains the backup will be the only one present inside the `Backup` folder.
  - macOS:
    - Plug in your iPhone to your Mac.
    - Open **Finder** (iTunes is no longer used for backups on macOS Catalina or later).
    - Select your iPhone from the sidebar under **Locations**.
    - Ensure that your iPhone has "**Trust this computer**" enabled when prompted.
    - In the **General** tab, look at the "Backups" section and ensure "**Encrypt local backup**" is **unchecked**.
    - Click "**Back Up Now**".
    - Wait for the backup to finish.
    - **Note the location of the backup:** You can find the folder by clicking "**Manage Backups...**" in the General tab, right-clicking your backup, and selecting "**Show in Finder**." (The manual path is `~/Library/Application Support/MobileSync/Backup/`).
  - Linux:
    - Open your terminal and install `libimobiledevice` (e.g., `sudo apt install libimobiledevice-utils` on Ubuntu/Debian).
    - Plug in your iPhone to your computer.
    - Ensure your iPhone has "**Trust this computer**" enabled when prompted.
    - Open a terminal and run `idevicepair pair` to confirm the connection.
    - Create a folder where you want the backup to live (e.g., `mkdir ~/iPhoneBackup`).
    - Run the command: `idevicebackup2 backup ~/iPhoneBackup`.
    - Wait for the terminal to indicate the backup is complete.
    - **Note the location of the backup:** The backup will be located in the folder you specified (in this example, `~/iPhoneBackup`), contained within a subfolder named after your device’s Unique Device ID (UDID).
    - **Quick Tip:** On Linux, if the device isn't recognized immediately, you might need to restart the `usbmuxd` service with `sudo systemctl restart usbmuxd`.

3. Start the progam by running the following command in your shell (Command Prompt, PowerShell, Bash, Terminal, etc.):
```bash
   python iExtract.py
```
- Note: The command may differ depending on the Python setup installed on your machine. You may instead need to enter `python3`, `python3.13`, `python3.14`, etc., or you may need to start Python by providing the path to the executable itself if none of these methods work. We recommend adding `python` to your system's path environment variable to prevent this issue from occurring.
