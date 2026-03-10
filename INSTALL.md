<h1 align="center">iExtract Installation</h1>

## Prerequisites
- Python 3.13+
- Git

## Installation

1. Open your terminal and clone the repo:
```bash
git clone https://github.com/Gustakev/cs362-class-project.git
```

2. Move into the repo:
```bash
cd cs362-class-project
```

3. Start a virtual environment:
```bash
# On Windows (PowerShell: run as Administrator)
py -3.13 -m venv venv
.\venv\Scripts\Activate.ps1

# On Mac/Linux
python3.13 -m venv venv
source venv/bin/activate
```

> **Note:** On Windows, running as Administrator is required for symbolic link support. On Linux, if `python3-tk` is not installed, run `sudo apt install python3-tk` before proceeding.

4. Install the required dependencies:
```bash
pip install -r requirements.txt
```

> **Important:** Keep this terminal open. Closing it will end the virtual environment session. If you close the terminal accidentally, re-navigate to the repo folder and re-run the activation command in step 3 before running the program again.

5. Start the program:
```bash
python iExtract.py
```

> **Note:** Depending on your Python installation, you may need to use `python3` or `python3.13` instead of `python`.

## Verify Installation

If the installation was successful, the program will display a launcher menu prompting you to choose between the Standard CLI and the Textual Dashboard (Beta). Both modes have equivalent features, but the basic CLI is more stable.
