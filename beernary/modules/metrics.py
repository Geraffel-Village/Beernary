#!/usr/bin/python3

"""
Pushes time series to InfluxDB
"""

from influxdb import InfluxDBClient
from loguru import logger

class BeernaryInfluxDBClient():
    """Represents the currently used InfluxDB client."""
    def __init__(self, influx_host, influx_port, influx_user, influx_password, influx_database):
        self.client = InfluxDBClient(host=influx_host, port=influx_port, username=influx_user, password=influx_password, database=influx_database)

    def push_draft(self, tap, user, nick, pulses):
        influx_line = "draft,user="+str(user)+",nick="+str(nick)+",tap="+str(tap)+" pulses="+str(pulses)
        logger.debug(f"Writing influxdb line: {influx_line}")
        self.client.write_points(points=influx_line, protocol="line")
