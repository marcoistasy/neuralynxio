# imports

import numpy as np
from channel import Channel

# properties

HEADER_SIZE = 16 * 1024  # Header has 16 kilobytes length (note that this seems to be variable - if issues arise,
# double check the header length)


# Functions

def read_neuralynx_ncs(file):
    """

    Function for taking a neuralynx .ncs file and reading it in a  python compatible way

    Args:
        file: .ncs
        NCS file containing the recordings.

    Returns:
        A NeuralynxNCS object for the given data file

    """

    # Open file
    fid = open(file, 'rb')

    # Reference auxiliary attributes (such as ADBitVolts) from header
    hdr_dict = _parse_header(_read_header(fid))

    # Skip header by shifting position by header size
    fid.seek(HEADER_SIZE)

    # Read data according to Neuralynx information
    data_format = np.dtype([('TimeStamp', np.uint64),
                            ('ChannelNumber', np.uint32),
                            ('SampleFreq', np.uint32),
                            ('NumValidSamples', np.uint32),
                            ('Samples', np.int16, 512)])

    raw = np.fromfile(fid, dtype=data_format)

    # Close file
    fid.close()

    # return a variable mapping the read file onto the relevant data structure (see neuralynx_models for
    # specifications of the structures)

    return Channel(raw_chan_number=raw['ChannelNumber'],
                   time_stamps=raw['TimeStamp'],
                   raw_readings=raw['Samples'],
                   hdr_dict=hdr_dict)


def read_neuralynx_files(file_paths):
    """

    Runs the function above but for an array of files

    Args:
        file_paths: array
            File paths of NCS recordings.

    Returns:
        ncs_files: array
            array of NeuralynxNCS objects

    """

    ncs_files = []

    for file in file_paths:
        try:
            ncs_files.append(read_neuralynx_ncs(file))
        except:
            print('Could not open file {}'.format(file))

    return ncs_files


def _read_header(fid):
    """

    Read the raw header data (16 kb) from the file object fid.
    Restore the position in the file object after reading.

    Args:
        fid: file to read opened in a 'rb' manner

    Returns:
        Raw Header instance

    """

    pos = fid.tell()
    fid.seek(0)
    raw_hdr = fid.read(HEADER_SIZE).strip(b'\0')
    fid.seek(pos)

    return raw_hdr


def _parse_header(raw_hdr):
    """
    Args:

        raw_hdr: raw header instance

    Returns:
        Dictionary of header attributes mapped on to values

    """

    # Parse the header string into a dictionary of name value pairs
    hdr = dict()

    # Decode the header as iso-8859-1 (the spec says ASCII, but there is at least one case of 0xB5 in some headers)
    raw_hdr = raw_hdr.decode('iso-8859-1')

    # Get the independent lines of the header
    hdr_lines = [line.strip() for line in raw_hdr.split('\r\n') if line != '']

    # Read the parameters, assuming "-PARAM_NAME PARAM_VALUE" format
    for line in hdr_lines[1:]:

        try:
            name, value = line[1:].split(maxsplit=1)  # Ignore the dash and split PARAM_NAME and PARAM_VALUE
            hdr[name] = value
        except:
            print('Unable to parse parameter line from Neuralynx header: {}'.format(line))

    return hdr

#%%
channel = read_neuralynx_ncs('RAM5_0001.ncs')