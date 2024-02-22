# Running Man episodes get categorized incorrectly sometimes. This script will fix that.
import os
from pathlib import Path

NZBGET_COMPLETE_DIR = os.getenv('NZBGET_COMPLETE_DIR')
list_of_files = os.listdir(NZBGET_COMPLETE_DIR + '\\')


def rename_file(file_name):
    folder_in_folder = os.listdir(NZBGET_COMPLETE_DIR + '\\' + file_name)[0]
    good_file_name = folder_in_folder.replace('[Esub]', '.S01').replace('[NCscrapes]', '').replace(' 720P', '.720P')
    good_file_path = NZBGET_COMPLETE_DIR + '\\' + file_name + '\\' + good_file_name
    complete_folder_path = NZBGET_COMPLETE_DIR + '\\' + file_name + '\\' + folder_in_folder
    file_in_folder = os.listdir(complete_folder_path)[0]
    complete_file_path = complete_folder_path + '\\' + file_in_folder
    file_extension = Path(complete_file_path).suffix
    full_good_file_path = good_file_path.replace('[Esub]', '.S01').replace('[NCscrapes]', '') + file_extension
    print('renaming: ', complete_file_path, ' to ', full_good_file_path)
    # replace file_in_folder file name with good_file_name
    # make folder for final_file_name except the last part
    os.makedirs('\\'.join(full_good_file_path.split('\\')[:-1]))
    os.rename(complete_file_path,
              full_good_file_path)
    # remove the complete_file_path
    os.rmdir(complete_folder_path)
    # also remove the folder in folder
    os.rmdir('\\'.join(complete_folder_path.split('\\')[:-1]))

    return


def main():
    for file in list_of_files:
        if 'Running.Man[Esub]' in file:
            rename_file(file)
        else:
            print('skipping: ', file)


if __name__ == '__main__':
    main()
