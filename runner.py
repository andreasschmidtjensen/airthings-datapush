import os
import time
import reader
from influx_writer import write_to_influxdb

while True:
    try:
        print("Reading from Airthings...")
        data = reader.read_values()
        print("Writing result to InfluxDB...")
        write_to_influxdb(data)

        time.sleep(os.environ["SAMPLE_PERIOD"])
    except Exception as e:
        print(e)
