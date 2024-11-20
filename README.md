# Minimal EMR Management System Application

This application allows case managers to track and manage patient data locally.

How to Use:
1. Extract the ZIP file.
2. Run the application by double-clicking the executable:
   - Windows: `emr_app.exe`
   - macOS/Linux: `emr_app`

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
pyinstaller --onefile --noconsole --hidden-import=Pillow --hidden-import=PyQt5.QtChart emr_app.py

## License

This project is licensed under the MIT License.

## Contact

For any inquiries, please contact marcinknara@gmail.com.
