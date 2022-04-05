# imports

import warnings

import numpy as np
import pandas as pd

from external.neuralynxio.scripts.channel import Channel

# note, detailed explanation on the file structures may be found at https://neuralynx.com/_software/NeuralynxDataFileFormats.pdf

# _____CONSTANTS_____

HEADER_SIZE = 16 * 1024  # header has 16 kilobytes length (note that this seems to be variable - if issues arise, double-check the header length)
SAMPLES_PER_RECORD = 512  # the number of samples per record of the .ncs file


# _____PUBLIC FUNCTIONS_____

def read_neuralynx_continuous_file(file_path, scaling='micro'):
    """

    Function for taking a neuralynx .ncs file and reading it in a  python compatible way

    Args:
        file_path: str
            .ncs file containing the recordings.
        scaling: None, 'micro', or 'milli'
            if None, scales the data in Volts -- otherwise, scales according to prefix

    Returns:
        A NeuralynxNCS object for the given data file

    """

    # open file
    fid = open(file_path, 'rb')

    # reference auxiliary attributes (such as ADBitVolts) from header
    hdr_dict = _parse_header(_read_header(fid))

    # skip header by shifting position by header size
    fid.seek(HEADER_SIZE)

    # Read data according to Neuralynx information
    data_format = np.dtype([('TimeStamp', np.uint64),  # timestamp in microseconds for this record -- sample time for the first data point in the samples array
                            ('ChannelNumber', np.uint32),  # channel number for this record
                            ('SampleFreq', np.uint32),  # sampling frequency
                            ('NumValidSamples', np.uint32),  # number of values in Samples containing valid data
                            ('Samples', np.int16, SAMPLES_PER_RECORD)])  # data points for a record -- currently, the samples array is a [512] array
    raw = np.fromfile(fid, dtype=data_format)

    # close file
    fid.close()

    # check that the integrity of the data -- might seem silly, but Neuralynx be wack
    _check_ncs_records(raw)

    # return a variable mapping the read file onto the relevant data structure
    return Channel(channel_number=raw['ChannelNumber'][0],
                   time_stamps=raw['TimeStamp'],
                   raw_readings=raw['Samples'],
                   header=hdr_dict,
                   scaling=scaling)


def read_neuralynx_continuous_files(file_paths):
    """

    Runs the function above but for an array of files

    Args:
        file_paths: [str]
            File paths of .ncs recordings.

    Returns:
        ncs_files: [Channel]
            array of NeuralynxNCS objects

    """

    channels = []

    for file in file_paths:
        try:
            channels.append(read_neuralynx_continuous_file(file))
        except:
            print('Could not open file {}'.format(file))

    return channels


def read_neuralynx_events_file(file_path):
    """

    Function for taking a neuralynx .nev file and reading it in a  python compatible way

    Args:
        file_path: str
            .ncs file containing the recordings.

    Returns:
        hdr_dict: dict of header
        df: pandas dataframe for the given data file

    """

    # open file
    fid = open(file_path, 'rb')

    # reference auxiliary attributes (such as ADBitVolts) from header
    hdr_dict = _parse_header(_read_header(fid))

    # skip header by shifting position by header size
    fid.seek(HEADER_SIZE)

    # read data according to Neuralynx information
    data_format = np.dtype([('stx', np.int16),  # reserved
                            ('pkt_id', np.int16),  # id for the originating system of this packet
                            ('pkt_data_size', np.int16),  # this value should always be two (2)
                            ('time_stamp', np.uint64),  # cheetah timestamp for this record - this value is in microseconds.
                            ('event_id', np.int16),  # id value for this event
                            ('ttl', np.int16),  # decimal TTL value read from the TTL input port
                            ('crc', np.int16),  # record CRC check from Cheetah.
                            ('dummy_one', np.int16),  # reserved
                            ('dummy_two', np.int16),  # reserved
                            ('extra', np.int32, 8),  # extra bit values for this event - this array has a fixed length of eight (8)
                            ('event_string', 'S', 128)])  # event string associated with this event record - this string consists of 127 characters plus the required null termination
    raw = np.fromfile(fid, dtype=data_format)

    # close file
    fid.close()

    # ensure that all packets have a data size of 2 -- this is the convention by neuralynx
    assert np.all(raw['pkt_data_size'] == 2), 'Some packets have invalid data size'

    # create data frame from file data
    data = {'stx': raw['stx'], 'pkt_id': raw['pkt_id'], 'pkt_data_size': raw['pkt_data_size'],
            'time_stamp': raw['time_stamp'], 'event_id': raw['event_id'], 'ttl': raw['ttl'], 'crc': raw['crc'],
            'dummy_one': raw['dummy_one'], 'dummy_two': raw['dummy_two'], 'extra': [i for i in raw['extra']],
            'event_string': [i.decode("utf-8")  for i in raw['event_string']]}

    # return
    return hdr_dict, pd.DataFrame(data)


# _____PRIVATE FUNCTIONS_____

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
    hdr = {}

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


def _check_ncs_records(raw):
    """
    Check that all records in the raw array have similar characteristics throughout the recording

    Args:

        raw: the raw extracted data

    """

    # reference the difference in time stamps to ensure that all records are incremented the same
    dt = np.diff(raw['TimeStamp'])
    dt = np.abs(dt - dt[0])

    # check that channel number remains the same
    if not np.all(raw['ChannelNumber'] == raw[0]['ChannelNumber']):
        warnings.warn('Channel number changed during record sequence')

    # check that the sampling frequency remains the same
    if not np.all(raw['SampleFreq'] == raw[0]['SampleFreq']):
        warnings.warn('Sampling frequency changed during record sequence')

    # check that there are the correct number of samples per time point
    if not np.all(raw['NumValidSamples'] == 512):
        warnings.warn('Invalid samples in one or more records')

    # check that the time difference is always less than 1
    if not np.all(dt <= 1):
        warnings.warn('Time stamp difference tolerance exceeded')
