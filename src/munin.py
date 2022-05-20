from incomfort import *

import sys

def main():
    with open('/etc/incomfort-gateway') as f:
        h = Heater(Gateway(f.read().strip()), 0)
    if len(sys.argv) == 1:
        print('multigraph incomfort_temp')
        print('heater.value %s' % h.heater_temp)
        print('tap.value %s' % h.tap_temp)
        print()
        print('multigraph incomfort_room_temp')
        print('room.value %s' % h.room_temp)
        print('setpoint.value %s' % h.setpoint)
        print()
        print('multigraph incomfort_pressure')
        print('pressure.value %s' % h.pressure)
        return 0
    if sys.argv[1] == 'config':
        print('multigraph incomfort_temp')
        print('graph_title incomfort temperatures')
        print('graph_vlabel degrees celsius')
        print('graph_category incomfort')
        print('heater.label heater')
        print('tap.label tap')
        print()
        print('multigraph incomfort_room_temp')
        print('graph_title incomfort room temperatures')
        print('graph_vlabel degrees celsius')
        print('graph_category incomfort')
        print('room.label room')
        print('setpoint.label setpoint')
        print()
        print('multigraph incomfort_pressure')
        print('graph_title incomfort pressure')
        print('graph_vlabel bar')
        print('graph_category incomfort')
        print('pressure.label pressure')
        return 0
    if sys.argv[1] == 'autoconf':
        print('yes')
        return 0
    return -1

if __name__ == '__main__':
    sys.exit(main())
