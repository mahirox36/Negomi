import asyncio
from dataclasses import dataclass, field
from typing import Optional, Dict, List
from enum import Enum
import json
import os
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QFormLayout, QLabel,
    QLineEdit, QTextEdit, QPushButton, QFileDialog, QWidget, QMessageBox,
    QComboBox, QSpinBox
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from nexon import Message, Interaction
import re
from typing import TYPE_CHECKING
try:
    from .utils import extract_emojis
except: 
    pass
if TYPE_CHECKING:
    from .Users import UserData
    

class RequirementType(Enum):
    MESSAGE_COUNT = "message_count"
    MESSAGE_SENT = "message_sent"
    COMMAND_USE = "command_use"
    REACTION_RECEIVED = "reaction_received"
    REACTION_GIVEN = "reaction_given"
    GIF_SENT = "gif_sent"
    EMOJI_USED = "emoji_used"
    CUSTOM_EMOJI_USED = "custom_emoji_used"
    ATTACHMENT_SENT = "attachment_sent"
    MENTION_COUNT = "mention_count"
    UNIQUE_MENTION_COUNT = "unique_mention_count"
    LINK_SHARED = "link_shared"
    CONTENT_MATCH = "content_match"
    CHANNEL_ACTIVITY = "channel_activity"
    TIME_BASED = "time_based"
    OWNER_INTERACTION = "owner_interaction"
    INACTIVE_DURATION = "inactive_duration"
    # MESSAGE_RATE = "message_rate"
    UNIQUE_EMOJI_COUNT = "unique_emoji_count"
    SPECIFIC_EMOJI = "specific_emoji"
    # REVIVAL = "revival"
    ALL_COMMANDS = "all_commands"

class ComparisonType(Enum):
    EQUAL = "equal"
    GREATER = "greater"
    LESS = "less"
    GREATER_EQUAL = "greater_equal"
    LESS_EQUAL = "less_equal"

@dataclass
class BadgeRequirement:
    type: RequirementType
    value: int = 1
    specific_value: str = ""
    comparison: ComparisonType = ComparisonType.GREATER_EQUAL  # Default to >= for backwards compatibility
    
    def to_dict(self) -> dict:
        return {
            "type": self.type.value,
            "value": self.value,
            "specific_value": self.specific_value,
            "comparison": self.comparison.value
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'BadgeRequirement':
        return cls(
            type=RequirementType(data["type"]),
            value=data["value"],
            specific_value=data.get("specific_value", ""),
            comparison=ComparisonType(data.get("comparison", "greater_equal"))
        )

    def compare(self, actual_value: int, second_value:Optional[int] = None) -> bool:
        if second_value:
            if self.comparison == ComparisonType.EQUAL:
                return actual_value == second_value
            elif self.comparison == ComparisonType.GREATER:
                return actual_value > second_value
            elif self.comparison == ComparisonType.LESS:
                return actual_value < second_value
            elif self.comparison == ComparisonType.GREATER_EQUAL:
                return actual_value >= second_value
            elif self.comparison == ComparisonType.LESS_EQUAL:
                return actual_value <= second_value
            return False
        if self.comparison == ComparisonType.EQUAL:
            return actual_value == self.value
        elif self.comparison == ComparisonType.GREATER:
            return actual_value > self.value
        elif self.comparison == ComparisonType.LESS:
            return actual_value < self.value
        elif self.comparison == ComparisonType.GREATER_EQUAL:
            return actual_value >= self.value
        elif self.comparison == ComparisonType.LESS_EQUAL:
            return actual_value <= self.value
        return False


#TODO: instead of creating new id it get the id of the emojis (need to change in the settings)
@dataclass
class Badge:
    id: int
    title: str
    description: str
    image_path: str
    # emoji: str
    requirements: List[BadgeRequirement]
    points: int = 0
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "image_path": self.image_path,
            # "emoji": self.emoji,
            "requirements": [req.to_dict() for req in self.requirements],
            "points": self.points
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Badge':
        return cls(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            image_path=data["image_path"],
            # emoji=data["emoji"],
            requirements=[BadgeRequirement.from_dict(req) for req in data["requirements"]],
            points=data.get("points", 0)
        )

class BadgeEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Badge Editor")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("font-family: Arial; font-size: 14px;")
        self.badge_manager = BadgeManager(None)
        self.init_ui()
    def get_next_badge_id(self) -> int:
        """Get the next available badge ID."""
        if not self.badge_manager.badges:
            return 1 
        max_id = max(badge.id for badge in self.badge_manager.badges.values())
        return max_id + 1
        
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
        self.emoji_input = QTextEdit()
        self.form_layout.addRow("Emoji:", self.emoji_input)
        
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
        
        # Comparison Type
        comparison_combo = QComboBox()
        for comp_type in ComparisonType:
            comparison_combo.addItem(comp_type.value)
        
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
        req_layout.addRow("Comparison:", comparison_combo)
        req_layout.addRow("Value:", value_input)
        req_layout.addRow("Specific:", specific_value_input)
        req_layout.addRow("", remove_button)
        
        self.requirements_layout.addWidget(req_widget)
        self.requirements.append((type_combo, comparison_combo, value_input, specific_value_input))
    
    def remove_requirement(self, widget):
        widget.deleteLater()
        self.requirements = [(t, c, v, s) for (t, c, v, s) in self.requirements 
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
        emoji = self.emoji_input.toPlainText().strip()
        points = self.points_input.value()
        
        if not title or not description:
            QMessageBox.warning(self, "Missing Data", "Please fill in all fields.")
            return
        
        if not self.requirements:
            QMessageBox.warning(self, "No Requirements", "Please add at least one requirement.")
            return
        
        badge_id = self.get_next_badge_id()  
        # Save image
        image_name = f"{title.lower().replace(' ', '_')}_badge.{self.image_path.split('.')[-1]}"
        saved_image_path = os.path.join(self.output_folder, image_name.replace("/", " "))
        with open(self.image_path, "rb") as src, open(saved_image_path, "wb") as dest:
            dest.write(src.read())
        
        # Create requirements list
        requirements = []
        for type_combo, comparison_combo, value_input, specific_value_input in self.requirements:
            req = BadgeRequirement(
                type=RequirementType(type_combo.currentText()),
                value=value_input.value(),
                specific_value=specific_value_input.text().strip(),
                comparison=ComparisonType(comparison_combo.currentText())
            )
            requirements.append(req.to_dict())
        
        # Create badge data
        badge_data = {
            "id": badge_id,
            "title": title,
            "description": description,
            "emoji": emoji,
            "image_path": f"Assets/Badges/{image_name.replace("/", " ")}",
            "requirements": requirements,
            "points": points
        }
        
        # Save to JSON
        json_file = os.path.join(self.output_folder, "badges.json")
        if os.path.exists(json_file):
            with open(json_file, "r", encoding="utf-8") as file:
                data = json.load(file)
        else:
            data = []
        
        data.append(badge_data)
        with open(json_file, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        
        QMessageBox.information(self, "Success", "Badge saved successfully!")
        self.clear_inputs()

    def clear_inputs(self):
        self.image_label.clear()
        self.image_label.setText("No Image Selected")
        self.title_input.clear()
        self.description_input.clear()
        self.emoji_input.clear()
        self.points_input.setValue(0)
        
        # Clear requirements
        for widget in self.findChildren(QWidget):
            if widget.parent() == self.requirements_layout.parent():
                widget.deleteLater()
        self.requirements.clear()

class BadgeManager:
    def __init__(self, user_data: Optional['UserData']):
        self.user_data = user_data
        self.badges = self.load_badges()
    
    def load_badges(self) -> Dict[str, Badge]:
        try:
            with open("Assets/Badges/badges.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                return {badge_data["title"]: Badge.from_dict(badge_data) 
                        for badge_data in data}
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    async def check_requirement(self, req: BadgeRequirement, message: Optional[Message | Interaction] = None) -> bool:
        def check_numeric_requirement(actual_value: int) -> bool:
            return req.compare(actual_value)

        if req.type == RequirementType.MESSAGE_COUNT:
            return check_numeric_requirement(self.user_data.total_messages)
        elif req.type == RequirementType.REACTION_RECEIVED:
            return check_numeric_requirement(self.user_data.reactions_received)
        elif req.type == RequirementType.REACTION_GIVEN:
            return check_numeric_requirement(self.user_data.reactions_given)
        elif req.type == RequirementType.ATTACHMENT_SENT:
            return check_numeric_requirement(self.user_data.attachments_sent)
        elif req.type == RequirementType.MENTION_COUNT:
            return check_numeric_requirement(self.user_data.mentions_count)
        elif req.type == RequirementType.UNIQUE_MENTION_COUNT:
            return check_numeric_requirement(len(self.user_data.unique_users_mentioned))
        elif req.type == RequirementType.LINK_SHARED:
            return check_numeric_requirement(self.user_data.links_shared)
        elif req.type == RequirementType.CHANNEL_ACTIVITY:
            return check_numeric_requirement(self.user_data.preferred_channels.get(req.specific_value, 0))
        elif req.type == RequirementType.COMMAND_USE:
                cmd_name = req.specific_value.lower()
                return check_numeric_requirement(self.user_data.favorite_commands.get(cmd_name, 0))
        elif req.type == RequirementType.TIME_BASED:
            current_time = datetime.now()
            try:
                time_pattern = r'(\d{1,2}):(\d{2})\s*(AM|PM)?'
                match = re.match(time_pattern, req.specific_value.strip().upper())
                if not match:
                    return False
                
                hour, minute, meridiem = match.groups()
                hour = int(hour)
                minute = int(minute)
                
                if meridiem:
                    if meridiem == 'PM' and hour != 12:
                        hour += 12
                    elif meridiem == 'AM' and hour == 12:
                        hour = 0
                
                current_minutes = current_time.hour * 60 + current_time.minute
                target_minutes = hour * 60 + minute
                return req.compare(current_minutes, target_minutes)
            except ValueError:
                return False
        
        if isinstance(message, Message):
            if req.type == RequirementType.GIF_SENT:
                return req.compare(self.user_data.gif_sent, req.value)
            
            elif req.type == RequirementType.OWNER_INTERACTION:
                # return message.author.id == int(req.specific_value)
                if message.reference:
                    cachedMessage = message.reference.cached_message
                    messageReferenced = cachedMessage if cachedMessage else await message.channel.fetch_message(message.reference.message_id)
                else: return False
                return messageReferenced.author.id == 829806976702873621
            
            elif req.type == RequirementType.UNIQUE_EMOJI_COUNT:
                emoji_count = len(set(extract_emojis(message.content)))
                return check_numeric_requirement(emoji_count)
            
            elif req.type == RequirementType.SPECIFIC_EMOJI:
                emojisExtracted = extract_emojis(req.specific_value)
                return any(emoji in message.content for emoji in emojisExtracted)
            elif req.type == RequirementType.INACTIVE_DURATION:
                future_time = self.user_data.last_updated + timedelta(hours=float(req.value))
                if future_time < datetime.now():
                    return True
                else: 
                    return False
                
            
            elif req.type == RequirementType.MESSAGE_SENT:
                return True
            
            elif req.type == RequirementType.EMOJI_USED:
                emoji_pattern = r'[\U0001F300-\U0001F9FF]|[\u2600-\u26FF\u2700-\u27BF]'
                emojisExtracted = extract_emojis(message.content)
                if req.specific_value:
                    return set(list(req.specific_value)) & set(emojisExtracted)
                emojis_in_msg = len(re.findall(emoji_pattern, message.content))
                return check_numeric_requirement(emojis_in_msg)

            elif req.type == RequirementType.CUSTOM_EMOJI_USED:
                custom_emoji_pattern = r'<:\w+:\d+>'
                if req.specific_value:
                    return f":{req.specific_value}:" in message.content
                custom_emojis = len(re.findall(custom_emoji_pattern, message.content))
                return check_numeric_requirement(custom_emojis)

            elif req.type == RequirementType.CONTENT_MATCH:
                if not req.specific_value:
                    return False
                try:
                    pattern = re.compile(req.specific_value, re.IGNORECASE)
                    return bool(pattern.search(message.content.lower()))
                except re.error:
                    # Fallback to simple string matching if regex is invalid
                    return req.specific_value.lower() in message.content.lower()
        elif isinstance(message, Interaction):
            if req.type == RequirementType.ALL_COMMANDS:
                total_commands = len(message.client.get_application_commands())
                used_commands = len(self.user_data.favorite_commands)
                return total_commands == used_commands
        return False

    async def check_badges(self, message: Optional[Message | Interaction] = None) -> List[Badge]:
        earned_badges = []
        for badge in self.badges.values():
            if badge.id not in self.user_data.badges:
                requirements_met = all(await asyncio.gather(*(self.check_requirement(req, message) for req in badge.requirements)))
                if requirements_met:
                    earned_badges.append(badge)
                    self.user_data.badges.add(badge.id)
                    self.user_data.reputation += badge.points
        return earned_badges

if __name__ == "__main__":
    app = QApplication([])
    window = BadgeEditor()
    window.show()
    app.exec_()