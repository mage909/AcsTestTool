import os
import serial
import glob
import time


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


def init():
    get_ports = sorted(glob.glob("/dev/ttyUSB*"))
    os.system("sudo chown root:root %s" % get_ports[0])
    time.sleep(1)
    os.system("sudo chmod 666 %s" % get_ports[0])
    time.sleep(1)
    s = serial.Serial(port=get_ports[0], baudrate=9600, timeout=1)
    time.sleep(1)
    s.write(ports.get('AllOff'))
    return s


if __name__ == '__main__':
    print "init relay"
    relay = init()
    on = ports.get('AllOn')
    off = ports.get('AllOff')
    i = 1
    print "sleep&wakeup stress begin"
    while True:
        # screen off
        time.sleep(5)
        relay.write(on)
        time.sleep(0.2)
        relay.write(off)
        # sleep 60s
        print "display off,sleep 60s"
        time.sleep(60)
        # screen on
        relay.write(on)
        time.sleep(0.2)
        relay.write(off)
        # wake 15s
        print "display off,wait 15s"
        time.sleep(15)
        print "Sleep_Wakeup LOOP %d" % i
        i += 1
