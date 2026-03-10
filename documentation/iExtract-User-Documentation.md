**iExtract User Documentation**

**Project Overview**

This program allows users to export their iPhone photo albums locally without requiring a paid subscription, while preserving original file structure and metadata. This gives users full ownership and offline access to their personal media.

**System Requirements**

* **Supported OSes**  
* Microsoft Windows 10/11 32-bit or 64-bit  
* Linux 32-bit or 64-bit  
* macOS 32-bit or 64-bit

  *Disclaimer:* Whether a system using a certain OS will run this program depends on whether it has a shell and terminal and whether Python 3.13 supports the system. There are no guarantees of functionality offered for rare OSes or rare OS distros.

**How to Install**

1. **Clone repo**  
   1. In the terminal (using the shell of your choice) run the command:  
      \`git clone https://github.com/Gustakev/cs362-class-project.git\`    
2. **Move to repo location**  
   1. In the terminal, run the command:  \`cd cs362-class-project\`  
3. **Install Python**  
   1. Install Python 3.13+ for your system from this link: [https://www.python.org/downloads/](https://www.python.org/downloads/)  
4. **Initialize virtual environment**  
   1. In the terminal, run the command: \`python \-m venv venv\`  
   2. Note: If the above command, or any other command prefixed with ‘python’ fails, ensure that you have a Python path variable set on your system. It may either be ‘python’, ‘python3’, or something more specific like ‘python3.13’, depending on your installation.  
5. **Activate virtual environment**  
   1. If your machine is running Mac or Linux, in the terminal, run the command:  
      \`source venv/bin/activate\`   
   2. If you have a Windows machine, in administrator PowerShell, run the command: \`.\\venv\\Scripts\\Activate.ps1\`   
6. **Install requirements**  
   1. In the terminal, run the command: \`pip install \-r requirements.txt\`  
   2. **Note:** Some Linux users may need to run the command: \`sudo apt install python3-tk\` in order to obtain a working installation of ‘tkinter’.  
7. **How to deactivate the virtual environment**  
   1. Enter \`deactivate\` into the terminal. 

**How to Run the Software**

In the terminal run the command:  \`python iExtract.py\`   The program will prompt a command-line interface in the terminal.

**How to Use the Software**

	**iExtract Launcher Menu:**

- Choose the CLI Mode or the Textual UI Mode (Both modes are equivalent in features — the Textual UI mode is just more intuitive.)

	**iExtract Main Menu:**

- **Option 1: Load iPhone Backup Folder**  
  Allows the user to select and load an unencrypted iPhone backup (of a phone running iOS 26+) directory from their local machine. The system scans and validates the backup. The user must only select this option, provide a path to the backup, and then wait.  
- **Option 2: Export All Camera Roll Media**  
  Exports all photos and videos from the user’s camera roll to a local folder while preserving original file structure and metadata (e.g., timestamps). The user must select which folder to extract their collections to, start the extraction process, and then wait.  
- **Option 3: Export Specific Camera Roll Media**  
  Allows users to select and export specific albums or subsets of media from their camera roll. The user must check which collections from the backup they would like to extract, where they would like them to go, start the extraction, and wait.  
- **Option 4: Settings (Work in Progress)**  
  Provides configuration options such as conversion options, an option to exclude all media that is marked as hidden in the . Additional settings and customization options are planned. The user must enter this menu, select the correct submenu, e.g., ‘Conversion Settings’, and set up the extraction however they would like to.  
- **Option 5: Help (Work in Progress)**  
  Links to the User Documentation (this document) and the Developer Documentation. **Future Plans:** Provides a list of FAQs and answers, along with helpful tips. The user must simply select this menu option, the ‘Tips’ option or the ‘FAQs’ option, and return to the main menu once they are satisfied with the information obtained.  
- **Option 6: Report Bug (Work in Progress)**  
  Allows users to submit bug reports for issues encountered while using the program. Users may select this menu option, open the link to the project repo’s issues page, and submit an issue.  
- **Option 7: Photo Descriptor (Beta Demo / WIP)**  
  Currently allows users to step through a few example photos to explore the functionality of our image descriptor which will be fully implemented in the future, so that users on headless systems can determine the contents of images (and videos, in the future) within their extractions, instead of having no idea what they have extracted.  
- **Option 8: Restart (Work in Progress)**  
  Safely restarts the application.  
- **Option 9: Quit**  
  Safely exits the application.

**How to Report a Bug**

Users can report bugs through the in-app “Report Bug” option, which will link to the project’s GitHub issue tracker: [https://github.com/Gustakev/cs362-class-project/issues](https://github.com/Gustakev/cs362-class-project/issues). When submitting a bug report, users should include the following:

* Which feature had the issue  
* What action they were attempting  
* What they expected to happen  
* What actually happened

**Known Bugs or Limitations:** Known bugs or limitations should be documented in the bug tracker. A user testing the implemented use case(s) should not encounter trivial bugs (e.g., NPEs) or a large number of bugs that are unlisted in the bug tracker.

- **Bugs:**  
  * [GitHub Issue Tracker: Bugs](https://github.com/Gustakev/cs362-class-project/issues?q=state%3Aopen%20label%3Abug)  
- **Limitations:**  
  * No major limitations at this time, beyond limited device support confirmation.