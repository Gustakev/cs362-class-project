- In this directory, indiviual components will have their own directories, named using the snake case convention.

- Within each of those directories, there will be subdirectories, also named using snake case, that represent the 3 relevant layers of the component (excluding the Presentation Layer, which is the command line interface):
  - The Application Layer (app): Contains functions that communicate with the Data Layer and the Domain Layer, as well as the command line interface (Presentation Layer), facilitating the component's functional logic, e.g., transforming raw data from the Data Layer into a data structure that was defined within the Domain Layer.
  - The Data Layer (data): Contains functions that operate on data.
  - The Domain Layer (domain): Contains data structure definitions and "business logic."