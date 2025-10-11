import time
import shutil
import zipfile
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Watch folder
WATCH_FOLDER = Path.home() / "Downloads/Maritime Knowledge"

# Destination folders
DEST_FOLDERS = {
    "Images": Path.home() / "third-officer-maintenance-system/data_sources/originals/Images",
    "PDFs": Path.home() / "third-officer-maintenance-system/data_sources/originals/Documents/PDFs",
    "Certificates": Path.home() / "third-officer-maintenance-system/data_sources/originals/Documents/Certificates",
    "Spreadsheets": Path.home() / "third-officer-maintenance-system/data_sources/originals/Documents/Spreadsheets",
    "Word_Files": Path.home() / "third-officer-maintenance-system/data_sources/originals/Documents/Word_Files",
    "Other_Files": Path.home() / "third-officer-maintenance-system/data_sources/originals/Other_Files",
    "Uncategorized": Path.home() / "third-officer-maintenance-system/data_sources/originals/Uncategorized"
}

# Ensure destination folders exist
for folder in DEST_FOLDERS.values():
    folder.mkdir(parents=True, exist_ok=True)

LOG_FILE = Path.home() / "third-officer-maintenance-system/scripts/auto_move_log.txt"

# File type sets
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".svg"}
PDF_EXTENSIONS = {".pdf"}
SPREADSHEET_EXTENSIONS = {".xls", ".xlsx", ".csv"}
WORD_EXTENSIONS = {".doc", ".docx"}

def log(message: str):
    print(message)
    with LOG_FILE.open("a") as f:
        f.write(message + "\n")

def move_file(src_path: Path):
    try:
        name_lower = src_path.name.lower()
        if src_path.suffix.lower() in IMAGE_EXTENSIONS:
            dest_path = DEST_FOLDERS["Images"] / src_path.name
        elif src_path.suffix.lower() in PDF_EXTENSIONS:
            if "certificate" in name_lower:
                dest_path = DEST_FOLDERS["Certificates"] / src_path.name
            else:
                dest_path = DEST_FOLDERS["PDFs"] / src_path.name
        elif src_path.suffix.lower() in SPREADSHEET_EXTENSIONS:
            dest_path = DEST_FOLDERS["Spreadsheets"] / src_path.name
        elif src_path.suffix.lower() in WORD_EXTENSIONS:
            dest_path = DEST_FOLDERS["Word_Files"] / src_path.name
        elif src_path.suffix.lower() == ".zip":
            with zipfile.ZipFile(src_path, 'r') as zip_ref:
                extract_folder = DEST_FOLDERS["Other_Files"]
                zip_ref.extractall(extract_folder)
                log(f"Extracted ZIP: {src_path.name} → {extract_folder}")
            src_path.unlink()  # delete ZIP after extraction
            return
        else:
            dest_path = DEST_FOLDERS["Other_Files"] / src_path.name

        shutil.move(str(src_path), str(dest_path))
        log(f"Moved {src_path.name} → {dest_path}")
    except Exception as e:
        log(f"Error moving {src_path}: {e}")

class Handler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            time.sleep(1)  # wait to ensure download completes
            move_file(Path(event.src_path))

if __name__ == "__main__":
    observer = Observer()
    observer.schedule(Handler(), str(WATCH_FOLDER), recursive=False)
    observer.start()
    print(f"Watching folder: {WATCH_FOLDER}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
