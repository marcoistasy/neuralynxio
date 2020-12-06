# imports

import numpy as np
import copy


class Channel:

    # A class that holds all information from a neuralynx .ncs file

    def __init__(self, raw_chan_number, time_stamps, raw_readings, hdr_dict):
        """ Init """

        # properties that can be directly set from source
        # self.channel_name = channel_name
        self.time_stamps = time_stamps

        # properties that must be indexed from source
        # self.ad_bitvolts = float(raw_adbitvolts)
        self.channel_number = raw_chan_number[0]
        # self.sampling_frequency = int(raw_sampling_freq)
        self._header = hdr_dict
        # properties that must be computed from source
        self.readings = raw_readings.ravel() # * self.ad_bitvolts  # convert to volts

    # _____PROPERTIES_____

    @property
    def duration(self):
        """

        Returns:
            the duration of the recording (in seconds)

        """

        return self.readings.shape[0] #/ self.sampling_frequency

    @property
    def time_vector(self):
        """

        Returns:

            a 1d time vector on which to map the recordings

        """

        return np.linspace(0, self.duration, self.readings.shape[0])

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
