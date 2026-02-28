# https://www.reddit.com/r/PleX/comments/s14kbf/whats_the_plex_dance_to_get_plex_to_redetect_the/
import os
import shutil

from tqdm import tqdm

folder_path = os.getenv('SHOW_FOLDER_PATH')
temp_folder_path = os.getenv('TEMP_FOLDER_PATH')


def move_files(source_path, destination_path):
    if not source_path or not destination_path:
        raise ValueError('Both source_path and destination_path are required.')

    os.makedirs(destination_path, exist_ok=True)
    # take files currently on plex and move them to a temp folder
    for file_name in tqdm(os.listdir(source_path)):
        print(f'Moving file: {file_name} to {destination_path}')
        shutil.move(os.path.join(source_path, file_name), os.path.join(destination_path, file_name))
        print('Moved.')


def plex_dance(show_path=None, temp_path=None, wait_for_input=True):
    show_path = show_path or folder_path
    temp_path = temp_path or temp_folder_path

    move_files(show_path, temp_path)
    print('Press enter after scanning and emptying trash.')
    if wait_for_input:
        input('> ')
    # move files back to plex
    move_files(temp_path, show_path)


def main():
    plex_dance()


if __name__ == '__main__':
    main()
