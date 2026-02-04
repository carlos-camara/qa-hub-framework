import os
import shutil
import re
from datetime import datetime

class ReportManager:
    @staticmethod
    def organize_junit_reports(temp_dir, target_base, project_name=None):
        """
        Organizes JUnit XML files from a temp directory into a structured reports folder.
        Matches the logic previously implemented in PowerShell scripts.
        """
        if not os.path.exists(temp_dir):
            print(f"[ReportManager] Temp directory not found: {temp_dir}")
            return

        if not os.path.exists(target_base):
            os.makedirs(target_base)

        xml_files = [f for f in os.listdir(temp_dir) if f.startswith("TESTS-") and f.endswith(".xml")]
        if not xml_files:
            print("[ReportManager] No JUnit XML files found to organize.")
            return

        # Use current time for potential new folder
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        # We might want to group artifacts from the same run if they happen within a short window
        # For simplicity, we create one folder per execution if one doesn't exist already
        
        for filename in xml_files:
            # Extract project name from filename: TESTS-<project>.<feature>.xml
            match = re.search(r"TESTS-([^.]+)", filename)
            current_project = match.group(1) if match else (project_name or "unknown")
            
            # Find a recent directory for this project (within last 5 mins) to keep files together
            # In Python we'll just use a fresh one for the whole call unless we want to be fancy
            
            target_dir = os.path.join(target_base, f"{current_project}_{timestamp}")
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
            
            src = os.path.join(temp_dir, filename)
            dst = os.path.join(target_dir, filename)
            
            shutil.move(src, dst)
            print(f"[ReportManager] Moved {filename} -> {target_dir}")

        # Cleanup temp dir if empty
        try:
            if not os.listdir(temp_dir):
                os.rmdir(temp_dir)
        except Exception:
            pass
