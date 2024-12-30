# Minimal EMR Management System Application

This application allows case managers to track and manage patient data locally.

HOW TO USE:

On Windows:
1. Download {APP_NAME}_windows.zip file
2. Unzip downloaded file

On MAC:
1. Download {APP_NAME}_macos.tar.gz file
2. In the terminal, go to the directory where you downloaded the file
3. Run this command 
```
tar -xzvf {APP_NAME}_macos.tar.gz
```

HOW TO BUILD:

On Windows:
1. Go to the app directory
2. Delete build, dist, {APP_NAME}.spec directories/files
3. Run this command
```
 pyinstaller --onefile --noconsole --clean --windowed  --name CaseManager --icon=assets/casemanager_icon.ico emr_app.py
```
4. After that ZIP dist directory and name of this ZIP should be {APP_NAME}_windows.zip

On MAC:
1. Go to the app directory
2. Run this command
```
pyinstaller --onefile --noconsole --clean --windowed  --name CaseManager --icon=assets/casemanager_icon.ico emr_app.py
```
3. After that run these commands:
```
cd dist
```
```
tar -czvf CaseManager.tar.gz CaseManager.app
```


Features:
- Add/Edit/Delete patients.
- Manage weekly data for each patient.
- Export patient data and charts to Excel files.

Dependencies:
- JSON files (`patients.json`, `questions.json`, `patient_data.json`) must remain in the same directory as the application.

Enjoy using the EMR Application!

## Technical ReadMe Below

This application is a minimal EMR (Electronic Medical Records) management system designed to handle patient cases. It stores all the data locally and is run using Python.

## Features

- Manage patient records
- Store data locally
- Simple and minimalistic design

## Requirements

- Python 3.x

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/marcinknara/minimal-emr.git
    ```
2. Navigate to the project directory:
    ```bash
    cd minimal-emr
    ```

## Usage

Run the application:
```bash
python emr_app.py
```

## Build
pyinstaller --onefile --noconsole --clean --windowed  --name CaseManager --icon=assets/casemanager_icon.ico emr_app.py


## License

This project is licensed under the MIT License.

## Contact

For any inquiries, please contact marcinknara@gmail.com.
