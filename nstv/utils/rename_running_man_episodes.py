# Running Man episodes get categorized incorrectly sometimes. This script will fix that.
import os
from pathlib import Path

NZBGET_COMPLETE_DIR = os.getenv('NZBGET_COMPLETE_DIR')
list_of_files = os.listdir(NZBGET_COMPLETE_DIR + '\\')


def rename_file(file_name):
    folder_in_folder = os.listdir(NZBGET_COMPLETE_DIR + '\\' + file_name)[0]
    good_file_name = folder_in_folder.replace('[Esub]', '.').replace('[NCscrapes]', '')
    file_in_folder = os.listdir(NZBGET_COMPLETE_DIR + '\\' + file_name + '\\' + folder_in_folder)[0]
    file_extension = Path(file_in_folder).suffix
    # replace file_in_folder file name with good_file_name
    os.rename(NZBGET_COMPLETE_DIR + '\\' + file_name + '\\' + folder_in_folder + '\\' + file_in_folder,
              NZBGET_COMPLETE_DIR + '\\' + file_name + '\\' + folder_in_folder + '\\' + good_file_name + file_extension)
    return


def main():
    for file in list_of_files:
        if 'Running.Man' in file:
            rename_file(file)


if __name__ == '__main__':
    main()
