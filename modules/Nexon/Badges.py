from dataclasses import dataclass, field
from typing import Optional, Union, Dict, Callable, List
from enum import Enum
import json
import os
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QFormLayout, QLabel,
    QLineEdit, QTextEdit, QPushButton, QFileDialog, QWidget, QMessageBox,
    QComboBox, QSpinBox
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from nextcord import User, Member, Message, Interaction
import re
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .Users import UserData

class RequirementType(Enum):
    MESSAGE_COUNT = "message_count"
    COMMAND_USE = "command_use"
    REACTION_RECEIVED = "reaction_received"
    REACTION_GIVEN = "reaction_given"
    GIF_SENT = "gif_sent"
    EMOJI_USED = "emoji_used"
    CUSTOM_EMOJI_USED = "custom_emoji_used"
    ATTACHMENT_SENT = "attachment_sent"
    MENTION_COUNT = "mention_count"
    LINK_SHARED = "link_shared"
    CONTENT_MATCH = "content_match"
    CHANNEL_ACTIVITY = "channel_activity"

@dataclass
class BadgeRequirement:
    type: RequirementType
    value: int = 1
    specific_value: str = ""  # For specific commands, emojis, or content matches
    
    def to_dict(self) -> dict:
        return {
            "type": self.type.value,
            "value": self.value,
            "specific_value": self.specific_value
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'BadgeRequirement':
        return cls(
            type=RequirementType(data["type"]),
            value=data["value"],
            specific_value=data.get("specific_value", "")
        )

@dataclass
class Badge:
    title: str
    description: str
    image_path: str
    requirements: List[BadgeRequirement]
    points: int = 0
    
    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "description": self.description,
            "image_path": self.image_path,
            "requirements": [req.to_dict() for req in self.requirements],
            "points": self.points
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Badge':
        return cls(
            title=data["title"],
            description=data["description"],
            image_path=data["image_path"],
            requirements=[BadgeRequirement.from_dict(req) for req in data["requirements"]],
            points=data.get("points", 0)
        )

class BadgeEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enhanced Badge Editor")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("font-family: Arial; font-size: 14px;")
        
        self.init_ui()
        
    def init_ui(self):
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout(self.main_widget)
        
        self.form_layout = QFormLayout()
        self.layout.addLayout(self.form_layout)
        
        # Basic Badge Info
        self.setup_basic_info()
        
        # Requirements Section
        self.setup_requirements_section()
        
        # Save Button
        self.save_button = QPushButton("Save Badge")
        self.save_button.clicked.connect(self.save_badge)
        self.layout.addWidget(self.save_button)
        
        self.output_folder = "Assets/Badges/"
        os.makedirs(self.output_folder, exist_ok=True)
    
    def setup_basic_info(self):
        # Image Selection
        self.image_label = QLabel("No Image Selected")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("border: 1px solid gray;")
        self.image_label.setFixedHeight(150)
        self.form_layout.addRow("Image:", self.image_label)
        
        self.image_button = QPushButton("Upload Image")
        self.image_button.clicked.connect(self.upload_image)
        self.form_layout.addRow("", self.image_button)
        
        # Basic Info Fields
        self.title_input = QLineEdit()
        self.form_layout.addRow("Title:", self.title_input)
        
        self.description_input = QTextEdit()
        self.form_layout.addRow("Description:", self.description_input)
        
        self.points_input = QSpinBox()
        self.points_input.setRange(0, 1000)
        self.form_layout.addRow("Points:", self.points_input)
    
    def setup_requirements_section(self):
        # Requirements Section
        self.requirements_layout = QVBoxLayout()
        self.requirements = []
        
        # Add Requirement Button
        self.add_req_button = QPushButton("Add Requirement")
        self.add_req_button.clicked.connect(self.add_requirement)
        self.layout.addWidget(self.add_req_button)
        
        self.layout.addLayout(self.requirements_layout)
        
    def add_requirement(self):
        req_widget = QWidget()
        req_layout = QFormLayout(req_widget)
        
        # Requirement Type
        type_combo = QComboBox()
        for req_type in RequirementType:
            type_combo.addItem(req_type.value)
        
        # Value Input
        value_input = QSpinBox()
        value_input.setRange(1, 10000)
        
        # Specific Value Input
        specific_value_input = QLineEdit()
        specific_value_input.setPlaceholderText("e.g., command name, emoji, or content to match")  # Fixed method name
        
        # Remove Button
        remove_button = QPushButton("Remove")
        remove_button.clicked.connect(lambda: self.remove_requirement(req_widget))
        
        req_layout.addRow("Type:", type_combo)
        req_layout.addRow("Value:", value_input)
        req_layout.addRow("Specific:", specific_value_input)
        req_layout.addRow("", remove_button)
        
        self.requirements_layout.addWidget(req_widget)
        self.requirements.append((type_combo, value_input, specific_value_input))
    
    def remove_requirement(self, widget):
        widget.deleteLater()
        self.requirements = [(t, v, s) for (t, v, s) in self.requirements 
                           if t.parent().parent() != widget]

    def upload_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "", "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_path:
            self.image_path = file_path
            pixmap = QPixmap(file_path).scaled(150, 150, Qt.KeepAspectRatio)
            self.image_label.setPixmap(pixmap)

    def save_badge(self):
        if not hasattr(self, 'image_path'):
            QMessageBox.warning(self, "Missing Image", "Please select an image.")
            return
            
        title = self.title_input.text().strip()
        description = self.description_input.toPlainText().strip()
        points = self.points_input.value()
        
        if not title or not description:
            QMessageBox.warning(self, "Missing Data", "Please fill in all fields.")
            return
        
        if not self.requirements:
            QMessageBox.warning(self, "No Requirements", "Please add at least one requirement.")
            return
        
        # Save image
        image_name = f"{title.lower().replace(' ', '_')}_badge.{self.image_path.split('.')[-1]}"
        saved_image_path = os.path.join(self.output_folder, image_name)
        with open(self.image_path, "rb") as src, open(saved_image_path, "wb") as dest:
            dest.write(src.read())
        
        # Create requirements list
        requirements = []
        for type_combo, value_input, specific_value_input in self.requirements:
            req = BadgeRequirement(
                type=RequirementType(type_combo.currentText()),
                value=value_input.value(),
                specific_value=specific_value_input.text().strip()
            )
            requirements.append(req.to_dict())
        
        # Create badge data
        badge_data = {
            "title": title,
            "description": description,
            "image_path": f"Assets/Badges/{image_name}",
            "requirements": requirements,
            "points": points
        }
        
        # Save to JSON
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
        self.points_input.setValue(0)
        
        # Clear requirements
        for widget in self.findChildren(QWidget):
            if widget.parent() == self.requirements_layout.parent():
                widget.deleteLater()
        self.requirements.clear()

class BadgeManager:
    def __init__(self, user_data: 'UserData'):
        self.user_data = user_data
        self.badges = self.load_badges()
    
    def load_badges(self) -> Dict[str, Badge]:
        try:
            with open("Assets/Badges/badges.json", "r") as f:
                data = json.load(f)
                return {badge_data["title"]: Badge.from_dict(badge_data) 
                        for badge_data in data}
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def check_requirement(self, req: BadgeRequirement, message: Optional[Message | Interaction] = None) -> bool:
        if req.type == RequirementType.MESSAGE_COUNT:
            return self.user_data.total_messages >= req.value
        elif req.type == RequirementType.REACTION_RECEIVED:
            return self.user_data.reactions_received >= req.value
        elif req.type == RequirementType.REACTION_GIVEN:
            return self.user_data.reactions_given >= req.value
        elif req.type == RequirementType.ATTACHMENT_SENT:
            return self.user_data.attachments_sent >= req.value
        elif req.type == RequirementType.MENTION_COUNT:
            return self.user_data.mentions_count >= req.value
        elif req.type == RequirementType.LINK_SHARED:
            return self.user_data.links_shared >= req.value
        elif req.type == RequirementType.CHANNEL_ACTIVITY:
            return self.user_data.preferred_channels.get(req.specific_value, 0) >= req.value
        elif req.type == RequirementType.COMMAND_USE:
                cmd_name = req.specific_value.lower()
                return self.user_data.favorite_commands.get(cmd_name, 0) >= req.value
        
        # Handle requirements that need message context
        if isinstance(message, Message):
            if req.type == RequirementType.GIF_SENT:
                if message.attachments:
                    return any(att.filename.lower().endswith(('.gif', '.gifv')) for att in message.attachments)
                return any(url for url in re.findall(r'https?://\S+', message.content) if url.lower().endswith(('.gif', '.gifv')))

            elif req.type == RequirementType.EMOJI_USED:
                emoji_pattern = r'[\U0001F300-\U0001F9FF]|[\u2600-\u26FF\u2700-\u27BF]'
                if req.specific_value:
                    return req.specific_value in message.content
                emojis_in_msg = len(re.findall(emoji_pattern, message.content))
                return emojis_in_msg >= req.value

            elif req.type == RequirementType.CUSTOM_EMOJI_USED:
                custom_emoji_pattern = r'<:\w+:\d+>'
                if req.specific_value:
                    return f":{req.specific_value}:" in message.content
                custom_emojis = len(re.findall(custom_emoji_pattern, message.content))
                return custom_emojis >= req.value

            elif req.type == RequirementType.CONTENT_MATCH:
                if not req.specific_value:
                    return False
                try:
                    pattern = re.compile(req.specific_value, re.IGNORECASE)
                    return bool(pattern.search(message.content))
                except re.error:
                    # Fallback to simple string matching if regex is invalid
                    return req.specific_value.lower() in message.content.lower()
        return False

    def check_badges(self, message: Optional[Message | Interaction] = None) -> List[Badge]:
        earned_badges = []
        for badge in self.badges.values():
            if badge.title not in self.user_data.badges:
                requirements_met = True
                for req in badge.requirements:
                    if not self.check_requirement(req, message):
                        requirements_met = False
                        break
                
                if requirements_met:
                    earned_badges.append(badge)
                    self.user_data.badges.add(badge.title)
                    self.user_data.reputation += badge.points

        return earned_badges

if __name__ == "__main__":
    app = QApplication([])
    window = BadgeEditor()
    window.show()
    app.exec_()