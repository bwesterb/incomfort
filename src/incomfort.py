#!/usr/bin/env python3
""" Python client library for the incomfort LAN2RF gateway. """

import sys
import json
import os.path
import http.client
import argparse

def _lsbmsb(lsb, msb):
    return (lsb + msb*256) / 100.0

def _set(gateway, heater, setpoint):
    conn = http.client.HTTPConnection(gateway)
    conn.request('GET', '/data.json?heater=%s&thermostat=0&setpoint=%s' % (
                            heater, setpoint))
    resp = conn.getresponse()
    return json.loads(resp.read())


def _status(gateway, heater):
    conn = http.client.HTTPConnection(gateway)
    conn.request('GET', '/data.json?heater=%s' % heater)
    resp = conn.getresponse()
    return json.loads(resp.read())

def _heaters(gateway):
    conn = http.client.HTTPConnection(gateway)
    conn.request('GET', '/heaterlist.json')
    resp = conn.getresponse()
    return json.loads(resp.read())['heaterlist']

class Heater(object):
    def __init__(self, gw, i):
        self.gw = gw
        self.i = i
        self._update()
    def _update(self):
        self._data = _status(self.gw.host, self.i)

    @property
    def pressure(self):
        return _lsbmsb(self._data['ch_pressure_lsb'],
                    self._data['ch_pressure_msb'])
    @property
    def heater_temp(self):
        return _lsbmsb(self._data['ch_temp_lsb'],
                    self._data['ch_temp_msb'])

    @property
    def tap_temp(self):
        return _lsbmsb(self._data['tap_temp_lsb'],
                    self._data['tap_temp_msb'])

    @property
    def room_temp(self):
        return _lsbmsb(self._data['room_temp_1_lsb'],
                    self._data['room_temp_1_msb'])

    @property
    def setpoint(self):
        return _lsbmsb(self._data['room_temp_set_1_lsb'],
                    self._data['room_temp_set_1_msb'])

    @property
    def setpoint_override(self):
        return _lsbmsb(self._data['room_set_ovr_1_lsb'],
                    self._data['room_set_ovr_1_msb'])
    @property
    def display_code(self):
        return {85:  'sensortest',
                170: 'service',
                204: 'tapwater',
                51:  'tapwater int.',
                240: 'boiler int.',
                15:  'boiler ext.',
                153: 'postrun boiler',
                102: 'central heating',
                0:   'opentherm',
                255: 'buffer',
                24:  'frost',
                231: 'postrun ch',
                126: 'standby',
                37:  'central heating rf'
                    }.get(self._data['displ_code'], 'unknown')

    @property
    def burning(self):
        return bool(self._data['IO'] & 8)
    @property
    def lockout(self):
        return bool(self._data['IO'] & 1)
    @property
    def pumping(self):
        return bool(self._data['IO'] & 2)
    @property
    def tapping(self):
        return bool(self._data['IO'] & 4)

    def set(self, setpoint):
        self._data = _set(self.gw.host, self.i,
                    int((min(max(setpoint, 5), 30) - 5.0) * 10))
        self.print_summary()


    def print_summary(self):
        print("Pressure     %s" % self.pressure)
        print("Heater temp. %s" % self.heater_temp)
        print("Tap temp.    %s" % self.tap_temp)
        print("Display code %s" % self.display_code)
        print("Room temp.   %s" % self.room_temp)
        print("Setpoint     %s" % self.setpoint)
        print("Stpt. ovrd.  %s" % self.setpoint_override)
        print()
        print("Burning?     %s" % self.burning)
        print("Pumping?     %s" % self.pumping)
        print("Tapping?     %s" % self.tapping)
        print("Error?       %s" % self.lockout)

class Gateway(object):
    def __init__(self, host):
        self.host = host

    @property
    def heaters(self):
        return [Heater(self, i)
                        for i, h in enumerate(_heaters(self.host))
                        if h]

def main():
    # TODO, put it here ourselves
    path = '/etc/incomfort-gateway'
    host = None
    if not os.path.exists(path):
        path = os.path.expanduser('~/.incomfort-gateway')
        if not os.path.exists(path):
            host = input("Type the IP of the LAN2RF gateway: ")
            with open(path, 'w') as f:
                f.write(host)
            print(" (stored in %s)" % path)
    if host is None:
        with open(path) as f:
            host = f.read().strip()
    # TODO have a nice UI for multiple heaters... Who has multiple heaters
    #      anyway?
    h = Heater(Gateway(host), 0)
    if len(sys.argv) == 1:
        h.print_summary()
        return
    if sys.argv[1] == 'pressure':
        print(h.pressure); return
    if sys.argv[1] == 'heater_temp':
        print(h.heater_temp); return
    if sys.argv[1] == 'tap_temp':
        print(h.tap_temp); return
    if sys.argv[1] == 'display_code':
        print(h.display_code); return
    if sys.argv[1] == 'room_temp':
        print(h.room_temp); return
    if sys.argv[1] == 'setpoint':
        print(h.setpoint); return
    if sys.argv[1] == 'burning':
        print(int(h.burning)); return
    if sys.argv[1] == 'pumping':
        print(int(h.pumping)); return
    if sys.argv[1] == 'tapping':
        print(int(h.tapping)); return
    if sys.argv[1] == 'error':
        print(int(h.error)); return

    if len(sys.argv) == 3 and sys.argv[1] == 'set':
        h.set(float(sys.argv[2]))

if __name__ == '__main__':
    main()

