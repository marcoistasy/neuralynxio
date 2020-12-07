# imports

import numpy as np
import ntpath
import copy

# _____CONSTANTS_____

MICROVOLT_FACTOR = 1e+6

class Channel:

    # A class that holds all information from a neuralynx .ncs file

    def __init__(self, channel_number, time_stamps, raw_readings, header):
        """ Init """

        # properties that can be directly set from source
        self.time_stamps = time_stamps
        self._header = header

        # properties that must be indexed from source
        self.sampling_frequency = float(self._header['SamplingFrequency'])
        self.channel_number = channel_number
        self.channel_name = self._header['AcqEntName']

        # properties that must be computed from source
        self._raw_readings = raw_readings.ravel()
        self.readings = self._raw_readings * float(self._header['ADBitVolts']) * MICROVOLT_FACTOR  # convert to microvolts

    # _____PROPERTIES_____

    @property
    def duration(self):
        """

        Returns:
            the duration of the recording (in seconds)

        """

        return self.readings.shape[0] / self.sampling_frequency

    @property
    def time_vector(self):
        """

        Returns:

            a 1d time vector on which to map the recordings

        """

        return np.linspace(0, self.duration, self.readings.shape[0])

    @property
    def index(self):
        """

        Determines the index of the channel. In effect, whether the channel is stand-alone or a continuation of another

        Returns:

            Index of a channel

        """

        # strip file name of all superfluous data
        file_name = self._header['OriginalFileName']
        file_name_without_extension = ntpath.basename(file_name).split('.ncs')[0]

        # if the channel is part of a series, return the index. Otherwise, return 0.
        try:
            index = file_name_without_extension.split('_')[1]
            return int(index)
        except:
            return 0

    # _____METHODS_____

    def copy_with_reassigned_readings(self, new_readings):
        """

        Function for copying the current Neuralynx object with different readings.
        Useful when applying filters to the data.

        Args:
            new_readings: new readings to be applied to the old NeuralynxNCS object

        Returns:
            A new NeuralynxNCS object

        """

        new_ncs = copy.deepcopy(self)
        new_ncs.readings = new_readings
        return new_ncs
