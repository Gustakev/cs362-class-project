# Team Resources

This document lists our team roles, links to project‑relevant artifacts, and our communication tools/policies, as required for CS 362.

---

## 1. Team Members & Roles

| Name | Role(s) | Description of Responsibilities |
|------|---------|--------------------------------|
| Kevin Gustafson | Director & Frontend Developer | Directs the project's overall direction and implements the agreed upon UI design. |
| Sam Daughtry | Backend Developer | Develops much of the program's functional logic. |
| Noah Gregie | UI/UX Designer | Mocks up the UI and helps code the UI and test it for usability and non-functional requirements. Helps code the app where needed. |
| Brendon Wong | QA Tester | Designs tests and tests many of the program's core functionalities with those tests. Fixes bugs if they are found. |

> Roles may evolve as the project progresses. Updates should be documented here.

---

## 2. Project Artifacts

Lists **every artifact** the team relies on: tools, documents, external resources, installation instructions, etc.

### **2.1 Development Tools**
- Programming language(s):
  - Python
- Frameworks & libraries:
  - sys
  - tkinter
- Required versions:
  - Python: 3.14+ (For compatibility with the newest features.)
  - sys: ?
  - tkinter: ?
- Installation notes:
  - Python:
    - Install Python from [here](https://www.python.org/downloads/).

### **2.2 Documents & Shared Resources**
- Requirements document:
  - N/A
- Architecture/design document:
  - [Temporary: Click Here](https://docs.google.com/document/d/1D1vTsdaMA0Npfb_yuyDox-kD976CTZfN947ZtuWGLDE/edit?tab=t.0).
- Living document:
  - [Click here](https://docs.google.com/document/d/1Mhivfg5L7h5X3cCTO7E5iUiXo8Poj--A-039OMgZ9fI/edit?tab=t.0).
- Mockups & diagrams:
  - N/A

### **2.3 External Tools & Services**
- Issue tracker (GitHub Issues):
  - We will be using these to track issues discovered while working on features -- issues that do not need to be considered major features themselves.
- Weekly progress reports in GitHub repo:
  - [Click here](https://github.com/Gustakev/cs362-class-project/tree/main/reports).
- CI/CD (GitHub Actions):
  - N/A
- Any APIs or datasets:
  - N/A
- AI Photo Captioning Tool:
  - [Click here](https://github.com/BrendxnW/photo-captioning).

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

- Why using Python fits the project:
  - Python: This language is great for quick development, without having to worry about low-level memory errors very much, making the chances of corrupting a user's backup lower than if we were to use something like C or C++. Though Python does run slower than C or C++, for a utility program like ours, this will not be an issue, as the runtime will surely be dominated by the extraction process itself.
- Why these libraries/frameworks:
  - sys: This allows us to handle errors correctly, returning errors to stderr.
  - tkinter: This allows us to trigger file explorer popups for various reasons throughout the program, which will post to the GUI of the OS, not to the command line, making the UX smoother. The main reason we chose this over other libraries is that it works on Windows, macOS, and Linux.
- Any tradeoffs or alternatives considered:
  - C++: C++ was considered, as many of us are well versed in it, with some of us being the strongest in it out of any language. However, picking C++ would open the floodgates to many kinds of errors we do not want to deal with in such a short development timeline. Additionally, for a program like ours, the performance gains would be minimal if we went with C++ over Python.
  - JS: JS was considered instead of Python due to how dynamic it is and how quick JS programs can run, as opposed to Python programs. However, we, as a team, are not as well versed in JS (and its oddities may introduce bugs that wouldn't come about while writing code in Python), so it lost the vote.

---

## 6. Updates Log

A simple place to track changes to this file.

| Date | Change | Author |
|------|--------|--------|
| 2026‑01‑30 | Initial version | Kevin Gustafson |
