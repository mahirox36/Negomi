import json
import shutil
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
from contextlib import contextmanager

class DataManager:
    """A unified data management class for handling JSON data storage with enhanced features."""
    
    def __init__(self,
                 name: str,
                 server_id: Optional[int] = None,
                 file: str = "data",
                 subfolder: Optional[str] = None,
                 default: Union[Dict, List, None] = None,
                 auto_save: bool = True):
        """
        Initialize the DataManager.
        
        Args:
            name: The name of the data store
            server_id: Optional server ID for guild-specific data
            file: Name of the JSON file (without extension)
            subfolder: Optional subfolder path
            default: Default data structure
            auto_save: Whether to auto-save on context exit
        """
        # Construct the path
        base_path = Path("Data")
        path_parts = [name]
        if server_id is not None:
            path_parts.append(str(server_id))
        if subfolder:
            path_parts.append(subfolder)
        
        self.path = base_path.joinpath(*path_parts)
        self.file = self.path / f"{file}.json"
        self.default = default if default is not None else {}
        self.data = self.default
        self.auto_save = auto_save
        
        
        # Load existing data
        self.load()

    def save(self) -> None:
        """Save data to JSON file."""
        self.path.mkdir(parents=True, exist_ok=True)
        with open(self.file, "w", encoding='utf-8') as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    def load(self) -> Union[Dict, List, Any]:
        """Load data from JSON file."""
        try:
            with open(self.file, "r", encoding='utf-8') as f:
                self.data = json.load(f)
            return self.data
        except FileNotFoundError:
            self.data = self.default
            return self.default

    def delete(self, key: Optional[str] = None) -> None:
        """Delete data or specific key."""
        if key is not None:
            if key in self.data:
                del self.data[key]
                self.save()
        else:
            if self.file.exists():
                self.file.unlink()
            if not any(self.path.iterdir()):
                shutil.rmtree(self.path)

    def get(self, key: Any, default: Any = None) -> Any:
        """Get value from data with optional default."""
        if isinstance(self.data, dict):
            return self.data.get(key, default)
        elif isinstance(self.data, (list, tuple)):
            return key if key in self.data else default
        return default

    def set(self, key: str, value: Any) -> None:
        """Set value in data."""
        self.data[key] = value
        
    def update(self, data: Dict) -> None:
        """Update data with dictionary."""
        if isinstance(self.data, dict):
            self.data.update(data)
    def append(self, data: Any) -> None:
        """Update data with dictionary."""
        if isinstance(self.data, list):
            self.data.append(data)


    def exists(self) -> bool:
        """Check if data file exists."""
        return self.file.exists()

    @contextmanager
    def transaction(self):
        """Context manager for batch operations."""
        try:
            yield self
        finally:
            if self.auto_save:
                self.save()

    def __getitem__(self, key: str) -> Any:
        """Get item using dictionary syntax."""
        return self.data[key]

    def __setitem__(self, key: str, value: Any) -> None:
        """Set item using dictionary syntax."""
        self.data[key] = value

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self.auto_save:
            self.save()
        return False

    def __len__(self):
        """Get length of data."""
        return len(self.data)

    def __str__(self):
        """String representation."""
        return f"DataManager(path='{self.file}')"
