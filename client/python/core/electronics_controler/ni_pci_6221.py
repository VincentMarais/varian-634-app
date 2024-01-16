"""
This program allows reading the voltage across the photodiodes using an NI-PCI 6221 card.
Doc NI-PCI 6221
https://www.ni.com/docs/fr-FR/bundle/pci-pxi-usb-6221-specs/page/specs.html
"""

import time
import numpy as np
import nidaqmx
from nidaqmx.constants import AcquisitionType, TerminalConfiguration
from pyfirmata import util, INPUT

class VoltageAcquisition:
    """
    A class that allows reading the voltage across the photodiodes using an NI-PCI 6221 card.
    """

    def __init__(self):
        """
        Initializes an instance of the VoltageAcquisition class.

        Parameters:
        - channels : List of acquisition channels (e.g., ['Dev1/ai0', 'Dev1/ai1']).
        - sample_rate : Sampling rate in samples per second (Hz).
        - samples_per_channel : Number of samples to acquire per channel.
        """

        # Voltage acquisition parameters
        self.channels = ['Dev1/ai0', 'Dev1/ai1']
        self.samples_per_channel = 250000  # Sampling frequency
        self.sample_rate = 30000

        # Characteristics of square wave (xenon arc lamp control signal)
        self.frequency = np.array([20.0])
        self.duty_cycle = np.array([0.5])
        self.device = '/Dev1/ctr0'

    def configure_task_voltage(self, task, channel):
        """
        Configures the analog voltage measurement task.

        Parameters:
        - task : nidaqmx task object.
        - channel : Analog input channel to configure (e.g., 'Dev1/ai0').
        """

        task.ai_channels.add_ai_voltage_chan(channel, terminal_config=TerminalConfiguration.DIFF)
        task.timing.cfg_samp_clk_timing(self.sample_rate, samps_per_chan=self.samples_per_channel, sample_mode=AcquisitionType.FINITE)

    def configure_task_impulsion(self, task):
        """
        Configures the pulse generation task.

        Parameters:
        - task : nidaqmx task object.
        """

        task.co_channels.add_co_pulse_chan_freq(self.device, freq=self.frequency[0], duty_cycle=self.duty_cycle, initial_delay=0.0)
        task.timing.cfg_implicit_timing(sample_mode=AcquisitionType.CONTINUOUS)
        task.start()

    def measure_voltage(self, task, channel):
        """
        Measures voltage across the specified channel.

        Parameters:
        - task : nidaqmx task object.
        - channel : Analog input channel to measure (e.g., 'Dev1/ai0').

        Returns:
        - voltages : List of measured voltages.
        """

        voltages = []
        self.configure_task_voltage(task, channel)
        voltages = task.read(number_of_samples_per_channel=self.samples_per_channel)
        task.stop()
        return voltages

    def measure_mean_voltage(self, task):
        """
        Measures the mean voltage.

        Parameters:
        - task : nidaqmx task object.

        Returns:
        - mean : Mean of the measured voltages.
        """

        min_voltages = []
        frequence = int(self.frequency[0])
        for _ in range(frequence):
            # Data acquisition
            data = task.read(number_of_samples_per_channel=self.samples_per_channel)
            # Conversion of data into a numpy array for easy calculations
            np_data = np.array(data)

            # Find and store the minimum
            min_voltage = np.min(np_data)
            min_voltages.append(min_voltage)
        task.stop()
        mean = np.mean(min_voltages)
        return mean

    def acquire_data_voltages_chemical_kinetics(self, time_acquisition, delay_between_measurements):
        """
        Acquires minimum voltages from the voltage measurement task.

        Parameters:
        - time_acquisition : Acquisition duration in seconds (optional).
        - delay_between_measurements : Delay between consecutive measurements in seconds.

        Returns:
        - moment : List of time instants.
        - voltages : List of minimum measured voltages.
        """

        voltages = []
        moment = [0]

        with nidaqmx.Task() as read_voltage:
            start_time = time.time()

            while time.time() - start_time < time_acquisition:  # Loop for the specified duration
                start_time_temp = time.time()
                # Data acquisition
                data = self.measure_mean_voltage(read_voltage)
                voltages.append(data)
                instant_time = time.time() - start_time_temp
                while instant_time < delay_between_measurements:
                    instant_time += time.time() - start_time_temp
                moment.append(instant_time)
            read_voltage.stop()
        return moment, voltages

    def voltage_acquisition_scanning_baseline(self, channel):
        """
        Performs voltage acquisition based on the task type.

        Parameters:
        - channel : Index of the channel to acquire.

        Returns:
        - Mean of the measured minimum voltages.
        """

        with nidaqmx.Task() as task_voltage, nidaqmx.Task() as task_impulsion:
            self.configure_task_impulsion(task_impulsion)
            self.configure_task_voltage(task_voltage, self.channels[channel])
            min_voltages = self.measure_mean_voltage(task_voltage)
            task_impulsion.stop()
            task_voltage.stop()
        return min_voltages

    def voltage_acquisition_chemical_kinetics(self, channel, time_acquisition, time_per_acquisition):
        """
        Performs voltage acquisition based on the task type.

        Parameters:
        - channel : Index of the channel to acquire.
        - time_acquisition : Acquisition duration in seconds (optional).
        - time_per_acquisition : Time between consecutive measurements.

        Returns:
        - voltages : List of measured voltages.
        """

        with nidaqmx.Task() as task_voltage, nidaqmx.Task() as task_impulsion:
            self.configure_task_impulsion(task_impulsion)
            self.configure_task_voltage(task_voltage, self.channels[channel])
            voltages = self.acquire_data_voltages_chemical_kinetics(time_acquisition, time_per_acquisition)
            task_impulsion.stop()
            task_voltage.stop()
        return voltages

    def sensors_state(self, board, pin):
        """
        Provides the digital state of a sensor: True or False.
        """
        # Configure digital port 3 as input
        board.digital[pin].mode = INPUT

        # Create an Iterator instance to not miss incoming data
        it = util.Iterator(board)
        it.start()

        # Allow the iterator to start
        time.sleep(1)
        
            # Read the value of digital port 3
        digital_value = board.digital[pin].read()

            # Display the value
        print(f"Value read on digital port {pin}:", digital_value)

            # Wait a bit before reading again
        time.sleep(0.1)

if __name__ == "__main__":
    acqui_voltage = VoltageAcquisition()

    from pyfirmata import Arduino
    # Arduino
    BOARD = Arduino('COM9')
    PIN_SENSOR = 5
    acqui_voltage.sensors_state(BOARD, PIN_SENSOR)

    import matplotlib.pyplot as plt

    # NI PCI 6221
    TASK = nidaqmx.Task()
    CHANNEL = 'Dev1/ai0'

    data_y = acqui_voltage.measure_voltage(TASK, CHANNEL)
    x_data = np.arange(0, len(data_y), 1)
    plt.plot(x_data, data_y)
    plt.xlabel('samples')
    plt.ylabel('Voltage (Volt)')
    plt.legend()
    plt.grid()
    plt.tight_layout()
    plt.show()
