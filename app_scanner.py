import winreg
import os
import logging
from typing import List, Dict, Optional

class AppScanner:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def _read_registry(self, hive, reg_path) -> List[Dict[str, str]]:
        apps = []
        try:
            with winreg.OpenKey(hive, reg_path) as key:
                for i in range(winreg.QueryInfoKey(key)[0]):
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        with winreg.OpenKey(key, subkey_name) as subkey:
                            name = self._get_reg_value(subkey, "DisplayName")
                            publisher = self._get_reg_value(subkey, "Publisher")
                            install_loc = self._get_reg_value(subkey, "InstallLocation")
                            if name:
                                apps.append({
                                    "name": name,
                                    "publisher": publisher,
                                    "install_location": install_loc
                                })
                    except Exception as e:
                        self.logger.warning(f"Error reading subkey {subkey_name}: {e}")
        except Exception as e:
            self.logger.error(f"Error opening registry {reg_path}: {e}")
        return apps

    def _get_reg_value(self, key, value_name) -> Optional[str]:
        try:
            value, _ = winreg.QueryValueEx(key, value_name)
            return value
        except:
            return None

    def scan_installed_apps(self) -> List[Dict[str, str]]:
        """Scans HKLM, HKCU, and Program Files for installed apps."""
        apps = []
        registry_paths = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        ]
        
        for hive, path in registry_paths:
            apps.extend(self._read_registry(hive, path))
        
        # Check common install directories (optional)
        program_files_dirs = [
            os.environ.get("ProgramFiles"),
            os.environ.get("ProgramFiles(x86)"),
            os.environ.get("LocalAppData") + "\\Programs"
        ]
        
        for dir_path in program_files_dirs:
            if dir_path and os.path.exists(dir_path):
                for root, _, files in os.walk(dir_path):
                    if "unins000.exe" in files:  # Common uninstaller
                        apps.append({
                            "name": os.path.basename(root),
                            "install_location": root
                        })
        return apps
