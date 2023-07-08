import pyvisa
import time
"""
https://www.youtube.com/watch?v=ku9uRmr8sCo&list=PLMFn2UaPBVfWVjCbQh_DsJknlwpVkiIhh


This Short series is an Introduction level 
#Keysight #SCPI #python
course to Test Instrumentation Automation 
"""
rm = pyvisa.ResourceManager()
vi = rm.open_resource("C:\\Users\\vimarais\\Documents\\AcquisitionVariant.vi")

# Configurer les paramètres si nécessaire

vi.write("RUN")
time.sleep(5)  # Attendre 5 secondes (ou la durée nécessaire à votre VI)

vi.close()
