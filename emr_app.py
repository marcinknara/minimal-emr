import sys
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, 
    QTableWidget, QTableWidgetItem, QMessageBox, QHBoxLayout, QCheckBox
)
from PyQt5.QtChart import QChart, QChartView, QLineSeries
from PyQt5.QtCore import Qt
import os
from PyQt5.QtWidgets import QFileDialog
from openpyxl import Workbook
from openpyxl.drawing.image import Image
import tempfile

DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

class EMRManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EMR System")
        self.setGeometry(100, 100, 900, 600)
        
        # Main layout
        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout()
        
        # Table to display patients
        self.patient_table = QTableWidget()
        self.patient_table.setColumnCount(4)
        self.patient_table.setHorizontalHeaderLabels(["ID", "Name", "Age", "Data"])
        self.main_layout.addWidget(self.patient_table)
        
        # Connect cellChanged signal to handle table edits
        self.patient_table.cellChanged.connect(self.update_patient_data)
        
        # Load patient data
        self.patients = self.load_patients()
        self.populate_table()

        # Buttons
        add_button = QPushButton("Add Patient")
        add_button.clicked.connect(self.add_patient)
        self.main_layout.addWidget(add_button)
        
        delete_button = QPushButton("Delete Patient")
        delete_button.clicked.connect(self.delete_patient)
        self.main_layout.addWidget(delete_button)
        
        # export_button = QPushButton("Export Patient Data")
        # export_button.clicked.connect(self.export_data)
        # self.main_layout.addWidget(export_button)
        
        # Set up the main widget
        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)
        
        # Menu for settings
        self.menu_bar = self.menuBar()
        settings_menu = self.menu_bar.addMenu("Settings")
        
        # Add Edit Data button to settings
        edit_data_action = settings_menu.addAction("Edit Data")
        edit_data_action.triggered.connect(self.open_edit_data_screen)
        
        # Load questions
        self.questions = self.load_questions()

    def load_patients(self):
        try:
            path = get_resource_path("patients.json")
            print(f"Loading patients from: {path}")  # Debugging information
            if not os.path.exists(path):
                with open(path, "w") as file:
                    json.dump([], file, indent=4)
                    print("Created new patients.json file.")  # Debugging information
            with open(path, "r") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            QMessageBox.warning(self, "Error", f"Failed to load patients: {str(e)}")
            return []
    
    def save_patients(self):
        try:
            with open(get_resource_path("patients.json"), "w") as file:
                json.dump(self.patients, file, indent=4)
        except IOError as e:
            QMessageBox.critical(self, "Error", f"Failed to save patients: {str(e)}")

    def populate_table(self):
        """Populate the patient table."""
        self.patient_table.blockSignals(True)
        self.patient_table.setRowCount(0)
        for i, patient in enumerate(self.patients):
            try:
                self.patient_table.insertRow(i)
                id_item = QTableWidgetItem(str(patient.get("id", i + 1)))
                id_item.setFlags(Qt.ItemIsEnabled)
                self.patient_table.setItem(i, 0, id_item)

                name_item = QTableWidgetItem(patient.get("name", f"Patient {i + 1}"))
                name_item.setFlags(name_item.flags() | Qt.ItemIsEditable)
                self.patient_table.setItem(i, 1, name_item)

                age_item = QTableWidgetItem(str(patient.get("age", 30)))
                age_item.setFlags(age_item.flags() | Qt.ItemIsEditable)
                self.patient_table.setItem(i, 2, age_item)

                data_button = QPushButton("Data")
                data_button.clicked.connect(lambda _, p=patient: self.open_data_screen(p))
                self.patient_table.setCellWidget(i, 3, data_button)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Error populating patient row {i}: {str(e)}")
        self.patient_table.blockSignals(False)
    
    def update_patient_data(self, row, column):
        """Update the patient data based on table edits."""
        try:
            if column == 1:  # Name column
                self.patients[row]["name"] = self.patient_table.item(row, column).text().strip()
                if not self.patients[row]["name"]:
                    raise ValueError("Name cannot be empty.")
            elif column == 2:  # Age column
                age = int(self.patient_table.item(row, column).text().strip())
                if age <= 0:
                    raise ValueError("Age must be a positive number.")
                self.patients[row]["age"] = age
            self.save_patients()
        except ValueError as e:
            QMessageBox.warning(self, "Invalid Input", str(e))
            self.populate_table()  # Revert invalid input
    
    def add_patient(self):
        """Add a new patient."""
        new_patient = {
            "id": len(self.patients) + 1,
            "name": f"New Patient {len(self.patients) + 1}",
            "age": 30,
            "records": {}
        }
        self.patients.append(new_patient)
        self.save_patients()
        self.populate_table()

    def save_questions_from_settings(self, updated_questions):
        """Save updated questions from the settings screen."""
        self.questions = updated_questions  # Update the in-memory list of questions
        self.save_questions()  # Save the questions to the JSON file

    def save_questions(self):
        with open(get_resource_path("questions.json"), "w") as file:
            json.dump(self.questions, file, indent=4)
    
    def delete_patient(self):
        """Delete the selected patient."""
        selected_row = self.patient_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a patient to delete.")
            return
        
        # Confirm deletion
        patient_name = self.patient_table.item(selected_row, 1).text()
        confirmation = QMessageBox.question(
            self, 
            "Confirm Deletion", 
            f"Are you sure you want to delete patient '{patient_name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirmation == QMessageBox.No:
            return
        
        del self.patients[selected_row]
        
        # Reassign IDs to maintain sequence
        for i, patient in enumerate(self.patients):
            patient["id"] = i + 1
        
        self.save_patients()
        self.populate_table()
    
    
    def load_questions(self):
        path = get_resource_path("questions.json")
        if not os.path.exists(path):
            default_questions = [
                {"text": "Question 1", "type": "Quantitative"},
                {"text": "Question 2", "type": "Qualitative"},
            ]
            with open(path, "w") as file:
                json.dump(default_questions, file, indent=4)
        with open(path, "r") as file:
            return json.load(file)  
    
    def open_data_screen(self, patient):
        """Open the Data screen for the selected patient."""
        self.data_window = DataScreen(patient, self.questions)
        self.data_window.show()
    
    def open_edit_data_screen(self):
        """Open the Edit Data screen."""
        self.edit_data_window = EditDataScreen(
            self.questions, 
            self.save_questions_from_settings  # Pass the method as a callback
        )
        self.edit_data_window.show()

    # def export_data(self):
    #     """Export patient data to a file."""
    #     print("Export patient data to CSV/Excel/PDF")

def get_resource_path(filename):
    """Get the absolute path to the resource file in the resources folder."""
    if getattr(sys, 'frozen', False):  # Running as a PyInstaller bundle
        base_path = os.path.dirname(sys.executable)  # Directory of the executable
    else:
        base_path = os.path.abspath(".")  # Current working directory for development

    # Ensure the resources directory exists
    resources_path = os.path.join(base_path, "resources")
    os.makedirs(resources_path, exist_ok=True)

    # Return the path to the specific file inside the resources folder
    return os.path.join(resources_path, filename)

class DataScreen(QWidget):
    def __init__(self, patient, questions):
        super().__init__()
        self.setWindowTitle(f"Data for {patient['name']}")
        self.setGeometry(100, 100, 800, 600)
        
        self.patient = patient  # Patient's reference
        self.questions = questions  # Questions list
        
        # Load existing patient data
        self.patient_data = self.load_patient_data()
        
        # Main layout
        layout = QVBoxLayout()
        
        # Table for weekly data input
        self.data_table = QTableWidget()
        self.data_table.setColumnCount(6)  # Question + 5 days (Monday to Friday)
        self.data_table.setHorizontalHeaderLabels(["Question", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
        self.populate_table()
        layout.addWidget(self.data_table)
        
        # Chart for quantitative data
        self.chart = QChart()
        self.chart_view = QChartView(self.chart)
        layout.addWidget(self.chart_view)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_data)
        button_layout.addWidget(save_button)
        
        export_button = QPushButton("Export to Excel")
        export_button.clicked.connect(self.export_to_excel)
        button_layout.addWidget(export_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Update the chart initially
        self.update_chart()
    
    def populate_table(self):
        """Populate the data table with weekly inputs."""
        self.data_table.setRowCount(0)
        for i, question in enumerate(self.questions):
            self.data_table.insertRow(i)
            
            # Question Name (non-editable)
            question_item = QTableWidgetItem(question["text"])
            question_item.setFlags(Qt.ItemIsEnabled)  # Make it non-editable
            self.data_table.setItem(i, 0, question_item)
            
            # Weekly data inputs (editable)
            for j, day in enumerate(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], start=1):
                value = self.patient_data.get(question["text"], {}).get(day, "")
                day_item = QTableWidgetItem(str(value))
                self.data_table.setItem(i, j, day_item)
    
    def save_data(self):
        """Save weekly data for the patient."""
        try:
            for row in range(self.data_table.rowCount()):
                question = self.data_table.item(row, 0).text()
                self.patient_data[question] = {}
                for col, day in enumerate(DAYS_OF_WEEK, start=1):
                    item = self.data_table.item(row, col)
                    value = item.text() if item else ""
                    self.patient_data[question][day] = value
            self.save_patient_data()
            QMessageBox.information(self, "Saved", "Patient data has been updated.")
            self.update_chart()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save data: {str(e)}")
            print(f"Error in save_data: {e}")  # Debugging information
        
        # Save the data to the file
        self.save_patient_data()
        QMessageBox.information(self, "Saved", "Patient data has been updated.")
        
        # Update the chart with new data
        self.update_chart()
    
    def update_chart(self):
        """Update the line chart with quantitative data."""
        self.chart.removeAllSeries()
        
        for question in self.questions:
            if question["type"] == "Quantitative":
                # Create a series for the question
                series = QLineSeries()
                series.setName(question["text"])
                
                # Add data points for Monday to Friday
                weekly_data = self.patient_data.get(question["text"], {})
                for i, day in enumerate(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]):
                    try:
                        value = float(weekly_data.get(day, 0) or 0)
                    except ValueError:
                        value = 0  # Handle non-numeric values gracefully
                    series.append(i, value)
                
                self.chart.addSeries(series)
        
        # Configure the chart
        self.chart.createDefaultAxes()
        self.chart.setTitle("Quantitative Data (Weekly)")
        self.chart.legend().setVisible(True)
    
    def load_patient_data(self):
        """Load existing patient data for the specific patient."""
        try:
            path = get_resource_path("patient_data.json")
            if os.path.exists(path):
                with open(path, "r") as file:
                    all_data = json.load(file)
                    return all_data.get(str(self.patient["id"]), {})  # Load only this patient's data
            else:
                return {}
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load patient data: {str(e)}")
            print(f"Error loading patient data: {e}")  # Debugging information
            return {}

    
    def save_patient_data(self):
        """Save the patient's data to a persistent file."""
        try:
            path = get_resource_path("patient_data.json")
            all_data = {}
            
            # Load existing data if file exists
            if os.path.exists(path):
                with open(path, "r") as file:
                    all_data = json.load(file)
            
            # Update this patient's data
            all_data[str(self.patient["id"])] = self.patient_data
            
            # Write back to file
            with open(path, "w") as file:
                json.dump(all_data, file, indent=4)
            print(f"Saved patient data for ID {self.patient['id']} to {path}")  # Debugging information
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save patient data: {str(e)}")
            print(f"Error saving patient data: {e}")  # Debugging information
    
    def export_to_excel(self):
        try:
            # Ask for a save location for the Excel file
            save_path, _ = QFileDialog.getSaveFileName(
                self, "Save File", f"{self.patient['name']}_data.xlsx", "Excel Files (*.xlsx)"
            )
            if not save_path:
                return

            # Create a temporary directory for the chart image
            temp_dir = tempfile.gettempdir()
            chart_image_path = os.path.join(temp_dir, f"{self.patient['name']}_chart.png")

            # Create Excel workbook
            wb = Workbook()
            ws = wb.active
            ws.title = f"Data for {self.patient['name']}"

            ws.append(["Patient Name:", self.patient["name"]])
            ws.append(["Patient Age:", self.patient["age"]])
            ws.append([])

            # Add headers
            ws.append(["Question"] + DAYS_OF_WEEK)

            for question, weekly_data in self.patient_data.items():
                row = [question]
                for day in DAYS_OF_WEEK:
                    row.append(weekly_data.get(day, ""))
                ws.append(row)

            # Add chart image
            try:
                chart_pixmap = self.chart_view.grab()
                chart_pixmap.save(chart_image_path)
                img = Image(chart_image_path)
                ws.add_image(img, "H2")
            except Exception as e:
                QMessageBox.warning(self, "Warning", f"Failed to add chart image: {str(e)}")

            # Save the Excel file
            wb.save(save_path)
            QMessageBox.information(self, "Exported", f"Data exported to {save_path}.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export data: {str(e)}")
        finally:
            # Clean up temporary files
            if os.path.exists(chart_image_path):
                os.remove(chart_image_path)


class EditDataScreen(QWidget):
    def __init__(self, questions, save_questions_callback):
        super().__init__()
        self.setWindowTitle("Edit Data Points")
        self.setGeometry(100, 100, 600, 400)
        
        # Store references
        self.questions = questions
        self.save_questions_callback = save_questions_callback
        
        # Main layout
        layout = QVBoxLayout()
        
        # Table for displaying questions
        self.question_table = QTableWidget()
        self.question_table.setColumnCount(2)
        self.question_table.setHorizontalHeaderLabels(["Question", "Type"])
        self.populate_table()
        layout.addWidget(self.question_table)
        
        # Buttons for adding and deleting questions
        button_layout = QHBoxLayout()
        add_button = QPushButton("Add")
        add_button.clicked.connect(self.add_question)
        button_layout.addWidget(add_button)
        
        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(self.delete_question)
        button_layout.addWidget(delete_button)
        
        layout.addLayout(button_layout)
        
        # Save button
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_questions)
        layout.addWidget(save_button)
        
        self.setLayout(layout)
    
    def populate_table(self):
        """Populate the table with current questions."""
        self.question_table.setRowCount(0)
        for i, question in enumerate(self.questions):
            self.question_table.insertRow(i)
            
            # Question text (editable)
            question_item = QTableWidgetItem(question["text"])
            question_item.setFlags(question_item.flags() | Qt.ItemIsEditable)
            self.question_table.setItem(i, 0, question_item)
            
            # Checkbox for type
            checkbox = QCheckBox("Quantitative")
            checkbox.setChecked(question["type"] == "Quantitative")
            checkbox.setToolTip("Check for Quantitative, Uncheck for Qualitative")
            self.question_table.setCellWidget(i, 1, checkbox)
    
    def add_question(self):
        """Add a new question."""
        new_question = {"text": "New Question", "type": "Quantitative"}
        self.questions.append(new_question)
        self.populate_table()
    
    def delete_question(self):
        """Delete the selected question."""
        selected_row = self.question_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a question to delete.")
            return
        
        question_text = self.question_table.item(selected_row, 0).text()
        confirmation = QMessageBox.question(
            self, 
            "Confirm Deletion", 
            f"Are you sure you want to delete the question '{question_text}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirmation == QMessageBox.Yes:
            del self.questions[selected_row]
            self.populate_table()
    
    def save_questions(self):
        """Save the changes to the questions."""
        # Update questions list from the table
        self.questions.clear()
        for row in range(self.question_table.rowCount()):
            question_text = self.question_table.item(row, 0).text()
            checkbox = self.question_table.cellWidget(row, 1)
            question_type = "Quantitative" if checkbox.isChecked() else "Qualitative"
            self.questions.append({"text": question_text, "type": question_type})
        
        # Save updated questions using the callback
        self.save_questions_callback(self.questions)
        QMessageBox.information(self, "Saved", "Data points have been updated successfully.")
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EMRManager()
    window.show()
    sys.exit(app.exec_())