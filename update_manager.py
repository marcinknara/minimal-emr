import requests
import os
import zipfile
import shutil
import logging
import re
import platform
from packaging.version import Version, InvalidVersion
import sys
import psutil  # To check and terminate running processes
import time
import subprocess

# Add this to the top of update_manager.py
def setup_logging():
    log_dir = os.path.expanduser("~/Library/Application Support/CaseManager")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "app.log")

    logging.basicConfig(
        filename=log_file,
        filemode="a",  # Append to the log file
        format="%(asctime)s - %(levelname)s - %(message)s",
        level=logging.DEBUG,
    )
    logging.debug("UpdateManager logging setup complete.")

setup_logging()

def wait_for_application_exit(app_name):
    """Wait for the application process to terminate."""
    logging.info(f"Waiting for {app_name} to exit...")
    while True:
        running = False
        for process in psutil.process_iter(['name']):
            if process.info['name'] == app_name:
                running = True
                break
        if not running:
            break
        time.sleep(1)  # Check every second
    logging.info(f"{app_name} has exited.") 


class UpdateManager:
    def __init__(self, current_version, repo_owner, repo_name):
        self.current_version = current_version
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.update_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"
    
    def get_update_directory(self):
        """Return the update directory path based on the platform."""
        if platform.system() == "Darwin":  # macOS
            base_dir = os.path.expanduser("~/Library/Application Support/CaseManager/updates")
        elif platform.system() == "Windows":  # Windows
            base_dir = os.path.join(os.getenv("LOCALAPPDATA", ""), "CaseManager", "updates")
        else:  # Linux or others
            base_dir = os.path.expanduser("~/.config/CaseManager/updates")

        os.makedirs(base_dir, exist_ok=True)  # Ensure the directory exists
        return base_dir

    def normalize_version(self, version):
        """Normalize the version string by removing prefixes like 'v'."""
        return re.sub(r'^v', '', version)

    def check_for_updates(self):
        try:
            response = requests.get(self.update_url)
            response.raise_for_status()
            release_data = response.json()
            
            # Normalize version strings for comparison
            latest_version_raw = release_data["tag_name"]
            latest_version = self.normalize_version(latest_version_raw)
            current_version = self.normalize_version(self.current_version)

            logging.debug(f"Comparing versions: current={self.current_version}, latest={latest_version}")

             # Use packaging.version for semantic version comparison
            try:
                if Version(current_version) < Version(latest_version):
                    download_url = release_data["assets"][0]["browser_download_url"]
                    logging.info(f"New version {latest_version} available!")
                    return latest_version, download_url
                else:
                    logging.info("You are using the latest version.")
                    return None, None
            except InvalidVersion as e:
                logging.error(f"Invalid version encountered: {e}")
                return None, None
        except Exception as e:
            logging.error(f"Failed to check for updates: {e}")
            return None, None

    def download_update(self, download_url, output_dir=None):
        try:
            if not output_dir:
                output_dir = self.get_update_directory()  # Use user-specific directory
            logging.info("Starting update download from: %s", download_url)
            response = requests.get(download_url, stream=True)
            response.raise_for_status()

            zip_path = os.path.join(output_dir, "update.zip")
            with open(zip_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=1024):
                    file.write(chunk)

            # Extract the zip
            extracted_dir = os.path.join(output_dir, "update_package")
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(extracted_dir)

            os.remove(zip_path)
            logging.info("Update downloaded and extracted to: %s", extracted_dir)
            return extracted_dir
        except Exception as e:
            logging.error(f"Failed to download update: {e}")
            return None

    def apply_update(self, app_dir=None, update_dir=None):
        """Apply the downloaded update and restart the application."""
        try:
            if not app_dir:
                app_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
            if not update_dir:
                update_dir = self.get_update_directory()

            logging.info("Waiting for application to exit before applying update...")
            self.terminate_running_instance()  # Ensure the main app is terminated
            wait_for_application_exit("CaseManager")  # Replace with the exact app name if needed

            logging.info("Applying update from: %s", update_dir)
            extracted_update_dir = os.path.join(update_dir, "update_package")
            if not os.path.exists(extracted_update_dir):
                logging.error("Update package directory not found: %s", extracted_update_dir)
                return False

            # Apply the update
            for item in os.listdir(extracted_update_dir):
                source_path = os.path.join(extracted_update_dir, item)
                dest_path = os.path.join(app_dir, item)

                if os.path.isdir(source_path):
                    logging.info("Updating directory: %s -> %s", source_path, dest_path)
                    if os.path.exists(dest_path):
                        shutil.rmtree(dest_path)
                    shutil.copytree(source_path, dest_path)
                elif os.path.isfile(source_path):
                    logging.info("Updating file: %s -> %s", source_path, dest_path)
                    shutil.copy2(source_path, dest_path)

            # Clean up temporary update directory
            shutil.rmtree(update_dir, ignore_errors=True)
            logging.info("Update applied successfully.")

            # Restart the application
            self.restart_application()
            return True
        except Exception as e:
            logging.error("Failed to apply update: %s", str(e))
            return False

    def terminate_running_instance(self):
        """Terminate the running instance of the application."""
        current_pid = os.getpid()
        for process in psutil.process_iter(['pid', 'name']):
            if process.info['name'] == "CaseManager" and process.info['pid'] != current_pid:
                logging.info(f"Terminating running process: PID {process.info['pid']}")
                process.terminate()
                process.wait(timeout=5)

    def restart_application(self):
        """Restart the application."""
        try:
            logging.info("Restarting application...")
            subprocess.Popen([sys.executable] + sys.argv)
            sys.exit(0)
        except Exception as e:
            logging.error("Failed to restart application: %s", str(e))