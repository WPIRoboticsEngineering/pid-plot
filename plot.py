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


# plot class
class AnalogPlot:
    # constr
    def __init__(self, strPort, maxLen):
        # open serial port
        self.ser = serial.Serial(strPort, 115200)

        # self.ax = deque([0.0]*maxLen)
        # self.ay = deque([0.0]*maxLen)
        self.buffered_values = []
        for i in range(0, 7):
            self.buffered_values.append(deque([0.0] * maxLen))
        self.maxLen = maxLen

    # add to buffer
    def addToBuf(self, buf, val):
        if len(buf) < self.maxLen:
            buf.append(val)
        else:
            buf.pop()
            buf.appendleft(val)

    # add data
    def add(self, data):
        assert (len(data) == 7)
        for i in range(0, 7):
            self.addToBuf(self.buffered_values[i], data[i])
            # self.addToBuf(self.ax, data[0])
            # self.addToBuf(self.ay, data[1])
            # self.addToBuf(self.az, data[2])

    # update plot
    def update(self, frameNum, axes):
        try:
            line = self.ser.readline()
            data = [float(val) for val in line.split(',')]
            # print data
            if (len(data) == 7):
                self.add(data)
                for i in range(0, 7):
                    axes[i].set_data(range(self.maxLen), self.buffered_values[i])
                    # a0.set_data(range(self.maxLen), self.ax)
                    # a1.set_data(range(self.maxLen), self.ay)
        except KeyboardInterrupt:
            print('exiting')
        except Exception as e:
            print(e)

        return axes[0],

    def update_serial(self):
        while 1:
            try:
                line = self.ser.readline()
                print line
                data = [float(val) for val in line.split(',')]
                # print data
                if (len(data) == 7):
                    self.add(data)
            except KeyboardInterrupt:
                print('exiting')
            except Exception as e:
                print(e)

    def update_plot(self, frameNum, axes):
        try:
            for i in range(0, 7):
                axes[i].set_data(range(self.maxLen), self.buffered_values[i])
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


def main():
    # create parser
    parser = argparse.ArgumentParser(description="LDR serial")
    # add expected arguments
    parser.add_argument('--port', dest='port', required=True)

    # parse args
    args = parser.parse_args()

    # strPort = '/dev/tty.usbserial-A7006Yqh'
    strPort = args.port

    print('reading from serial port %s...' % strPort)

    # plot parameters
    analogPlot = AnalogPlot(strPort, 2000)

    t = threading.Thread(target=analogPlot.update_serial)
    t.start();

    print('plotting data...')

    # set up animation
    fig = plt.figure()
    ax = plt.axes(xlim=(0, 2000), ylim=(0, 1023))
    axes = []
    for i in range(0, 7):
        a0 = ax.plot([], [])
        axes.append(a0[0])
    # a0, = ax.plot([], [])
    # a1, = ax.plot([], [])
    anim = animation.FuncAnimation(fig, analogPlot.update_plot,
                                   fargs=(tuple(axes),),
                                   interval=10)

    # show plot
    plt.show()

    # clean up
    analogPlot.close()

    print('exiting.')


# call main
if __name__ == '__main__':
    main()
