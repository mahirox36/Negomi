import os
import sys
from pathlib import Path
from typing import Optional
import requests
import subprocess
from dataclasses import dataclass
from .Nexon import logger

@dataclass
class Version:
    major: int
    minor: int
    patch: int
    
    @classmethod
    def from_string(cls, version_str: str) -> 'Version':
        major, minor, patch = map(int, version_str.split('.'))
        return cls(major, minor, patch)
    
    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"
    
    def __gt__(self, other: 'Version') -> bool:
        return (self.major, self.minor, self.patch) > (other.major, other.minor, other.patch)

class AutoUpdater:
    def __init__(self, github_owner: str, github_repo: str, current_version: str):
        self.github_owner = github_owner
        self.github_repo = github_repo
        self.current_version = Version.from_string(current_version)
        self.logger = logger  # Using your existing logger
        
        # Create temp directory for downloads
        self.temp_dir = Path("temp")
        self.temp_dir.mkdir(exist_ok=True)
        
    def check_for_updates(self) -> bool:
        """Check if a new version is available."""
        try:
            # Get latest release info from GitHub
            url = f"https://api.github.com/repos/{self.github_owner}/{self.github_repo}/releases/latest"
            response = requests.get(url)
            response.raise_for_status()
            
            latest = response.json()
            latest_version = Version.from_string(latest['tag_name'].lstrip('v').split("-")[0])
            
            return latest_version > self.current_version
            
        except Exception as e:
            self.logger.error(f"Failed to check for updates: {e}")
            return False
    
    def download_update(self) -> Optional[Path]:
        """Download the latest release."""
        try:
            # Get latest release
            url = f"https://api.github.com/repos/{self.github_owner}/{self.github_repo}/releases/latest"
            response = requests.get(url)
            response.raise_for_status()
            
            latest = response.json()
            
            # Find the exe asset
            exe_asset = next(
                (asset for asset in latest['assets'] if asset['name'].endswith('.exe')),
                None
            )
            
            if not exe_asset:
                self.logger.error("No exe found in latest release")
                return None
                
            # Download the exe
            download_url = exe_asset['browser_download_url']
            exe_path = self.temp_dir / exe_asset['name']
            
            response = requests.get(download_url, stream=True)
            response.raise_for_status()
            
            with open(exe_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    
            return exe_path
            
        except Exception as e:
            self.logger.error(f"Failed to download update: {e}")
            return None
    
    def apply_update(self, new_exe_path: Path) -> bool:
        """Apply the update by replacing the current exe after process exits."""
        if not new_exe_path.exists():
            return False

        try:
            current_exe = Path(sys.executable).resolve()
            current_pid = os.getpid()

            # Create update script in the same directory as the executable
            update_script = current_exe.parent / "update.bat"

            self.logger.info(f"Creating update script at: {update_script}")

            # Create the batch script with full paths
            script_content = f'''@echo off
echo Waiting for process {current_pid} to end...
:loop
tasklist | find "{current_pid}" >nul
if not errorlevel 1 (
    timeout /t 1 /nobreak >nul
    goto loop
)
echo Process ended, applying update...
move /y "{new_exe_path.resolve()}" "{current_exe}"
if errorlevel 1 (
    echo Failed to move file
    pause
    exit /b 1
)
echo Starting new version...
start "" "{current_exe}"
echo Cleaning up...
del "%~f0"
'''

            # Write the script with UTF-8 encoding
            with open(update_script, 'w', encoding='utf-8') as f:
                f.write(script_content)

            self.logger.info("Update script created, executing...")

            # Execute the batch file with proper working directory
            process = subprocess.Popen(
                [str(update_script)],
                shell=True,
                cwd=str(current_exe.parent),
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )

            self.logger.info("Update process started, shutting down current instance...")

            # Exit current process
            sys.exit(0)

        except Exception as e:
            self.logger.error(f"Failed to apply update: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to apply update: {e}")
            return False