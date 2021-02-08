# born-digital-accessioner

A simple interface to create or update archival object records and create associated event records in bulk via the ArchivesSpace API. Written for [Yale Digital Accessioning Service (DAS)](https://guides.library.yale.edu/c.php?g=300384&p=3593184) workflows.

## Tutorial

The Born Digital Accessioner was designed to support the following workflow:

1. During physical processing of archival collections, archivists from special collections repositories across Yale document all digital media items in the DAS spreadsheet template.
2. Repository staff send the physical media and completed template to the Digital Accessioning Service. 
3. DAS staff perform assorted preservation actions, and add the type of action, the outcome, and the date performed to each row of the DAS spreadsheet template.
4. __DAS staff ingest the DAS spreadsheet into the Born Digital Accessioner, which either updates existing ArchivesSpace archival object records for the born digital materials, or creates new ones. In either case, event records are also created for each of the preservation actions performed by the Digital Accessioning Service.__

### Download application

Download the application and its supporting files either by entering `git clone https://github.com/ucancallmealicia/born-digital-accessioner` into your Terminal or Prompt, or by clicking the green Code button in the top left corner of the repository and selecting Download ZIP. Extract the folder and save it to your filesystem.

### Populate configuration file and data folders

The application takes a number of inputs from the user, which are managed in the included `data` folder in within the main application folder.

#### `config.json`

This file stores the user's ArchivesSpace login information. The user is only required to populate the the "api_username" and "api_password" fields. The other settings can be managed within the application. 

The "agent_authorizer" field is optional, and should only be populated when the person who was responsible for completing the PII scan or any other events listed on the spreadsheet is different from the person who is running the application. If this is the case, enter the first and last name of the implementer/authorizer in the "agent_authorizer" field - i.e "John Doe". Be sure before running the script that the implementer/authorizer has an agent record in ArchivesSpace.

#### `data/api_inputs`

Within the data folder is another folder entitled `api_inputs`. Place any completed DASS spreadsheets in this folder to access them within the application. If you add any new spreadsheets while the application is running, you can refresh your browser to see them in the app dropdown.

#### `data/json_backups`

Also within the data folder is a folder entitled `json_backups`. This folder stores backups created when existing ArchivesSpace records are updated by the application. 

To keep your backups organized, you should create a folder within the `json_backups` folder to store backups for each spreadsheet.

If you add new folders while the application is running, you can refresh your browser to see them in the app dropdown.

### Open application

The application can be run either by executing the `born-dig-accessioner.py` script in the Terminal, or by double-clicking on the appropriate executable. Windows users should double-click the `.exe` version and Mac users should double-click the unix executable.

A Terminal or Prompt window will open which indicates that the application is starting. Once you see the 'Debug mode: off' message, you can navigate to `http://127.0.0.1:8050/` in your browser to begin using the application.

__NOTE:__ The mechanism for packaging the applications and managing the various related files and folders is still being finalized. If Mac users are unable to start the application by clicking on the executable file, open a Terminal window, drag and drop the file into the window, and press 'return'.

__NOTE:__ This application is still in development, and runs on a development server. Once additional YUL staff members have tested the application it will be moved to a production-suitable server.

### Choose ArchivesSpace instance

The user can select an ArchivesSpace instance to work on by selecting one of the radio buttons. Per YAMS API best practices, updates must be run in DEV or TEST before running in PROD.

Only select 'Local' if you have a local instance of ArchivesSpace actively running on your computer.

### Select input source and output destination

Choose an input file by clicking the 'Select an input file' dropdown and highlighting your desired file. Be sure that you have added at least one spreadsheet to the 

Next, select your backup directory by clicking the 'Select a backup directory' dropdown and highlighting your desired directory. You do not have to select a backup directory if you are creating new ArchivesSpace records.

### Select action: `Create records` or `Update records`

The user chooses an action by clicking either the ‘Create records’ or ‘Update records’ buttons.

Sometimes repository staff will have already created archival object records in ArchivesSpace for born-digital materials. In these cases, the ArchivesSpace URL of each existing object should be listed on the DAS spreadsheet. Users click the 'Update Records' button to add metadata to these records, and to create event records related to DAS preservation actions.

If archival objects records don't already exist, the ArchivesSpace URL of the parent archival object record under which child archival objects records will be created should be listed on each row of the DAS spreadsheet. Users click the 'Create Records' button to create these new child records and their associated event records.

__NOTE:__ Archival object records can be created or updated even if no event data is present.

### Step 4: Review Outputs

While the script is running, the output logs will print to the browser window. These give a rough indication of the progress of the application, but please note that the formatting is still in development.

Once the script finishes, the user can review various outputs. A copy of the original spreadsheet data plus all new ArchivesSpace URIs is saved to the `/data/api_inputs` folder upon completion. The log files for the script are stored in the `/data/logs` folder. All JSON backups for updated ArchivesSpace records will be stored in a folder within the `data/json_backups` folder.

## Tips

If you intend to run more than one spreadsheet, refresh your browser to clear the on-screen logs and the current input. Trying to select a new spreadsheet without refreshing the browser may result in an error reading the configuration file (this bug is currently being addressed, but the cause of the issue is unclear).

## Troubleshooting

### Data Issues

The most common cause of errors is invalid data entered into the DAS spreadsheet template, such as:

* Incorrect formatting of extent types and events (requires the database value)
* Data in the wrong column
* Missing data
* Typos

Most of the time, when the program encounters an error it will move onto the next record without stopping, but this is not always the case. Check the log file if the program stops during execution.

### Bugs

If your data looks good and you’re still having issues, check the program log for detailed error reporting. If you find a bug please submit an issue!

## Questions?

[Email me](mailto:alicia.detelich@yale.edu)
