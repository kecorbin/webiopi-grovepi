#!/usr/bin/env python
import smbus
from webiopi.utils import logger
import time
import math
import RPi.GPIO as GPIO
import struct
import sys
from webiopi.decorators.rest import request, response
debug = 0


class GrovePi():
    #FUNCTIONS = [GPIOPort.IN for i in range(8)]


    def __init__(self):
        self.__dWrite_cmd = [2]
        self.__dRead_cmd = [1]
        self.__pMode_cmd = [5]
        self.__address = 0x04
        self.__unused = 0
        self.__dWrite_cmd = [2]
        self.__address = 0x04
        self.__unused = 0
        self.rev = GPIO.RPI_REVISION
        if self.rev == 2 or self.rev == 3:
            self.bus = smbus.SMBus(1)
        else:
            self.bus = smbus.SMBus(0)


    def __str__(self):
        return "GrovePi(%d)" % self.__unused


    def __family__(self):
        return "GrovePi"

    def read_i2c_byte(self, address):
        try:
            return self.bus.read_byte(address)
        except IOError:
            if debug:
                print ("IOError")
            return -1


    def write_i2c_block(self, address, block):
        try:
            return self.bus.write_i2c_block_data(address, 1, block)
        except IOError:
            if debug:
                print ("IOError")
            return -1


    def pinMode(self, pin, mode):
        if mode == "OUTPUT":
            self.write_i2c_block(self.__address, self.__pMode_cmd + [pin, 1, self.__unused])
        elif mode == "INPUT":
            self.write_i2c_block(self.__address, self.__pMode_cmd + [pin, 0, self.__unused])
        return 1

    def __getFunction__(self, channel):
        raise NotImplementedError

    def __setFunction__(self, channel, value):
        raise NotImplementedError

    @request("GET", "digital/output/%(channel)d")
    @response("%d")
    def digitalRead(self, channel):
        logger.info("Executing read_i2c_block")
        self.write_i2c_block(self.__address, self.__dRead_cmd + [channel, self.__unused, self.__unused])
        time.sleep(.1)
        n = self.read_i2c_byte(self.__address)
        return n


    @request("POST", "digital/output/%(channel)d/%(value)d")
    @response("%d")
    def digitalWrite(self, channel, value):
        logger.info("Executing write_i2c_block")
        self.write_i2c_block(self.__address, self.__dWrite_cmd + [channel, value, self.__unused])
        return 1


    def __portRead__(self):
        raise NotImplementedError

    def __portWrite__(self, value):
        raise NotImplementedError


