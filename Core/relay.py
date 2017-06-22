import serial
import os
import time
import sys
import glob


class Relay(object):
    # ports = {
    #     'AllOn': '\x55\x01\x01\x02\x02\x02\x02\x5F',
    #     'AllOff': '\x55\x01\x01\x01\x01\x01\x01\x5B',
    #     'OutOneOn': '\x55\x01\x01\x02\x00\x00\x00\x59',
    #     'OutOneOff': '\x55\x01\x01\x01\x00\x00\x00\x58',
    #     'OutTwoOn': '\x55\x01\x01\x00\x02\x00\x00\x59',
    #     'OutTwoOff': '\x55\x01\x01\x00\x01\x00\x00\x58',
    #     'OutThreeOn': '\x55\x01\x01\x00\x00\x02\x00\x59',
    #     'OutThreeOff': '\x55\x01\x01\x00\x00\x01\x00\x58',
    #     'OutFourOn': '\x55\x01\x01\x00\x00\x00\x02\x59',
    #     'OutFourOff': '\x55\x01\x01\x00\x00\x00\x01\x58',
    # }

    ports = {
        'AllOn': '\xFE\x0F\x00\x00\x00\x04\x01\xFF\x31\xD2',
        'AllOff': '\xFE\x0F\x00\x00\x00\x04\x01\x00\x71\x92',
        'OutOneOn': '\xFE\x05\x00\x00\xFF\x00\x98\x35',
        'OutOneOff': '\xFE\x05\x00\x00\x00\x00\xD9\xC5',
        'OutTwoOn': '\xFE\x05\x00\x01\xFF\x00\xC9\xF5',
        'OutTwoOff': '\xFE\x05\x00\x01\x00\x00\x88\x05',
        'OutThreeOn': '\xFE\x05\x00\x02\xFF\x00\x39\xF5',
        'OutThreeOff': '\xFE\x05\x00\x02\x00\x00\x78\x05',
        'OutFourOn': '\xFE\x05\x00\x03\xFF\x00\x68\x35',
        'OutFourOff': '\xFE\x05\x00\x03\x00\x00\x29\xC5',
    }
    serials = []

    def __init__(self):
        try:
            get_ports = sorted(glob.glob("/dev/ttyUSB*"))
            for t in get_ports:
                os.system("sudo chown root:root %s" % t)
                time.sleep(2)
                os.system("sudo chmod 666 %s" % t)
                time.sleep(2)
                self.serials.append(serial.Serial(port=t, baudrate=9600, timeout=1))
                time.sleep(2)
                self.serials[-1].write(self.ports.get('AllOff'))
                time.sleep(2)
        except Exception as e:
            print e

    def echo(self, port, flag=0):
        serialslen = len(self.serials)
        if serialslen == 0 or serialslen < flag+1:
            print "------> Don't detect relay, or relay index out of range,exit"
            sys.exit(0)
        else:
            self.serials[flag].write(self.ports.get(port))

    def onkey(self, port, t):
        time.sleep(3)
        self.echo('Out'+port.capitalize()+'On')
        time.sleep(t)
        self.echo('Out'+port.capitalize()+'Off')

    def allOutOn(self, flag=0):
        self.echo('AllOn', flag)

    def allOutOff(self, flag=0):
        self.echo('AllOff', flag)
