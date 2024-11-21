import requests
import os
import zipfile
import shutil

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
                print(f"New version {latest_version} available!")
                return latest_version, download_url
            else:
                print("You are using the latest version.")
                return None, None
        except Exception as e:
            print(f"Failed to check for updates: {e}")
            return None, None

    def download_update(self, download_url, output_dir):
        try:
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
            print("Update downloaded and extracted.")
            return True
        except Exception as e:
            print(f"Failed to download update: {e}")
            return False

    def apply_update(self, app_dir, update_dir):
        try:
            # Replace old files with new files
            for item in os.listdir(update_dir):
                s = os.path.join(update_dir, item)
                d = os.path.join(app_dir, item)
                print(f"Updating: {s} -> {d}")  # Debugging log
                if os.path.isdir(s):
                    if os.path.exists(d):
                        shutil.rmtree(d)
                    shutil.copytree(s, d)
                else:
                    shutil.copy2(s, d)
            print("Update applied successfully.")
            print(f"App directory: {os.getcwd()}")
            print(f"Update directory: {update_dir}")
            return True
        except Exception as e:
            print(f"Failed to apply update: {e}")
            return False