#!/usr/bin/env python
# This script bridges AdafruitSensorMeasurement advertisements BLE to MQTT

import time
import signal
import adafruit_ble
import adafruit_ble_broadcastnet

import json
import paho.mqtt.publish as publish

MQTT_HOST = ""

ble = adafruit_ble.BLERadio()
bridge_address = adafruit_ble_broadcastnet.device_address
print("This is BroadcastNet bridge:", bridge_address)


# termination handling - we want to let know that we are shutting down
def sigterm_handler(_signo, _stack_frame):
    publish.single("/home/ble2mqtt/online", 0, hostname=MQTT_HOST)
    sys.exit(0)

signal.signal(signal.SIGINT, sigterm_handler)
signal.signal(signal.SIGTERM, sigterm_handler)


publish.single("/home/ble2mqtt/online", 1, hostname=MQTT_HOST)

for measurement in ble.start_scan(adafruit_ble_broadcastnet.AdafruitSensorMeasurement, interval=0.5):

    reversed_address = [measurement.address.address_bytes[i] for i in range(5, -1, -1)]
    sensor_address = "{:02x}{:02x}{:02x}{:02x}{:02x}{:02x}".format(*reversed_address)

    d = dict()
    d["name"] = measurement.complete_name
    d["rssi"] = measurement.rssi
    d["vbatt"] = measurement.battery_voltage/1000
    d["seq"] = measurement.sequence_number
    print(d)
    publish.single("/home/ble2mqtt/{}".format(sensor_address), json.dumps(d), hostname=MQTT_HOST)

sigterm_handler()

