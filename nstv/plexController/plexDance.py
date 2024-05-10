# https://www.reddit.com/r/PleX/comments/s14kbf/whats_the_plex_dance_to_get_plex_to_redetect_the/
import os
import shutil

from tqdm import tqdm

folder_path = os.getenv('SHOW_FOLDER_PATH')
temp_folder_path = os.getenv('TEMP_FOLDER_PATH')


def move_files():
    # take files currently on plex and move them to a temp folder
    for file_name in tqdm(os.listdir(folder_path)):
        print(f'Moving file: {file_name} to {temp_folder_path}')
        shutil.move(f'{folder_path}\\{file_name}', f'{temp_folder_path}\\{file_name}')
        print('Moved.')


def main():
    move_files()
    print('Press enter after scanning and emptying trash.')
    input('> ')
    # move files back to plex
    for file_name in tqdm(os.listdir(temp_folder_path)):
        print(f'Moving file: {file_name} to {folder_path}')
        shutil.move(f'{temp_folder_path}\\{file_name}', f'{folder_path}\\{file_name}')


if __name__ == '__main__':
    main()
