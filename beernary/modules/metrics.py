#!/usr/bin/python3

"""
Pushes time series to InfluxDB
"""

from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

class BeernaryInfluxDBClient():
    """Represents the currently used InfluxDB client."""
    def __init__(self, influx_url, influx_token, influx_org, influx_bucket):
        self.client = InfluxDBClient(url=influx_url, token=influx_token, org=influx_org)
        self.influx_bucket = influx_bucket

    def push_draft(self, tap, user, pulses):
        with self.client.write_api(write_options=SYNCHRONOUS) as writer:
            writer.write(bucket=self.influx_bucket, record="draft,user="+str(user)+",tap="+str(tap)+" pulses="+str(pulses))