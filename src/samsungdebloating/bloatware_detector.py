from typing import List, Dict, Any
import json
import os

class BloatwareDetector:
    JSON_FILE_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'samsung.json')

    def __init__(self):
        self._bloatware_apps = self._load_bloatware_apps()

    def _load_bloatware_apps(self) -> List[Dict[str, Any]]:
        with open(self.JSON_FILE_PATH, mode='r', encoding='utf-8') as f:
            bloatware_apps = json.load(f)
        return bloatware_apps

    def compare_installed_apps(self, installed_apps: List[str]) -> List[str]:
        bloatware_detected = [
            app['Name']
            for app in self._bloatware_apps
            if app['Package'] in installed_apps
        ]
        return bloatware_detected
    
    def get_app_id(self, app_name: str) -> str:
        for app in self._bloatware_apps:
            if app['Name'] == app_name:
                return app['Package']
        return None
