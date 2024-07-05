#/usr/bin/python3
#
#  Copyright (c) 2020-2021 RTSoft. All rights reserved.
#
#  SPDX-License-Identifier: Apache-2.0
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import paho.mqtt.client as mqtt
from threading import Lock
import os
import sys
import time
import datetime
import json
import signal
import atexit

__version__ = '1.3'

log_level = 0 # 0 - no messages, 1 - errors, 2 - warnings, 3 - info, 4 - debug, 5 - verbose debug, 6 - more verbose debug
log_prefix = "ftguilib: "
def log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S ")
    #print(log_prefix, timestamp, message, file = open("/home/ft/log.txt", "a"))
    print(log_prefix, timestamp, message)
    return None

ftgui_instances = []

def __stop_all():
    global ftgui_instances
    for i in ftgui_instances:
        i.stop()

def __on_exit():
    if log_level >= 3: log("Exiting from application, cleanup...")
    __stop_all()

atexit.register(__on_exit)

class fttxt2_gui_connector:
    def __init__(self, client_name = None, broker_address = "127.0.0.1", broker_port = 2883):
        global ftgui_instances
        ftgui_instances.append(self)
        self.active = False
        self.gui_started = False
        self.gui_exited = False
        self.exit_on_gui_close = False
        self.pid = os.getpid()
        self.project = os.path.abspath(sys.argv[0])
        self.topic_notify = "TXTGUINotification"
        self.topic_event = "TXTGUIEvent"
        self.topic_attr = "TXTGUIAttributeChange"
        self.broker_address = os.getenv('TXT_BROKER_ADDRESS', broker_address)
        self.broker_port = int(os.getenv('TXT_BROKER_PORT', broker_port))
        self.broker_keepalive = 10
        self.handlers = dict()
        self.attributes = dict()
        self.invalidated = dict()
        self.setter_queue = dict()
        self.setter_request = None
        self.client_name = client_name or "Python%d" % self.pid
        self.client = mqtt.Client(self.client_name)
        self.client.on_message = self.on_message
        self.client.on_publish = self.on_publish
        self.setter_lock = Lock()
        if log_level >= 3: log("Initialized: pid: %s, project: %s" % (self.pid, self.project))
    
    def notify(self):
        self.exit_on_gui_close = True
        return self.run(False)
    
    def run(self, wait = True):
        # OBSOLETE
        return self.open(wait)
    
    def open(self, wait = True):
        if not self.active:
            self.active = True
            self.gui_started = False
            self.gui_exited = False
            if log_level >= 4: log("Connecting to broker: %s:%d as %s" % (self.broker_address, self.broker_port, self.client_name))
            self.client.connect(self.broker_address, self.broker_port, self.broker_keepalive)
            self.client.subscribe(self.topic_notify, qos = 2)
            self.client.subscribe(self.topic_event, qos = 2)
            self.client.loop_start()
            if log_level >= 4: log("Sending ProjectLoaded: %d %s" %(self.pid, self.project))
            self.client.publish(self.topic_notify, json.dumps({ "action": 'ProjectLoaded', "pid": str(self.pid), "project": self.project }), qos = 2)
            if wait:
                if log_level >= 5: log("Waiting for UI to start: active = %r, started = %r, exited = %r" % (self.active, self.gui_started, self.gui_exited))
                while not self.gui_started and not self.gui_exited and self.active:
                    if log_level >= 6: log("Waiting for UI to start: active = %r, started = %r, exited = %r" % (self.active, self.gui_started, self.gui_exited))
                    #self.client.loop()
                    time.sleep(0.25)
    
    def running(self):
        # OBSOLETE
        return self.is_open()
    
    def is_open(self):
        if log_level >= 6: log('Test gui running: active = %r, started = %r, exited = %r' % (self.active, self.gui_started, self.gui_exited))
        return self.active and self.gui_started and not self.gui_exited
    
    def stop(self, wait = False):
        # OBSOLETE
        return self.close(wait)
    
    def close(self, wait = False):
        if self.active:
            self.active = False
            if log_level >= 4: log("Sending ProjectExited")
            self.client.publish(self.topic_notify, json.dumps({ "action": 'ProjectExited', "pid": str(self.pid), "project": self.project }), qos = 2).wait_for_publish()
            if wait:
                if log_level >= 5: log("Waiting for UI to stop: active = %r, started = %r, exited = %r" % (self.active, self.gui_started, self.gui_exited))
                while self.is_open():
                    if log_level >= 6: log("Waiting for UI to stop: active = %r, started = %r, exited = %r" % (self.active, self.gui_started, self.gui_exited))
                    time.sleep(0.25)
            self.client.disconnect()
            self.gui_started = False
            self.gui_exited = False
            if log_level >= 3: log("Stopped and disconnected")
            self.client.loop_stop()
    
    def get_attr(self, path):
        # Note: If property is changing too quick, you may not see some intermediate values
        ids = str(path).split(".")
        if len(ids) != 2:
            if log_level >= 1: log("ERROR: Malformed attribute name: {}".format(path))
            return None
        if ids[0] not in self.attributes or ids[1] not in self.attributes[ids[0]]:
            if log_level >= 1: log("ERROR: No such attribute available: {}".format(path))
            return None
        if log_level >= 5: log("Getting attribute: {}".format(path))
        if str(path) in self.invalidated and self.is_open():
            self.run_queue(True)
            if log_level >= 4: log("Waiting for attribute: {}".format(path))
            while str(path) in self.invalidated and self.is_open():
                # Note: This busy wait may not work correctly if 2 x set_attr() called before get_attr()
                time.sleep(0.02)
        return self.attributes[ids[0]][ids[1]]
    
    def set_attr(self, path, value):
        ids = str(path).split(".")
        if len(ids) != 2:
            if log_level >= 1: log("ERROR: Malformed attribute name: {}".format(path))
            return None
        if ids[0] not in self.attributes or ids[1] not in self.attributes[ids[0]]:
            if log_level >= 1: log("ERROR: No such attribute available: {}".format(path))
            return None
        if self.is_open():
            if log_level >= 4: log("Setting attribute: {} = {}".format(path, value))
            self.invalidated[str(path)] = True
            self.setter_lock.acquire()
            if ids[0] not in self.setter_queue:
                self.setter_queue[ids[0]] = dict()
            self.setter_queue[ids[0]][ids[1]] = value
            self.setter_lock.release()
            self.run_queue()
            return True
        return False
    
    def has_attr(self, path, value):
        ids = str(path).split(".")
        if len(ids) != 2:
            return None
        return ids[0] in self.attributes and ids[1] in self.attributes[ids[0]]
    
    def attrs(self, objid = None):
        if objid != None:
            if objid not in self.attributes:
                return None
            return {"{}.{}".format(i, n): v for i,o in self.attributes.items() if i == objid for n,v in o.items()}
        return {"{}.{}".format(i, n): v for i,o in self.attributes.items() for n,v in o.items()}
    
    def set_exit_on_gui_close(self, enabled = True):
        self.exit_on_gui_close = enabled
    
    def input_accepted(self, obj_id, on_input_accepted):
        self.handlers["%s:%s" % (obj_id, "input_accepted")] = on_input_accepted
    
    def slider_moved(self, obj_id, on_slider_moved):
        self.handlers["%s:%s" % (obj_id, "slider_moved")] = on_slider_moved
    
    def button_clicked(self, obj_id, on_button_clicked):
        self.handlers["%s:%s" % (obj_id, "button_clicked")] = on_button_clicked
    
    def switch_toggled(self, obj_id, on_switch_toggled):
        self.handlers["%s:%s" % (obj_id, "switch_toggled")] = on_switch_toggled
    
    def checkbox_toggled(self, obj_id, on_checkbox_toggled):
        self.handlers["%s:%s" % (obj_id, "checkbox_toggled")] = on_checkbox_toggled
    
    def gesture(self, name, on_gesture):
        self.handlers["<null>:gesture_" + name] = on_gesture
    
    def run_queue(self, forced = False):
        if log_level >= 5: log("Run queue: forced: {}, current req: {}, has messages: {}".format(forced, self.setter_request, bool(self.setter_queue)))
        self.setter_lock.acquire()
        if bool(self.setter_queue):
            if self.setter_request == None or forced:
                if log_level >= 5: log("Sending attributes: '%s'" % (json.dumps({ "payload": self.setter_queue })))
                q = self.setter_queue
                self.setter_queue = dict()
                self.setter_lock.release()
                self.setter_request = self.client.publish(self.topic_notify, json.dumps({ "action": 'UIAttrSet', "pid": str(self.pid), "project": self.project, "payload": q }), qos = 2)
                return
        self.setter_lock.release()
    
    def on_publish(self, client, userdata, mid):
        if log_level >= 6: log("Published: {}, setter request: {}".format(mid, self.setter_request))
        if self.setter_request != None and mid == self.setter_request.mid:
            self.setter_request = None
        self.run_queue()
    
    def on_message(self, client, userdata, message):
        msg = str(message.payload.decode("utf-8"))
        if log_level >= 6: log("Message received: <<%s>>" % msg)
        if message.topic == self.topic_notify:
            o = json.loads(msg)
            if o['action'] == 'UILoaded' and o['project'] == self.project and o['pid'] == str(self.pid):
                if log_level >= 4: log("Received UILoaded, pid=%s" % o['pid'])
                self.attributes = o['payload'] if 'payload' in o else dict()
                self.invalidated = dict()
                self.setter_queue = dict()
                self.setter_request = None # TODO can we cancel this request?
                self.gui_started = True
            elif o['action'] == 'UIExited' and o['project'] == self.project and o['pid'] == str(self.pid):
                if log_level >= 4: log("Received UIExited, pid=%s" % o['pid'])
                self.gui_exited = True
                if self.exit_on_gui_close:
                    os.kill(self.pid, signal.SIGTERM)
            elif o['action'] == 'UIChanged' and o['project'] == self.project and o['pid'] == str(self.pid):
                if log_level >= 5: log("Received UIChanged, pid=%s" % o['pid'])
                d = o['payload'] if 'payload' in o else dict()
                for i,a in d.items():
                    if i in self.attributes:
                        self.attributes[i].update(a)
                        for n,v in a.items():
                            k = "{}.{}".format(i, n)
                            if k in self.invalidated:
                                del self.invalidated[k]
        elif message.topic == self.topic_event:
            o = json.loads(msg)
            if log_level >= 5: log("Received event: %s from %s, %s" % (o['event'], o['id'], o['name']))
            # Try find a handler
            h = None
            if o['id']:
                h = self.handlers.get("%s:%s" % (o['id'], o['event']), None)
            if not h:
                if log_level >= 5: log("WARNING: No handler defined for event: %s from %s, %s" % (o['event'], o['id'], o['name']))
            else:
                h(o)
    
    def __del__(self):
        global ftgui_instances
        self.stop()
        ftgui_instances.remove(self)

