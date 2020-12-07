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