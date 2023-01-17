import mne
import numpy as np
import param
import matplotlib.pyplot as plt
import os
import numpy as np
import pandas as pd
import mne
import sys


class panThopkins(param.Parameterized):
    #inputData = param.Parameter(default=raw)
    signalFreq = param.Number(default=250)
    windowSizeRunningWindow = param.Number(default=0.15)
    windowSizeEvalWindow = param.Number(default=0.15)

    def setVars(self, signal, signalFreq):
        self.signal = signal
        self.signalFreq = signalFreq
        self.N = len(signal)
        # time stamps of measurements
        self.timestamp = np.arange(
            0, self.N/self.signalFreq, 1/self.signalFreq)
        super().__init__()

    def run(self, dataObj, *events):
        print("doing calculations")
        # run init again
        self.setVars(dataObj, self.signalFreq)
        # run the filters
        self.timestamp = np.arange(0, len(self.signal))
        self.integration_signal, self.band_pass_signal, self.derivative_signal, self.square_signal = self.solve(
            self.signal)
        # the run QRS detection
        res = self.detect_peaks(dataObj, self.signalFreq,
                                self.windowSizeRunningWindow)
        res_dict = {"features": {
            "peaks": res,
            "integration_signal": self.integration_signal,
            "band_pass_signal": self.band_pass_signal,
            "derivative_signal": self.derivative_signal,
            "square_signal": self.square_signal,
            "sfreq": self.signalFreq,
        },  "name": "panThopkins"}
        return res_dict

    def low_pass_filter(self, signal):
        '''
        Low Pass Filter
        :param signal: input signal
        :return: processed signal

        '''
        low_pass_signal = signal.copy()
        for time in self.timestamp:
            curr = signal[time]

            if (time >= 1):
                curr += 2*low_pass_signal[time-1]

            if (time >= 2):
                curr -= low_pass_signal[time-2]

            if (time >= 6):
                curr -= 2*signal[time-6]

            if (time >= 12):
                curr += signal[time-12]

            low_pass_signal[time] = curr
        low_pass_signal = low_pass_signal / max(abs(low_pass_signal))
        return low_pass_signal

    def high_pass_filter(self, signal):
        '''
        High Pass Filter
        :param signal: input signal
        :return: prcoessed signal

        '''

        high_pass_signal = signal.copy()

        for time in self.timestamp:
            curr = -1*signal[time]

            if (time >= 16):
                curr += 32*signal[time-16]

            if (time >= 1):
                curr -= high_pass_signal[time-1]

            if (time >= 32):
                curr += signal[time-32]

            high_pass_signal[time] = curr
        high_pass_signal = high_pass_signal/max(abs(high_pass_signal))
        return high_pass_signal

    def band_pass_filter(self, signal):
        '''
        Band Pass Filter
        :param signal: input signal
        :return: processed signal

        Methodology/Explaination (min 2-3 lines):
        A bandpass filter is created by a combination of a high pass filter and a low pass filter.
        The signal is first filtered with a low pass filter and the output of the low pass filter
        is given to a high pass filter. The function of the filter is to eliminate
        noise due to muscle contractions, T-waves, or any other noise present in the data. The implementation
        is on the lines with Pan Tompkin's research paper
        '''
        low_pass_signal = self.low_pass_filter(signal)
        self.band_pass_signal = self.high_pass_filter(low_pass_signal)

        return self.band_pass_signal

    def derivative(self, signal):
        '''
        Derivative Filter
        :param signal: input signal
        :return: prcoessed signal

        Methodology/Explaination (min 2-3 lines):
        The implementation is as given in the research paper. It is used
        to get the slope information for the QRS complex. It takes the
        filtered signal as an input.
        '''
        T = 1/self.signalFreq
        self.derivative_signal = signal.copy()

        for time in self.timestamp:
            curr = 0

            if (time >= 2):
                curr -= signal[time-2]

            if (time >= 1):
                curr -= 2*signal[time-1]

            if (time < len(self.timestamp)-1):
                curr += 2*signal[time+1]

            if (time < len(self.timestamp)-2):
                curr += signal[time+2]
            self.derivative_signal[time] = (curr/(8*T))

        return self.derivative_signal

    def squaring(self, signal):
        '''
        Squaring the Signal
        :param signal: input signal
        :return: prcoessed signal

        Methodology/Explaination (min 2-3 lines):
        This just squares all the values in the waveform. It provides a non-linear amplification
        to the higher frequency components of QRS complexes in the derivative signal.
        '''
        return np.square(signal)

    def moving_window_integration(self, signal, window_size=0.15):
        '''
        Moving Window Integrator
        :param signal: input signal
        :return: prcoessed signal

        Methodology/Explaination (min 2-3 lines):
        It is a kind of running average within a window of certain size. Here I took a window
        of 0.15 seconds. This basically serves as a tool for detection and finding features
        of QRS complexes and R peaks.
        '''
        WINDOW_SIZE = window_size*self.signalFreq
        moving_window_signal = signal.copy()
        for time in self.timestamp:
            index = 0
            curr = 0
            while (index < WINDOW_SIZE):
                if (time < index):
                    break
                curr += signal[time-index]
                index += 1

            moving_window_signal[time] = curr/index
        return moving_window_signal

    def solve(self, signal):
        '''
        Solver, Combines all the above functions
        :param signal: input signal
        :return: prcoessed signal

        First the signal is filtered using a band pass filter, then passed in a differentiator
        followed by square wave generator, and then into a moving window integrator. The final signal is
        returned to to the caller.
        '''

        self.band_pass_signal = self.band_pass_filter(signal.copy())
        self.derivative_signal = self.derivative(self.band_pass_signal.copy())
        self.square_signal = self.squaring(self.derivative_signal.copy())
        moving_window_avg_signal = self.moving_window_integration(
            self.square_signal.copy())

        return moving_window_avg_signal, self.band_pass_signal, self.derivative_signal, self.square_signal

    def detect_peaks(self, ecg_signal, signalFreq, window_size=0.15):
        # Initialization of variables

        possible_peaks = []
        signal_peaks = []
        r_peaks = []
        # running estimate of the signal peak
        SPKI = 0
        # running estimate of the signal peak
        SPKF = 0
        # running estimate of the noise peak
        NPKI = 0
        # running estimate of the noise peak
        NPKF = 0
        rr_avg_one = []
        # First Integrated result threshold
        THRESHOLDI1 = 0
        # First Filtered result threshold
        THRESHOLDF1 = 0
        rr_avg_two = []
        # Second Integrated result threshold
        THRESHOLDI2 = 0
        # Second Filtered result threshold
        THRESHOLDF2 = 0
        # T wave detection flag
        is_T_found = 0
        # A search window of samples corresponding to 0.15 seconds
        window = round(window_size * signalFreq)

        # Stage I: Fudicial Mark possible_peaks on the integrated signal
        FM_peaks = []
        # Smoothening the integration signal
        self.integration_signal_smooth = np.convolve(
            self.integration_signal, np.ones((20,)) / 20, mode='same')
        localDiff = np.diff(self.integration_signal_smooth)
        # finding local maxima using difference array and ignoring
        # possible_peaks before initialization step i.e before signalFreq

        for i in range(1, len(localDiff)):
            if i-1 > 2*signalFreq and localDiff[i-1] > 0 and localDiff[i] < 0:
                FM_peaks.append(i-1)

        # Find out the possbile peaks for all the local maximas
        for index in range(len(FM_peaks)):

            # Finding maximum value position in the current search window
            current_peak = FM_peaks[index]
            left_limit = max(current_peak-window, 0)
            right_limit = min(current_peak+window+1,
                              len(self.band_pass_signal))
            max_index = -1
            max_value = -sys.maxsize
            for i in range(left_limit, right_limit):
                if(self.band_pass_signal[i] > max_value):
                    max_value = self.band_pass_signal[i]
                    max_index = i
            if (max_index != -1):
                possible_peaks.append(max_index)

            if (index == 0 or index > len(possible_peaks)):
                # if first peak
                if (self.integration_signal[current_peak] >= THRESHOLDI1):
                    SPKI = 0.125 * \
                        self.integration_signal[current_peak] + 0.875 * SPKI
                    if possible_peaks[index] > THRESHOLDF1:
                        SPKF = 0.125 * \
                            self.band_pass_signal[index] + 0.875 * SPKF
                        signal_peaks.append(possible_peaks[index])
                    else:
                        NPKF = 0.125 * \
                            self.band_pass_signal[index] + 0.875 * NPKF

                elif((self.integration_signal[current_peak] > THRESHOLDI2 and self.integration_signal[current_peak] < THRESHOLDI1) or (self.integration_signal[current_peak] < THRESHOLDI2)):
                    NPKI = 0.125 * \
                        self.integration_signal[current_peak] + 0.875 * NPKI
                    NPKF = 0.125 * self.band_pass_signal[index] + 0.875 * NPKF

            else:
                RRAVERAGE1 = np.diff(
                    FM_peaks[max(0, index-8):index + 1]) / signalFreq
                rr_one_mean = np.mean(RRAVERAGE1)
                rr_avg_one.append(rr_one_mean)
                limit_factor = rr_one_mean

                if (index >= 8):
                    # calculate RR limits and rr_avg_two
                    for RR in RRAVERAGE1:
                        if RR > RR_LOW_LIMIT and RR < RR_HIGH_LIMIT:
                            rr_avg_two.append(RR)
                            if (len(rr_avg_two) == 9):
                                rr_avg_two.pop(0)
                                limit_factor = np.mean(rr_avg_two)
                # set the RR limits
                if (len(rr_avg_two) == 8 or index < 8):
                    RR_LOW_LIMIT = 0.92 * limit_factor
                    RR_HIGH_LIMIT = 1.16 * limit_factor
                    RR_MISSED_LIMIT = 1.66 * limit_factor

                # Decrease the thresholds to half, if irregular beats detected
                if rr_avg_one[-1] < RR_LOW_LIMIT or rr_avg_one[-1] > RR_MISSED_LIMIT:
                    THRESHOLDI1 = THRESHOLDI1/2
                    THRESHOLDF1 = THRESHOLDF1/2

                # If current RR interval is greater than RR_MISSED_LIMIT perform search back
                curr_rr_interval = RRAVERAGE1[-1]
                search_back_window = round(curr_rr_interval * signalFreq)
                if curr_rr_interval > RR_MISSED_LIMIT:
                    left_limit = current_peak - search_back_window + 1
                    right_limit = current_peak + 1
                    search_back_max_index = -1
                    max_value = -sys.maxsize
                    # local maximum in the search back interval
                    for i in range(left_limit, right_limit):
                        if (self.integration_signal[i] > THRESHOLDI1 and self.integration_signal[i] > max_value):
                            max_value = self.integration_signal[i]
                            search_back_max_index = i

                    if (search_back_max_index != -1):
                        SPKI = 0.25 * \
                            self.integration_signal[search_back_max_index] + \
                            0.75 * SPKI
                        THRESHOLDI1 = NPKI + 0.25 * (SPKI - NPKI)
                        THRESHOLDI2 = 0.5 * THRESHOLDI1
                        # finding peak using search back of 0.15 seconds
                        left_limit = search_back_max_index - \
                            round(0.15 * signalFreq)
                        right_limit = min(len(self.band_pass_signal),
                                          search_back_max_index)

                        search_back_max_index2 = -1
                        max_value = -sys.maxsize
                        # local maximum in the search back interval
                        for i in range(left_limit, right_limit):
                            if(self.band_pass_signal[i] > THRESHOLDF1 and self.band_pass_signal[i] > max_value):
                                max_value = self.band_pass_signal[i]
                                search_back_max_index2 = i

                        # QRS complex detected
                        if self.band_pass_signal[search_back_max_index2] > THRESHOLDF2:
                            SPKF = 0.25 * \
                                self.band_pass_signal[search_back_max_index2] + \
                                0.75 * SPKF
                            THRESHOLDF1 = NPKF + 0.25 * (SPKF - NPKF)
                            THRESHOLDF2 = 0.5 * THRESHOLDF1
                            signal_peaks.append(search_back_max_index2)

                # T-wave detection
                if (self.integration_signal[current_peak] >= THRESHOLDI1):
                    if (curr_rr_interval > 0.20 and curr_rr_interval < 0.36 and index > 0):
                        # slope of current waveformm which is most probabaly a T-wave, using mean width of QRS complex 0.075
                        current_slope = max(
                            np.diff(self.integration_signal[current_peak - round(signalFreq * 0.075):current_peak + 1]))
                        # slope of the preceding waveform, which is mosty probabaly QRS complex
                        previous_slope = max(np.diff(
                            self.integration_signal[FM_peaks[index - 1] - round(signalFreq * 0.075): FM_peaks[index - 1] + 1]))
                        if (current_slope < 0.5 * previous_slope):
                            NPKI = 0.125 * \
                                self.integration_signal[current_peak] + \
                                0.875 * NPKI
                            is_T_found = 1
                    #  This is a signal peak
                    if (not is_T_found):
                        SPKI = 0.125 * \
                            self.integration_signal[current_peak] + \
                            0.875 * SPKI
                        # check if it is present in the possible peaks otherwise it is a noise peak
                        if possible_peaks[index] > THRESHOLDF1:
                            SPKF = 0.125 * \
                                self.band_pass_signal[index] + 0.875 * SPKF
                            signal_peaks.append(possible_peaks[index])
                        else:
                            NPKF = 0.125 * \
                                self.band_pass_signal[index] + 0.875 * NPKF

                elif ((self.integration_signal[current_peak] > THRESHOLDI1 and self.integration_signal[current_peak] < THRESHOLDI2) or (self.integration_signal[current_peak] < THRESHOLDI1)):
                    NPKI = 0.125 * \
                        self.integration_signal[current_peak] + 0.875 * NPKI
                    NPKF = 0.125 * self.band_pass_signal[index] + 0.875 * NPKF

            THRESHOLDI1 = NPKI + 0.25 * (SPKI - NPKI)
            THRESHOLDF1 = NPKF + 0.25 * (SPKF - NPKF)
            THRESHOLDI2 = 0.5 * THRESHOLDI1
            THRESHOLDF2 = 0.5 * THRESHOLDF1
            is_T_found = 0

        # searching in ECG signal to increase accuracy
        for i in np.unique(signal_peaks):
            i = int(i)
            window = round(0.2 * signalFreq)
            left_limit = i-window
            right_limit = min(i+window+1, len(ecg_signal))
            max_value = -sys.maxsize
            max_index = -1
            for i in range(left_limit, right_limit):
                if (ecg_signal[i] > max_value):
                    max_value = ecg_signal[i]
                    max_index = i

            r_peaks.append(max_index)

        return np.array(r_peaks)
