import os
import shutil
import unicodedata
import zipfile
import sys


def normalize(text):
    normalized_text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')
    normalized_text = ''.join([char if char.isalnum() or char in {'_', '.'} else '_' for char in normalized_text])
    return normalized_text


def extract_archive(archive_path, target_path):
    with zipfile.ZipFile(archive_path, 'r') as zip_ref:
        zip_ref.extractall(target_path)


def sort_files(folder_path):
    accepted_folders = {'archives', 'video', 'audio', 'documents', 'images'}
    image_extensions = {'JPEG', 'PNG', 'JPG', 'SVG'}
    video_extensions = {'AVI', 'MP4', 'MOV', 'MKV'}
    document_extensions = {'DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'XLS', 'PPTX'}
    audio_extensions = {'MP3', 'OGG', 'WAV', 'AMR'}
    archive_extensions = {'ZIP', 'GZ', 'TAR'}

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        if os.path.isfile(file_path):
            # Normalizuje nazwę pliku
            normalized_filename = normalize(filename)

            # Pobieranie rozszerzenia pliku
            _, file_extension = os.path.splitext(normalized_filename)
            file_extension = file_extension[1:].upper()

            # Określa folder docelowy na podstawie rozszerzenia
            if file_extension in image_extensions:
                target_folder = "images"
            elif file_extension in video_extensions:
                target_folder = "video"
            elif file_extension in document_extensions:
                target_folder = "documents"
            elif file_extension in audio_extensions:
                target_folder = "audio"
            elif file_extension in archive_extensions:
                target_folder = "archives"
            else:
                target_folder = "unknown"

            # Tworzy folder docelowy, jeśli nie istnieje
            target_path = os.path.join(folder_path, target_folder)
            if not os.path.exists(target_path):
                os.makedirs(target_path)

            # Przenoszenie pliku do odpowiedniego folderu
            shutil.move(file_path, os.path.join(target_path, normalized_filename))

        elif os.path.isdir(file_path) and filename not in accepted_folders:
            # Rekurencyjnie przetwarzanie zagnieżdżonych folderów
            sort_files(file_path)

        elif zipfile.is_zipfile(file_path):
            # Obssługiwanie archiwów
            target_folder = "archives"
            target_path = os.path.join(folder_path, target_folder)

            # Tworzy folder docelowy, jeśli nie istnieje
            if not os.path.exists(target_path):
                os.makedirs(target_path)

            # Wypakowuje archiwum do podfolderu o nazwie archiwum bez rozszerzenia
            archive_name = os.path.splitext(normalized_filename)[0]
            archive_target_path = os.path.join(target_path, archive_name)

            # Tworzy podfolder archiwum, jeśli nie istnieje
            if not os.path.exists(archive_target_path):
                os.makedirs(archive_target_path)

            # Wypakowuje archiwum
            extract_archive(file_path, target_path)

            # Przenosi zawartość archiwum do podfolderu o właściwej nazwie
            for extracted_file in os.listdir(archive_target_path):
                extracted_file_path = os.path.join(archive_target_path, extracted_file)
                shutil.move(extracted_file_path, target_path)

            # Usuwa archiwum
            os.remove(file_path)

    # Usuwa puste foldery
    for root, dirs, files in os.walk(folder_path, topdown=False):
        for folder in dirs:
            folder_path = os.path.join(root, folder)
            if not os.listdir(folder_path):
                os.rmdir(folder_path)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(1)
    folder_to_sort = sys.argv[1]
    sort_files(folder_to_sort)
