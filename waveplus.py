import struct
import sys
from bluepy.btle import UUID, Peripheral, Scanner, DefaultDelegate

# ====================================
# Utility functions for WavePlus class
# ====================================

def parseSerialNumber(ManuDataHexStr):
    if (ManuDataHexStr == None or ManuDataHexStr == "None"):
        SN = "Unknown"
    else:
        ManuData = bytearray.fromhex(ManuDataHexStr)

        if (((ManuData[1] << 8) | ManuData[0]) == 0x0334):
            SN  =  ManuData[2]
            SN |= (ManuData[3] << 8)
            SN |= (ManuData[4] << 16)
            SN |= (ManuData[5] << 24)
        else:
            SN = "Unknown"
    return SN

# ===============================
# Class WavePlus
# ===============================

class WavePlus():

    def __init__(self, SerialNumber: int = None, MacAddr: str = None):
        self.periph        = None
        self.curr_val_char = None
        self.MacAddr       = MacAddr
        self.SN            = SerialNumber
        self.uuid          = UUID("b42e2a68-ade7-11e4-89d3-123b93f75cba")

    @staticmethod
    def find_mac_from_serialnumber(serial_number: str, search_count: int = 50):
        print(f"- searching for Airthing with serialnumber {SN}")
        scanner = Scanner().withDelegate(DefaultDelegate())
        iteration = 0
        while iteration < search_count:
            devices      = scanner.scan(0.1) # 0.1 seconds scan period
            iteration += 1
            for dev in devices:
                ManuData = dev.getValueText(255)
                SN = parseSerialNumber(ManuData)
                if (SN == serial_number):
                    print(f"- found Airthing with serialnumber {SN}: {dev.addr}")
                    return dev.addr

        return None

    def connect(self):
        if (self.periph is None):
            print(f"- connecting to {self.MacAddr}")
            self.periph = Peripheral(self.MacAddr)
        
        if (self.curr_val_char is None):
            self.curr_val_char = self.periph.getCharacteristics(uuid=self.uuid)[0]

    def search_and_connect(self):
        # Auto-discover device on first connection
        if (self.MacAddr is None):
            self.MacAddr = WavePlus.find_mac_from_serialnumber(self.SN)

            if (self.MacAddr is None):
                print("ERROR: Could not find device.")
                print("GUIDE: (1) Please verify the serial number.")
                print("       (2) Ensure that the device is advertising.")
                print("       (3) Retry connection.")
                sys.exit(1)

        # Connect to device
        self.connect()

    def read(self):
        if (self.curr_val_char is None):
            print("ERROR: Devices are not connected.")
            sys.exit(1)
        rawdata = self.curr_val_char.read()
        rawdata = struct.unpack('<BBBBHHHHHHHH', rawdata)
        sensors = Sensors()
        sensors.set(rawdata)
        return sensors

    def disconnect(self):
        if self.periph is not None:
            self.periph.disconnect()
            self.periph = None
            self.curr_val_char = None

# ===================================
# Class Sensor and sensor definitions
# ===================================

NUMBER_OF_SENSORS               = 7
SENSOR_IDX_HUMIDITY             = 0
SENSOR_IDX_RADON_SHORT_TERM_AVG = 1
SENSOR_IDX_RADON_LONG_TERM_AVG  = 2
SENSOR_IDX_TEMPERATURE          = 3
SENSOR_IDX_REL_ATM_PRESSURE     = 4
SENSOR_IDX_CO2_LVL              = 5
SENSOR_IDX_VOC_LVL              = 6

class Sensors():
    def __init__(self):
        self.sensor_version = None
        self.sensor_data    = [None]*NUMBER_OF_SENSORS
        self.sensor_units   = ["%rH", "Bq/m3", "Bq/m3", "degC", "hPa", "ppm", "ppb"]

    def set(self, rawData):
        self.sensor_version = rawData[0]
        if (self.sensor_version == 1):
            self.sensor_data[SENSOR_IDX_HUMIDITY]             = rawData[1]/2.0
            self.sensor_data[SENSOR_IDX_RADON_SHORT_TERM_AVG] = self.conv2radon(rawData[4])
            self.sensor_data[SENSOR_IDX_RADON_LONG_TERM_AVG]  = self.conv2radon(rawData[5])
            self.sensor_data[SENSOR_IDX_TEMPERATURE]          = rawData[6]/100.0
            self.sensor_data[SENSOR_IDX_REL_ATM_PRESSURE]     = rawData[7]/50.0
            self.sensor_data[SENSOR_IDX_CO2_LVL]              = rawData[8]*1.0
            self.sensor_data[SENSOR_IDX_VOC_LVL]              = rawData[9]*1.0
        else:
            print("ERROR: Unknown sensor version.\n")
            print("GUIDE: Contact Airthings for support.\n")
            sys.exit(1)

    def conv2radon(self, radon_raw):
        radon = "N/A" # Either invalid measurement, or not available
        if 0 <= radon_raw <= 16383:
            radon  = radon_raw
        return radon

    def getValue(self, sensor_index):
        return self.sensor_data[sensor_index]

    def getUnit(self, sensor_index):
        return self.sensor_units[sensor_index]