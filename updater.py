import os
import shutil
import subprocess
import sys
import time
import logging

def setup_logging():
    log_file = os.path.expanduser("~/Library/Application Support/CaseManager/updater.log")
    logging.basicConfig(
        filename=log_file,
        filemode="a",
        format="%(asctime)s - %(levelname)s - %(message)s",
        level=logging.DEBUG,
    )
    logging.debug("Updater logging setup complete.")

setup_logging()

def apply_update(app_dir, update_dir):
    try:
        extracted_update_dir = os.path.join(update_dir, "update_package")
        logging.info(f"Applying update from: {extracted_update_dir} to {app_dir}")

        if not os.path.exists(extracted_update_dir):
            logging.error(f"Update package directory not found: {extracted_update_dir}")
            return False

        # Copy updated files to the application directory
        for item in os.listdir(extracted_update_dir):
            source_path = os.path.join(extracted_update_dir, item)
            dest_path = os.path.join(app_dir, item)

            if os.path.isdir(source_path):
                logging.info(f"Updating directory: {source_path} -> {dest_path}")
                if os.path.exists(dest_path):
                    shutil.rmtree(dest_path)
                shutil.copytree(source_path, dest_path)
            elif os.path.isfile(source_path):
                logging.info(f"Updating file: {source_path} -> {dest_path}")
                shutil.copy2(source_path, dest_path)

        # Clean up temporary update directory
        shutil.rmtree(update_dir, ignore_errors=True)
        logging.info("Update applied successfully.")
        return True
    except Exception as e:
        logging.error(f"Failed to apply update: {str(e)}")
        return False

def restart_application(app_path):
    try:
        logging.info(f"Restarting application: {app_path}")
        subprocess.Popen([sys.executable, app_path])
    except Exception as e:
        logging.error(f"Failed to restart application: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: updater.py <app_dir> <update_dir>")
        sys.exit(1)

    app_dir = sys.argv[1]
    update_dir = sys.argv[2]

    # Apply the update
    if apply_update(app_dir, update_dir):
        # Restart the application
        app_path = os.path.join(app_dir, "emr_app.py")
        restart_application(app_path)
    else:
        logging.error("Update failed. Application will not restart.")