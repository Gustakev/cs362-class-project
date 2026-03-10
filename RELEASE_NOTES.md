## What's New in 1.0.0
- Full iPhone backup extraction preserving collection (user and non-user album) structure in terms of folders
- Export all collections or a single specific collection using the menu options
- Blacklist/whitelist support for filtering collections (allows the user to export a subset of collections)
- HEIC → JPG and MOV → MP4 conversion engine (converts these file types and saves up to 25% extraction storage cost, at the cost of significantly more runtime overhead)
  - Optional: can be enabled or disabled in Settings. Both conversion options are off by default.
- Symlink support for non-exclusive assets (Windows requires launching the terminal in Admin or Developer Mode before using any shell in a way that will allow this to work, e.g., use Command Prompt, PowerShell, or Git Bash)
  - Enabled by default: can be disabled in Settings.
- Textual TUI as a beta alternative to the Standard CLI (feature parity achieved)
- Photo Descriptor (stretch goal) demo feature implemented with several sample photos

## Installation
From the repo root, see `INSTALL.md` for full setup instructions.
- If confused, refer to `documentation/iExtract-User-Documentation.md`

## Working Features
All major features (excluding the Photo Descriptor demo) listed above are fully functional. See the living document (`living_documents/CS 362 - Project Living Document.md`) for full use-case details.

## Known Issues
See open issues: https://github.com/Gustakev/cs362-class-project/issues?q=is:open