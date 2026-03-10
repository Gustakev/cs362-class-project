# Team Resources

This document lists our team roles, links to project‑relevant artifacts, and our communication tools/policies, as required for CS 362.

---

## 1. Team Members & Roles

| Name | Role(s) | Description of Responsibilities |
|------|---------|--------------------------------|
| Kevin Gustafson | Director & Backend Developer | Directs the project's overall direction and implements much of the core extraction and backend logic. |
| Sam Daughtry | Backend Developer | Develops much of the program's functional logic. |
| Noah Gregie | UI/UX Designer & Frontend Developer | Mocks up the UI and implements both the Standard CLI and the Textual Dashboard interface. Tests for usability and non-functional requirements. |
| Brendon Wong | QA Tester & ML Developer | Designs tests and tests many of the program's core functionalities with those tests. Fixes bugs if they are found. Develops and trains the AI photo captioning model. |

> Roles may evolve as the project progresses. Updates should be documented here.

---

## 2. Project Artifacts

Lists **every artifact** the team relies on: tools, documents, external resources, installation instructions, etc.

### **2.1 Development Tools**
- Programming language(s):
  - Python
- Frameworks & libraries:
  - **sys** — Standard library. Used for error handling (stderr) and clean exits.
  - **tkinter** — Standard library. Used to trigger native OS file explorer dialogs for folder selection.
  - **plistlib** — Standard library. Used to parse Apple `.plist` files from iPhone backups (device info, manifest).
  - **sqlite3** — Standard library. Used to query `Photos.sqlite` and `Manifest.db` from iPhone backups.
  - **pydantic** — Used to define and validate all domain data models (assets, albums, backup metadata, etc.).
  - **Pillow** — Used for image processing and HEIC/JPG conversion.
  - **pillow-heif** — Extends Pillow with HEIC/HEIF format support, required for reading Apple's native image format.
  - **imageio-ffmpeg** — Bundles a self-contained ffmpeg binary used by the conversion engine for MOV → MP4 transcoding.
  - **requests** — Used by the photo captioning component to call the AI model inference endpoint.
  - **textual** — Terminal UI framework used to implement the Textual Dashboard (Beta) interface.
- Required versions:
  - Python: **3.13** (3.14 has known pydantic compatibility issues with PyInstaller builds)
  - pydantic: >= 2.0.0
  - Pillow: >= 10.0.0
  - pillow-heif: >= 0.18.0
  - textual: >= 0.50.0
  - moviepy: >= 2.0.0 (listed in requirements; ffmpeg is preferred for actual conversion)
  - imageio-ffmpeg: latest
  - requests: latest
- Installation notes:
  - Python:
    - Install Python 3.13 from [here](https://www.python.org/downloads/). On Windows, check "Add to PATH" during installation.
  - All Python dependencies:
    - Run `pip install -r requirements.txt` from the project root inside a virtual environment.
  - Linux only — system-level dependency required before pip install:
    - `sudo apt install libheif-dev`
  - macOS only — system-level dependency required before pip install:
    - `brew install libheif` (requires [Homebrew](https://brew.sh))

### **2.2 Documents & Shared Resources**
- Requirements document:
  - N/A
- Architecture/design document:
  - [Temporary: Click Here](https://docs.google.com/document/d/1D1vTsdaMA0Npfb_yuyDox-kD976CTZfN947ZtuWGLDE/edit?tab=t.0).
- Living document:
  - Located at `/living_documents/` in the repository.
  - [Click here](https://docs.google.com/document/d/1Mhivfg5L7h5X3cCTO7E5iUiXo8Poj--A-039OMgZ9fI/edit?tab=t.0).
  
- Mockups & diagrams:
  - Program Flow Diagram:
    - [Click here](https://oregonstateuniversity-my.sharepoint.com/:u:/g/personal/gustafke_oregonstate_edu/IQBgmBfGjFt0Q5smIIyV4imhAdqkP3baczqTaU_koUTAxiw?e=CP3WyP).
- Developer Documentation:
  - Located at `/documentation/` in the repository.
  - [Click here](https://docs.google.com/document/d/1b_GKadfXZ3BhCbaBva2A9yGD2T_0b9aMbPcIgIuJqG4/edit?tab=t.0).
- User Documentation:
  - Located at `/documentation/` in the repository.
  - [Click here](https://docs.google.com/document/d/15Wjz9xbFSsDllAze02nyUA3Hoh9634gyACuPZ-2v-9Y/edit?tab=t.0).
- Beta Testing Feedback:
  - Located at `/beta-testing/` in the repository.

### **2.3 External Tools & Services**
- Issue tracker (GitHub Issues):
  - We use GitHub Issues to track bugs and minor tasks discovered during development.
- Weekly progress reports in GitHub repo:
  - [Click here](https://github.com/Gustakev/cs362-class-project/tree/main/reports).
- CI/CD (GitHub Actions):
  - Automated test suite runs on every push and pull request to the repository via GitHub Actions, using `unittest`. Status badge visible in the README.
- Packaging (PyInstaller):
  - iExtract is packaged into a standalone executable for Windows, Linux, and macOS using PyInstaller. An `iExtract.spec` file is present in the repo root reflecting the current build configuration. See the developer documentation for full build instructions.
- AI Photo Captioning Component:
  - [Click here](https://github.com/BrendxnW/image-captioning-cnn-lstm). A CNN-LSTM model trained to generate natural language captions for photos. Integrated into iExtract as a beta demo feature (Photo Descriptor).
- Any APIs or datasets:
  - N/A

---

## 3. Communication Channels & Policies

### **3.1 Synchronous Communication**
- Platform:
  - Primary: Microsoft Teams
  - Personal communications: Text or Discord
- Purpose: Enables quick communication between peers, so that we do not get stumped during development while waiting for someone to respond to a question.
- Expected response time: **20 minutes to 3 hours**
- Notes: These are always the preferred methods of communication when possible.

### **3.2 Asynchronous Communication**
- Platform: OSU Email
- Purpose: Enables communication between the team and other people who primarily use email addresses for communication. Also, enables team members to send and receive content via email.
- Expected response time: **9-12 hours**
- Notes: This is not the preferred method of communication.

### **3.3 Meeting Schedule**
- In‑class project meetings: **Tuesdays & Thursdays after lecture**
- Additional team meetings: **Wednesdays (3 PM)**
- Attendance expectations: **Must attend, unless you have an acceptable excuse**

### **3.4 Communication Norms**
- How decisions are made:
  - Project direction: Ask about and discuss the purpose of the app and what must be functional by certain dates in order to stay on track.
- How tasks are assigned: Based on the role of each person, tasks are assigned in a predictable manner.
- How blockers are reported: People write what is blocking them, both in the progress report for the week and in the Teams chat to tell the team.
- Conflict resolution expectations: Communicate differences and time conflicts early and, if you can't, try to make up for it later.

---

## 4. Version Control & Repository Practices

- Branching strategy: Branches will be designated by the feature name they are being made for in this format: "main-menu-dev".
- Commit message conventions: Say what has been done and why.
- Code review expectations: Ensure that bad practices are caught early, so that technical debt doesn't build.
- Who merges pull requests: Anyone may merge pull requests, as long as the conflicts have been resolved first.

---

## 5. Toolset Rationale

Briefly explaining **why** our team chose the languages, frameworks, and tools that we did.

- **Python** — Great for quick development without low-level memory management concerns, reducing the risk of corrupting a user's backup. While slower than C or C++, runtime for a utility like ours is dominated by the extraction process itself, making the performance difference negligible.
- **tkinter** — Allows native OS file explorer dialogs on Windows, macOS, and Linux without external dependencies. Chosen over alternatives for its cross-platform reliability.
- **pydantic** — Provides runtime data validation and clean model definitions throughout the app, catching malformed backup data early and keeping domain structures well-typed and self-documenting.
- **Pillow + pillow-heif** — Required combination for handling Apple's HEIC/HEIF image format. Pillow provides the base image processing; pillow-heif extends it with HEIC support, which is the default format for modern iPhones.
- **imageio-ffmpeg** — Self-contained ffmpeg binary that bundles with the app. Chosen over requiring the user to install ffmpeg separately, enabling MOV → MP4 conversion out of the box with no additional setup.
- **textual** — Chosen to implement the optional Textual Dashboard UI. Provides a rich terminal-based interface with widgets, layouts, and reactive state — all without requiring a traditional GUI framework. Gives users a more visual option while still being terminal-native.
- **requests** — Lightweight HTTP library used by the photo captioning component to call the inference endpoint. No alternatives were seriously considered given its ubiquity for this use case.
- **sqlite3** — Standard library. Used to query `Photos.sqlite` (Apple's photo library database) and `Manifest.db` (the backup file index). No third-party ORM is needed given the read-only, query-specific nature of the access.
- Any tradeoffs or alternatives considered:
  - **C++**: Was considered given team familiarity, but the risk of memory errors and the short development timeline made Python the safer choice. Performance gains would be minimal for this type of utility.
  - **JS**: Was considered for its dynamic nature and speed relative to Python, but the team is less fluent in JS and its quirks could introduce bugs that Python wouldn't. Lost the vote.
  - **moviepy**: Is listed in requirements and was the original video conversion library used. Replaced in practice by a direct ffmpeg subprocess approach via imageio-ffmpeg, which is more reliable and faster for MOV → MP4 conversion.

---

## 6. Updates Log

A simple place to track changes to this file.

| Date | Change | Author |
|------|--------|--------|
| 2026‑01‑30 | Initial version | Kevin Gustafson |
| 2026‑03‑09 | Updated libraries, roles, CI/CD status, packaging tools, photo captioning repo link, and toolset rationale to reflect current project state | Kevin Gustafson |