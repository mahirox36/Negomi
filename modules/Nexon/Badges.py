#TODO: Badges Editor
#TODO: Inputs: Image, Title, Description, How to obtain it. 
#TODO: Output: JsonFile and the Assets to the Assets Folder

import os
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QFormLayout, QLabel,
    QLineEdit, QTextEdit, QPushButton, QFileDialog, QWidget, QMessageBox
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt


class BadgeEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Badge Editor")
        self.setGeometry(100, 100, 600, 500)
        self.setStyleSheet("font-family: Arial; font-size: 14px;")
        
        # Main layout
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout(self.main_widget)

        # Form for badge inputs
        self.form_layout = QFormLayout()
        self.layout.addLayout(self.form_layout)

        # Input Fields
        self.image_label = QLabel("No Image Selected")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("border: 1px solid gray;")
        self.image_label.setFixedHeight(150)
        self.form_layout.addRow("Image:", self.image_label)

        self.image_button = QPushButton("Upload Image")
        self.image_button.clicked.connect(self.upload_image)
        self.form_layout.addRow("", self.image_button)

        self.title_input = QLineEdit()
        self.form_layout.addRow("Title:", self.title_input)

        self.description_input = QTextEdit()
        self.form_layout.addRow("Description:", self.description_input)

        self.obtain_input = QLineEdit()
        self.form_layout.addRow("How to Obtain:", self.obtain_input)

        # Save Button
        self.save_button = QPushButton("Save Badge")
        self.save_button.clicked.connect(self.save_badge)
        self.layout.addWidget(self.save_button)

        # Internal data
        self.image_path = None
        self.output_folder = "Assets/Badges/"
        os.makedirs(self.output_folder, exist_ok=True)

    def upload_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "", "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_path:
            self.image_path = file_path
            pixmap = QPixmap(file_path).scaled(150, 150, Qt.KeepAspectRatio)
            self.image_label.setPixmap(pixmap)

    def save_badge(self):
        title = self.title_input.text().strip()
        description = self.description_input.toPlainText().strip()
        obtain = self.obtain_input.text().strip()

        if not title or not description or not obtain or not self.image_path:
            QMessageBox.warning(self, "Missing Data", "Please fill in all fields.")
            return

        # Save the image to the Assets folder
        image_name = f"{title} Badge.{os.path.basename(self.image_path.split(".")[-1])}"
        saved_image_path = os.path.join(self.output_folder, image_name)
        with open(self.image_path, "rb") as src, open(saved_image_path, "wb") as dest:
            dest.write(src.read())

        # Save badge data to JSON
        badge_data = {
            "title": title,
            "description": description,
            "how_to_obtain": obtain,
            "image": f"Assets/{image_name}",
        }
        json_file = os.path.join(self.output_folder, "badges.json")
        if os.path.exists(json_file):
            with open(json_file, "r") as file:
                data = json.load(file)
        else:
            data = []

        data.append(badge_data)
        with open(json_file, "w") as file:
            json.dump(data, file, indent=4)

        QMessageBox.information(self, "Success", "Badge saved successfully!")
        self.clear_inputs()

    def clear_inputs(self):
        self.image_label.clear()
        self.image_label.setText("No Image Selected")
        self.title_input.clear()
        self.description_input.clear()
        self.obtain_input.clear()
        self.image_path = None


# class 

if __name__ == "__main__":
    app = QApplication([])
    window = BadgeEditor()
    window.show()
    app.exec()
