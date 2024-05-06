# Running Man episodes get categorized incorrectly sometimes. This script will fix that.
import os
from pathlib import Path

NZBGET_COMPLETE_DIR = 'C:\\Users\\Nick\\Downloads'
list_of_files = os.listdir(NZBGET_COMPLETE_DIR + '\\')


def rename_file(file_name):
    folder_in_folder = os.listdir(NZBGET_COMPLETE_DIR + '\\' + file_name)[0]
    good_file_name = folder_in_folder.replace('[Esub]', '.').replace('[NCscrapes]', '').replace(' 720P', '.720P')
    good_file_path = NZBGET_COMPLETE_DIR + '\\' + file_name + '\\' + good_file_name
    complete_folder_path = NZBGET_COMPLETE_DIR + '\\' + file_name + '\\' + folder_in_folder
    file_in_folder = os.listdir(complete_folder_path)[0]
    complete_file_path = complete_folder_path + '\\' + file_in_folder
    file_extension = Path(complete_file_path).suffix
    full_good_file_path = good_file_path.replace('[Esub]', '.').replace('[NCscrapes]', '') + '.720P' + file_extension
    print('renaming: ', complete_file_path, ' to ', full_good_file_path)
    # replace file_in_folder file name with good_file_name
    # make folder for final_file_name except the last part
    try:
        os.makedirs('\\'.join(full_good_file_path.split('\\')[:-1]))
    except FileExistsError:
        pass
    os.rename(complete_file_path,
              full_good_file_path)
    # remove the complete_file_path
    os.rmdir(complete_folder_path)
    # also remove the folder in folder
    os.rmdir('\\'.join(complete_folder_path.split('\\')[:-1]))

    return


def initial_rename():
    for file in list_of_files:
        if 'Running.Man[Esub]' in file:
            rename_file(file)
        else:
            print('skipping: ', file)


def rename_and_sort():

    seasons = {
        'Season 2010': ['E0' + str(i) + '.' for i in range(1, 24)],
        'Season 2011': ['E0' + str(i) for i in range(24, 75)],
        'Season 2012': ['E0' + str(i) for i in range(75, 100)],
        'Season 2013': ['E' + str(i) for i in range(127, 179)],
        'Season 2014': ['E' + str(i) for i in range(179, 228)],
        'Season 2015': ['E' + str(i) for i in range(228, 280)],
        'Season 2016': ['E' + str(i) for i in range(280, 332)],
        'Season 2017': ['E' + str(i) for i in range(332, 384)],
        'Season 2018': ['E' + str(i) for i in range(384, 433)],
        'Season 2019': ['E' + str(i) for i in range(433, 484)],
        'Season 2020': ['E' + str(i) for i in range(484, 536)],
        'Season 2021': ['E' + str(i) for i in range(536, 586)],
        'Season 2022': ['E' + str(i) for i in range(586, 635)],
        'Season 2023': ['E' + str(i) for i in range(635, 686)],
        'Season 2024': ['E' + str(i) for i in range(686, 709)],
    }
    seasons['Season 2012'].extend([str(i) for i in range(100, 127)])


    base_path = 'C:\\Users\\Nick\\Downloads'
    for file in list_of_files:
        for season, episodes in seasons.items():
            #print(season)
            for episode in episodes:
                if episode in file:
                    if 'Running.Man' in file:
                        print('found: ', episode)
                        print('moving: ', NZBGET_COMPLETE_DIR + '\\' + file, ' to ', base_path + '\\' + season)
                        try:
                            os.makedirs(base_path + '\\' + season)
                        except FileExistsError:
                            pass
                        print('78,', NZBGET_COMPLETE_DIR + '\\' + file)
                        full_file_name = base_path + '\\' + season + '\\' + file.replace('S01', season)
                        print('80: ', full_file_name)
                        os.rename(NZBGET_COMPLETE_DIR + '\\' + file, full_file_name)

        pass


if __name__ == '__main__':
    rename_and_sort()
