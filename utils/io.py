import ntpath
import os
import gc

import numpy as np

from utils.external import mdaio


def get_all_files_with_extension(directory, extension, keyword=None):
    """

    Get all files in a directory with a certain extension

    Args:
        directory: str
            path to directory to look through
        extension: str
            type of files to look through
        keyword: str
            if applicable, get only files with this keyword

    Returns:
        file_paths: [str]
            array of file paths
    """

    file_paths = []

    # iterate over all files in directory
    for file in os.listdir(directory):

        # iterate over all files with a given extension
        if file.endswith(extension):

            # no further sorting is required by keyword
            if keyword is None:
                file_paths.append(os.path.join(directory, file))

            # sort further by keyword
            else:
                file_paths.append(os.path.join(directory, file)) if keyword in file else None

    return sorted(file_paths)


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

def np_to_mda(path_to_np, output_path, dtype='float64', verbose=True):
    """

    Converts npz files to the mda format for use with mountainsort and writes them to disk

    Args:
        path_to_np: str
            path to the npz file 
        output_path: str
            path to save the mda file
        dtype: str
            data type by which to save the mda file -- can be 'uint8', 'uint16', 'uint32' 'int16' 'int32' 'float32', 'float64'
        verbose: bool
            whether to do an integrity check after

    """

    # load the file and extract relevant information
    print('Loading numpy data from {}'.format(path_to_np))
    loaded = np.load(path_to_np)
    print('Finished loading numpy data from {}'.format(path_to_np))
    names = loaded['names']
    traces = loaded['traces']

    # write the mda file
    if dtype == 'float64':
        mdaio.writemda64(traces, output_path)
    else:
        raise NotImplementedError('Writing .mda files in format other than float64 has not yet been implemented')

    if verbose:
        mda = mdaio.readmda(output_path)
        print('MDA file was written in the following order: {}'.format(names))
        print('First few data points from original file: {}'.format(traces[0][:11]))
        print('First few data points from mda file: {}'.format(mda[0][:11]))

    # memory clean up
    del loaded
    del names
    del traces
    gc.collect()

