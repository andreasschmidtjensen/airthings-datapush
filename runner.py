import os
import time

from dotenv import load_dotenv

import reader
from influx_writer import write_to_influxdb

load_dotenv()

while True:
    try:
        print("Reading from Airthings...")
        data = reader.read_values()
        print("Writing result to InfluxDB...")
        write_to_influxdb(data)
    except Exception as e:
        print(e)
    finally:
        time.sleep(int(os.environ["SAMPLE_PERIOD"]))
