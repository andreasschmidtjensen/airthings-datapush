import os
from typing import Dict

from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

# You can generate an API token from the "API Tokens Tab" in the UI
token = os.environ["INFLUX_TOKEN"]
org = os.environ["INFLUX_ORG"]
bucket = os.environ["INFLUX_BUCKET"]

def write_to_influxdb(data: Dict[str, float]):
    with InfluxDBClient(url=os.environ["INFLUX_URL"], token=token, org=org) as client:
        write_api = client.write_api(write_options=SYNCHRONOUS)

        sequence = [f"airquality,host={os.uname()[1]} {k}={v}" for k, v in data.items()]
        write_api.write(bucket, org, sequence)

    client.close()