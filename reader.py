import os
from typing import Dict
import waveplus as wp

def read_values() -> Dict[str, float]:
    serial_number = int(os.environ["AIRTHINGS_SERIALNUMBER"])
    mac_addr = os.environ["AIRTHINGS_MAC_ADDRESS"]

    waveplus = wp.WavePlus(SerialNumber=serial_number, MacAddr=mac_addr)
    try:
        waveplus.search_and_connect()

        # read values
        sensors = waveplus.read()

        # extract
        humidity = { "value": sensors.getValue(wp.SENSOR_IDX_HUMIDITY), "unit": sensors.getUnit(wp.SENSOR_IDX_HUMIDITY) }
        radon_st_avg = { "value": sensors.getValue(wp.SENSOR_IDX_RADON_SHORT_TERM_AVG), "unit": sensors.getUnit(wp.SENSOR_IDX_RADON_SHORT_TERM_AVG) }
        radon_lt_avg = { "value": sensors.getValue(wp.SENSOR_IDX_RADON_LONG_TERM_AVG), "unit": sensors.getUnit(wp.SENSOR_IDX_RADON_LONG_TERM_AVG) }
        temperature = { "value": sensors.getValue(wp.SENSOR_IDX_TEMPERATURE), "unit": sensors.getUnit(wp.SENSOR_IDX_TEMPERATURE) }
        pressure = { "value": sensors.getValue(wp.SENSOR_IDX_REL_ATM_PRESSURE), "unit": sensors.getUnit(wp.SENSOR_IDX_REL_ATM_PRESSURE) }
        CO2_lvl = { "value": sensors.getValue(wp.SENSOR_IDX_CO2_LVL), "unit": sensors.getUnit(wp.SENSOR_IDX_CO2_LVL) }
        VOC_lvl = { "value": sensors.getValue(wp.SENSOR_IDX_VOC_LVL), "unit": sensors.getUnit(wp.SENSOR_IDX_VOC_LVL) }

        # Print data
        data = {
            "humidity": humidity,
            "radon_st_avg": radon_st_avg,
            "radon_lt_avg": radon_lt_avg,
            "temperature": temperature,
            "pressure": pressure,
            "CO2_lvl": CO2_lvl,
            "VOC_lvl": VOC_lvl,
        }

        return data

    finally:
        waveplus.disconnect()