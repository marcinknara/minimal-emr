import requests
import os
import zipfile
import shutil
import logging

logger = logging.getLogger(__name__)

class UpdateManager:
    def __init__(self, current_version, repo_owner, repo_name):
        self.current_version = current_version
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.update_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"
    
    def check_for_updates(self):
        try:
            response = requests.get(self.update_url)
            response.raise_for_status()
            release_data = response.json()
            
            latest_version = release_data["tag_name"]
            if self.current_version != latest_version:
                download_url = release_data["assets"][0]["browser_download_url"]
                logger.info(f"New version {latest_version} available!")
                return latest_version, download_url
            else:
                logger.info("You are using the latest version.")
                return None, None
        except Exception as e:
            logger.error(f"Failed to check for updates: {e}")
            return None, None

    def download_update(self, download_url, output_dir):
        try:
            logger.info("Starting update download from: %s", download_url)
            response = requests.get(download_url, stream=True)
            response.raise_for_status()

            zip_path = os.path.join(output_dir, "update.zip")
            with open(zip_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=1024):
                    file.write(chunk)

            # Extract the zip
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(output_dir)

            os.remove(zip_path)
            logger.info("Update downloaded and extracted to: %s", output_dir)
            return True
        except Exception as e:
            logger.error(f"Failed to download update: {e}")
            return False

    def apply_update(self, app_dir, update_dir):
        """Apply the downloaded update."""
        try:
            logger.info("Applying update from: %s", update_dir)
            for item in os.listdir(update_dir):
                source_path = os.path.join(update_dir, item)
                dest_path = os.path.join(app_dir, item)

                # Skip non-regular files, sockets, and unnecessary system directories
                if not os.path.exists(source_path):
                    logger.warning("Source path does not exist: %s", source_path)
                    continue
                if os.path.islink(source_path) or not (os.path.isfile(source_path) or os.path.isdir(source_path)):
                    logger.warning("Skipping non-regular file: %s", source_path)
                    continue
                if item.startswith(".") or item.startswith("com.apple") or item in ["TemporaryItems"]:
                    logger.info("Skipping system or hidden file/directory: %s", source_path)
                    continue

                # Copy directories or files
                if os.path.isdir(source_path):
                    logger.info("Updating directory: %s -> %s", source_path, dest_path)
                    if os.path.exists(dest_path):
                        logger.info("Removing existing directory: %s", dest_path)
                        shutil.rmtree(dest_path)
                    shutil.copytree(source_path, dest_path)
                elif os.path.isfile(source_path):
                    logger.info("Updating file: %s -> %s", source_path, dest_path)
                    shutil.copy2(source_path, dest_path)

            logger.info("Update applied successfully.")
            return True
        except Exception as e:
            logger.error("Failed to apply update: %s", str(e))
            return False