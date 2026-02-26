# iExtract iOS Album to Folder Conversion Tool

### iExtract Version 0.1.0-alpha.1

## Project Overview
iExtract makes it easy for iPhone users to extract their photos and videos from a local backup to somewhere else on their local storage without breaking album and collection structure or metadata. Instead of having to rely on expensive cloud subscriptions or confusing export workflows, iExtract preserves the original organization of a user's photos, without the bloat or cost of other monolithic apps.

## Goal of Our App
* Provide a fast and intuitive export process for iOS media using a backup as the source
* Preserve album/collection structure during exports
* Maintain metadata (dates, locations, file types, etc.)
* Reduce dependency on iCloud storage
* Avoid quality loss that typically occurs through compression of files during exports using other tools

## Respository Layout
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
