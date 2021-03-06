#!/usr/bin/env python
# (c) 2021 Andreas Böhler
# License: Apache 2.0

import paho.mqtt.client as mqtt
import json
import yaml
import os
import sys
import time
import socket
import threading
import socketserver
import uuid

if os.path.exists('/config/rflink2tcp.yaml'):
    fp = open('/config/rflink2tcp.yaml', 'r')
    config = yaml.safe_load(fp)
elif os.path.exists('rflink2tcp.yaml'):
    fp = open('rflink2tcp.yaml', 'r')
    config = yaml.safe_load(fp)
else:
    print('Configuration file not found, exiting.')
    sys.exit(1)

class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):

    rbufsize = -1
    wbufsize = 0

    def setup(self):
        port = self.server.server_address[1]
        self.connection = self.request
        self.rfile = self.connection.makefile('rb', self.rbufsize)
        self.wfile = self.connection.makefile('wb', self.wbufsize)
        for ii in range(0, len(config['rflink'])):
            if int(config['rflink'][ii]['port']) == port:
                self.id = uuid.uuid1().hex
                config['rflink'][ii]['requests'][self.id] = self.send

    def send(self, msg):
        self.wfile.write(msg)

    def handle(self):
        data = self.rfile.readline().strip()
        while data:
            print(data)
            data = self.rfile.readline().strip()

    def finish(self):
        for ii in range(0, len(config['rflink'])):
            if 'requests' in config['rflink'][ii]:
                if self.id in config['rflink'][ii]['requests']:
                    del config['rflink'][ii]['requests'][self.id]
        if not self.wfile.closed:
            self.wfile.flush()
        self.wfile.close()
        self.rfile.close()

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

# Define MQTT event callbacks
def on_connect(client, userdata, flags, rc):
    connect_statuses = {
        0: "Connected",
        1: "incorrect protocol version",
        2: "invalid client ID",
        3: "server unavailable",
        4: "bad username or password",
        5: "not authorised"
    }
    print("MQTT: " + connect_statuses.get(rc, "Unknown error"))

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection")
    else:
        print("Disconnected")

def on_message(client, obj, msg):
    print("Msg: " + msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    for ii in range(0, len(config['rflink'])):
        if msg.topic.startswith(config['rflink'][ii]['topic']):
            if 'requests' in config['rflink'][ii]:
                for uuid in config['rflink'][ii]['requests']:
                    config['rflink'][ii]['requests'][uuid](msg.payload)

def on_publish(client, obj, mid):
    print("Pub: " + str(mid))

def on_subscribe(client, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

def on_log(client, obj, level, string):
    print(string)

# Setup MQTT connection
mqttc = mqtt.Client()

mqttc.on_connect = on_connect
mqttc.on_subscribe = on_subscribe
mqttc.on_disconnect = on_disconnect
mqttc.on_message = on_message

if config['mqtt']['debug']:
    print("Debugging messages enabled")
    mqttc.on_log = on_log    
    mqttc.on_publish = on_publish

if config['mqtt']['username'] and config['mqtt']['password']:
    mqttc.username_pw_set(config['mqtt']['username'], config['mqtt']['password'])
mqttc.connect(config['mqtt']['host'], config['mqtt']['port'], 60)
mqttc.loop_start()

for ii in range(0, len(config['rflink'])):
    mqttc.subscribe(config['rflink'][ii]['topic'])
    host = config['rflink'][ii]['host']
    port = int(config['rflink'][ii]['port'])
    server = ThreadedTCPServer((host, port), ThreadedTCPRequestHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    config['rflink'][ii]['server'] = server
    config['rflink'][ii]['requests'] = {}
    
while True:
    time.sleep(1)
