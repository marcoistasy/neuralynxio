# imports

import ntpath
import os


def get_all_files_with_extension(directory, extension):
    """

    Get all files in a directory with a certain extension

    Args:
        directory: str
            path to directory to look through
        extension: str
            type of files to look through

    Returns:
        file_paths: array
            array of file paths
    """

    file_paths = []

    for file in os.listdir(directory):

        if file.endswith(extension):
            file_paths.append(os.path.join(directory, file))

    return file_paths


def remove_paths_with_continuation(file_paths):
    """

    Remove all read file paths that are a continuation of another (i.e whose index is not 0).

    Args:
        file_paths: [str]
         all file paths to be read

    Returns:
        A processed object of file_paths where non-zero indices are removed

    """

    kept_paths = []

    for file_path in file_paths:
        file_name_without_extension = ntpath.basename(file_path).split('.ncs')[0]

        # if the channel is part of a series, return the index. Otherwise, return 0.
        try:
            _ = file_name_without_extension.split('_')[1]
        except:
            kept_paths.append(file_path)

    return kept_paths
