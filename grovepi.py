#!/usr/bin/env python
import smbus
from webiopi.utils import logger
import time
from webiopi.utils.types import M_JSON
import RPi.GPIO as GPIO
from webiopi.decorators.rest import request, response
debug = 1

class GroveGPIO():
    IN = 0
    OUT = 1

    LOW = False
    HIGH = True

class GrovePi(GroveGPIO):
    FUNCTIONS = [GroveGPIO.IN for i in range(8)]
    IN = 0
    OUT = 1

    LOW = False
    HIGH = True

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

    def getFunction(self, channel):
        raise NotImplementedError

    def setFunction(self, channel, value):
        if not value in [self.IN, self.OUT]:
            raise ValueError("Request function not supported")
        self.pinMode(channel, value)

    def checkChannel(self, channel):
        if not channel in range(8):
            raise ValueError("Channel %d invalid" % channel)

    @request("GET", "digital/output/%(channel)d")
    @response("%d")
    def digitalReadOutput(self, channel):
        self.checkChannel(channel)
        return self.digitalRead(channel)

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

    @request("GET", "digital/*")
    @response(contentType=M_JSON)
    def readAll(self):
        logger.info('Getting all GrovePi readings')
        inputs = {}
        outputs = {}
        for i in range(8):
            inputs[i] = self.digitalRead(i)
            outputs[i] = self.digitalReadOutput(i)
        logger.info('Inputs are {}'.format(inputs))
        logger.info('Outputs are {}'.format(outputs))
        return {"input": inputs, "output": outputs}

    @request("GET", "%(channel)d/function")
    def getFunctionString(self, channel):
        func = self.getFunction(channel)
        if func == self.IN:
            return "IN"
        elif func == self.OUT:
            return "OUT"
#        elif func == GPIO.PWM:
#            return "PWM"
        else:
            return "UNKNOWN"


    def __portRead__(self):
        raise NotImplementedError

    def __portWrite__(self, value):
        raise NotImplementedError


