import time
import os
import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from PIL import Image
import pyheif

src_dir = ''
dest_dir = ''

image_extensions = ['.heic']
processed_files = set()

class FileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            time.sleep(5)
            src_path = event.src_path
            if os.path.exists(src_path):
                file_extension = os.path.splitext(src_path)[1]
                if file_extension.lower() in image_extensions and src_path not in processed_files:
                    if not os.path.exists(dest_dir):
                        os.makedirs(dest_dir)
                    file_name = str(src_path).split('/')[-1]
                    new_file_name = file_name.split('.')[0] + '.jpeg'
                    dest_path = os.path.join(dest_dir, new_file_name)
                    if not os.path.exists(dest_path):
                        heic_to_jpg(os.path.join(src_dir, file_name), 
                                    dest_path)
                        processed_files.add(src_path)
                        shutil.move(src_path, dest_dir)


def handle_existing_files():
    for file_name in os.listdir(src_dir):
        if os.path.isfile(os.path.join(src_dir, file_name)):
            file_extension = os.path.splitext(file_name)[1]
            if file_extension.lower() in image_extensions:
                if not os.path.exists(dest_dir):
                    os.makedirs(dest_dir)
                new_file_name = file_name.split('.')[0] + '.jpeg'
                heic_to_jpg(os.path.join(src_dir, file_name), 
                            os.path.join(dest_dir, new_file_name))
                shutil.move(os.path.join(src_dir, file_name), dest_dir)


def heic_to_jpg(heic_file_path, jpg_file_path):
    heif_file = pyheif.read(heic_file_path)
    image = Image.frombytes(
        heif_file.mode,
        heif_file.size,
        heif_file.data,
        'raw',
        heif_file.mode,
        heif_file.stride
    )
    image.save(jpg_file_path, 'JPEG')


if __name__ == '__main__':
    handle_existing_files()
    event_handler = FileHandler()
    observer = Observer()
    observer.schedule(event_handler, path=src_dir, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt():
        observer.stop()
    observer.join()
