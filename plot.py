"""
ldr.py
Display analog data from Arduino using Python (matplotlib)
Author: Mahesh Venkitachalam
Website: electronut.in
"""

import sys, serial, argparse
import threading

import numpy as np
from time import sleep
from collections import deque

import matplotlib.pyplot as plt
import matplotlib.animation as animation

from serial.tools import list_ports

# define your data format here.
# for example:
#
# python side
# plot_items = ['Actual', 'Set', 'Control input']
# display_number_items = ['kP', 'kI', 'kD']
#
# arduino should print
# 1.0,1.0,1.0,1.0,1.0,1.0\n
#
# print each item in order define below,
# use comma as deliminator
# use a new line character to indicate current set of data

# will show as line plot
plot_items = ['Actual', 'Set']
# will not show up on the plot but will display number
display_number_items = ['kP', 'kI', 'kD', 'u', 'err', 'sum_err', 'diff_err']

points_on_screen = 1000


# plot class
class AnalogPlot:
    def __init__(self, strPort, maxLen):
        self.ser = serial.Serial(strPort, 115200)

        self.plot_buffer = []
        self.display_number_buffer = [0.0] * len(display_number_items)

        for i in range(0, len(plot_items)):
            self.plot_buffer.append(deque([0.0] * maxLen))

        self.maxLen = maxLen

    # add to buffer
    def addToBuf(self, buf, val):
        if len(buf) < self.maxLen:
            buf.appendleft(val)
        else:
            buf.popleft();
            buf.append(val)

    # add data
    def add(self, data):
        if len(data) == len(plot_items) + len(display_number_items):
            for i in range(0, len(plot_items)):
                self.addToBuf(self.plot_buffer[i], data[i])
            for i in range(0, len(display_number_items)):
                self.display_number_buffer[i] = data[i + len(plot_items)]
        else:
            raise BadSerialMessageException('Data length mismatch. ' +
                                            'Check your plot/display items config and Arduino code ' + str(data))

    def update_serial(self):
        while 1:
            try:
                line = self.ser.readline()
                data = [float(val) for val in line.split(',')]
                self.add(data)
            except KeyboardInterrupt:
                print('exiting')
            except Exception as e:
                print(e)
                print('raw line: ' + line)

    def update_plot(self, frameNum, txt, axes):
        try:
            for i in range(0, len(plot_items)):
                axes[i].set_data(range(self.maxLen), self.plot_buffer[i])

            measurements = ""
            for i, item in enumerate(display_number_items):
                measurements += "%s=%f " % (item, self.display_number_buffer[i])
            txt.set_text(measurements)


        except KeyboardInterrupt:
            print('exiting')
        except Exception as e:
            print(e)

        return axes[0],

    # clean up
    def close(self):
        # close serial
        self.ser.flush()
        self.ser.close()

        # main() function


class BadSerialMessageException(Exception):
    pass


def main():
    print('auto-detecting arduino...')

    serial_port = getArduinoPort()

    if serial_port is None:
        print('cannot find Arduino. Are you sure it is plugged in?\n'
              'Restart the program to auto-detect or manually input the port.')
        print('available ports: %s' % str([port[0] for port in list_ports.comports()]))

        serial_port = raw_input('Serial port: ')

    print('reading from serial port %s...' % serial_port)

    # plot parameters
    analogPlot = AnalogPlot(serial_port, points_on_screen)

    t = threading.Thread(target=analogPlot.update_serial)
    t.setDaemon(True)
    t.start()

    print('plotting data...')

    # set up animation
    fig = plt.figure(figsize=(15, 8))
    ax = plt.axes(xlim=(0, points_on_screen), ylim=(-2, 2))
    axes = []
    for i in range(0, len(plot_items)):
        a0 = ax.plot([], [], label=plot_items[i])
        axes.append(a0[0])
    plt.legend()
    fig.tight_layout()

    txt = plt.figtext(0.1, 0.1, '', family='monospace', fontsize=15)

    anim = animation.FuncAnimation(fig, analogPlot.update_plot,
                                   fargs=(txt, tuple(axes)),
                                   interval=20)

    # show plot
    plt.show()

    # clean up
    analogPlot.close()

    print('exiting.')


def getArduinoPort():
    # Arduino USB serial microcontroller program id data:
    VENDOR_ID = "2341"
    PRODUCT_ID = "0042"
    for port in list(list_ports.comports()):
        # if "USB VID:PID=%s:%s SER=%s" % (VENDOR_ID, PRODUCT_ID, SERIAL_NUMBER) in port[2]:
        if "USB VID:PID=%s:%s" % (VENDOR_ID, PRODUCT_ID) in port[2]:
            return port[0]


# call main
if __name__ == '__main__':
    main()
