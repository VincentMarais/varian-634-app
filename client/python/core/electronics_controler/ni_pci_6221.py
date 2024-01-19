"""
The objective of this program is to facilitate the reading 
of voltage across photodiodes using an NI-PCI 6221 card. 
Refer to the documentation for NI-PCI 6221, accessible at the following 
link: [NI-PCI 6221 Specs]
(https://www.ni.com/docs/fr-FR/bundle/pci-pxi-usb-6221-specs/page/specs.html).

The ultimate goal is to measure the intensity 
of light after passing through a cuvette and 
subsequently calculate the absorbance of 
the chemical sample under analysis.

Here are the key points:

1. The signal generated by the photodiode, 
as detailed in the 2023-2024 report, 
manifests as a square signal with a negative amplitude.

2. According to the photodiode 
theory outlined in the appendix report of 2022-2023, 
the voltage from the photodiode is directly 
proportional to the received light intensity.

3. Therefore, by measuring 
the minimum amplitude of 
the square signal produced by the photodiode, 
it becomes possible to quantify the intensity 
of the received light. This information 
is crucial for subsequent calculations, 
especially in determining the absorbance 
of the analyzed chemical sample.
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
        # cf link : Figure 8. NI PCI/PXI-6221 Pinout
        # Dev1/ai0 : pin 68 / pin 34 (ground)
        # Dev1/ai1 : pin 33 / pin 66 (ground)
        self.channels = ['Dev1/ai0', 'Dev1/ai1']
        self.samples_per_channel = 30000  # Sampling frequency
        self.sample_rate = 250000
        
        # Characteristics of square wave (xenon arc lamp control signal)
        self.frequency = np.array([20.0])
        self.duty_cycle = np.array([0.5])
        # cf link : Figure 8. NI PCI/PXI-6221 Pinout
        # /Dev1/ctr0 : pin 2 / pin 36 (ground)
        self.device = '/Dev1/ctr0'

    def configure_task_voltage(self, task_voltage, physical_channel):
        """
        Configures the analog voltage measurement task.

        Parameters:
        - task_voltage : nidaqmx task object.
        - physical_channel (str) : Analog input physical_channel to configure (e.g., 'Dev1/ai0').
        """
        # terminal_config = TerminalConfiguration.DIFF 
        # because we measure the potential difference between two ports of the NI PCI/PXI-6221 Pinout
        # e.g., The voltage at Dev1/ai0 terminals = potential_pin_68 - potential_pin_34
        task_voltage.ai_channels.add_ai_voltage_chan(physical_channel, terminal_config=TerminalConfiguration.DIFF)
        # sample_mode=AcquisitionType.FINITE : Acquire or generate a finite number of samples. 
        # But why is it better than CONTINUOUS?
        # Better...
        task_voltage.timing.cfg_samp_clk_timing(self.sample_rate, samps_per_chan=self.samples_per_channel, sample_mode=AcquisitionType.FINITE)


    def configure_task_impulsion(self, task_impulsion):
        """
        Configures the pulse generation task.

        Parameters:
        - task_impulsion : nidaqmx task object.
        """

        task_impulsion.co_channels.add_co_pulse_chan_freq(self.device, freq=self.frequency[0], duty_cycle=self.duty_cycle[0], initial_delay=0.0)
        # But why is it better than CONTINUOUS is better for generating a square wave?
        task_impulsion.timing.cfg_implicit_timing(sample_mode=AcquisitionType.CONTINUOUS)
        task_impulsion.start()
    
    def clear_tasks(self, task):
        task.close()

    def measure_voltage(self, task, physical_channel):
        """
        Measures voltage across the specified physical_channel.

        Parameters:
        - task : nidaqmx task object.
        - physical_channel (str) : Analog input physical_channel to measure (e.g., 'Dev1/ai0').

        Returns:
        - voltages (list float): List of measured voltages.
        """

        voltages = []
        self.configure_task_voltage(task, physical_channel)
        voltages = task.read(number_of_samples_per_channel=self.samples_per_channel)
        task.stop()

        return voltages

    def measure_mean_voltage(self, task, physical_channel):
        """
        Measures the mean voltage.

        Parameters:
        - task : nidaqmx task object.

        Returns:
        - mean (float) : Mean of the measured voltages.
        """
        voltages = []
        self.configure_task_voltage(task, physical_channel)
        voltages = task.read(number_of_samples_per_channel=self.samples_per_channel)
        task.stop()
        voltages = np.array(self.measure_voltage(task, physical_channel))
        mean = np.mean(voltages)
        return mean

    def acquire_data_voltages_chemical_kinetics(self, time_acquisition, delay_between_measurements, physical_channel):
        """
        Acquires minimum voltages from the voltage measurement task.

        Parameters:
        - time_acquisition (float) : Acquisition duration in seconds (optional).
        - delay_between_measurements (float): Delay between consecutive measurements in seconds.
        - physical_channel (str) : Analog input physical_channel to configure (e.g., 'Dev1/ai0').

        Returns:
        - moment (list float) : List of time instants.
        - voltages (list float) : List of minimum measured voltages.
        """

        voltages = []
        moment = [0]

        with nidaqmx.Task() as read_voltage:
            start_time = time.time()

            while time.time() - start_time < time_acquisition:  # Loop for the specified duration
                start_time_temp = time.time()
                # Data acquisition
                data = self.measure_mean_voltage(read_voltage, physical_channel)
                voltages.append(data)
                instant_time = time.time() - start_time_temp
                # Loop for wait 
                while instant_time < delay_between_measurements:
                    instant_time += time.time() - start_time_temp
                moment.append(instant_time)
        return moment, voltages

    def voltage_acquisition_scanning_baseline(self, physical_channel):
        """
        Performs voltage acquisition based on the task type.

        Parameters:
        - physical_channel (str) : Analog input physical_channel to measure (e.g., 'Dev1/ai0').

        Returns:
        - min_voltages (float) :  Mean of the measured voltages.
        """

        with nidaqmx.Task() as task_voltage, nidaqmx.Task() as task_impulsion:
            self.configure_task_impulsion(task_impulsion)
            self.configure_task_voltage(task_voltage, physical_channel)
            min_voltages = self.measure_mean_voltage(task_voltage, physical_channel)
            task_impulsion.stop()
        return min_voltages

    def voltage_acquisition_chemical_kinetics(self, physical_channel, time_acquisition, time_per_acquisition):
        """
        Performs voltage acquisition based on the task type.

        Parameters:
        - physical_channel (str) : Analog input physical_channel to measure (e.g., 'Dev1/ai0').
        - time_acquisition (int) : Acquisition duration in seconds (optional).
        - time_per_acquisition (int) : Time between consecutive measurements.

        Returns:
        - voltages (list float) : List of measured voltages.
        """

        with nidaqmx.Task() as task_voltage, nidaqmx.Task() as task_impulsion:
            self.configure_task_impulsion(task_impulsion)
            self.configure_task_voltage(task_voltage, physical_channel)
            voltages = self.acquire_data_voltages_chemical_kinetics(time_acquisition, time_per_acquisition, physical_channel)
            task_impulsion.stop()
        return voltages

    def sensors_state(self, board, pin):
        """
        Provides the digital state of a sensor: True or False.
        Parameters:
            - board (class) : class Arduino of pyfirmata 
            - pin (int) : output pin of sensor on the Arduino 
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
    # Test sensors_state 
    acqui_voltage.sensors_state(BOARD, PIN_SENSOR)


    # NI PCI 6221
    TASK = nidaqmx.Task()
    CHANNEL = ['Dev1/ai0']
    
    # display library
    import matplotlib.pyplot as plt

    # Test measure_voltage
    data_y = acqui_voltage.measure_voltage(TASK, CHANNEL[0])
    x_data = np.arange(0, len(data_y), 1)
    plt.plot(x_data, data_y)
    plt.xlabel('samples')
    plt.ylabel('Voltage (Volt)')
    plt.legend()
    plt.grid()
    plt.tight_layout()
    plt.show()
    # Test measure_mean_voltage
    TASK.close()



# Test voltage_acquisition_scanning_baseline
    #print(acqui_voltage.voltage_acquisition_scanning_baseline(CHANNEL[0]))

"""    # Test voltage_acquisition_chemical_kinetics
    TIME_ACQUISITION = 10
    TIME_PER_ACQUISITION = 1
    print(acqui_voltage.voltage_acquisition_chemical_kinetics(CHANNEL[0], TIME_ACQUISITION, TIME_PER_ACQUISITION))
"""