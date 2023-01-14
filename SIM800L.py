#!/usr/bin/python3
"""
Project	 	: SIM800 test script 
Date&Time	: 08th August 2019.
Description	: This module consists all APIs necessary for testing SIMcom SIM800H module
		http://simcomm2m.com/En/module/detail.aspx?id=75
"""
import serial
import logging
import time, sys


class SIM800L:
    def __init__(
        self,
        portName="",
        baudRate=115200,
        # bytesize=serial.EIGHTBITS,
        # parity=serial.PARITY_NONE,
        # stopbits=serial.STOPBITS_ONE,
        timeout=1,
    ):
        self.portName = portName
        self.baudRate = baudRate
        # self.bytesize = bytesize
        # self.parity = parity
        # self.stopbits = stopbits
        self.timeout = timeout

    def openComPort(self):
        try:
            self.ser = serial.Serial(
                self.portName,
                self.baudRate,
                timeout=self.timeout,
                # bytesize=self.bytesize,
                # parity=self.parity,
                # stopbits=self.stopbits,
            )
            time.sleep(0.5)
        except:
            logging.error("Couldn't open desired tty port: " + self.portName)
            sys.exit()

    def closeComPort(self):
        try:
            self.ser.close()
        except:
            logging.error("Couldn't close tty port")
            sys.exit()

    def sendAtCommand(self, command):
        self.command = command
        logging.info('Sending AT command: '+command)
        try:
            self.ser.write((command + "\r").encode())
            received='\t'
            received += (self.ser.read(20).splitlines()[-1]).decode()
            logging.info(received)
            if "ERROR" in received:
                return False
            return received
        except:
            print("Couldn't write on " + self.portName)
            return False

    def checkCommunication(self):
        if not self.sendAtCommand("AT"):
            return False
        return True

    def initATSettings(self):
        if not self.sendAtCommand("AT+MORING=1"):
            return False
        return True
 

    def sendSms(self):
        try:
            number = input("To >> ")
        except Exception as e:
            logging.error("Error: " + str(e))
            return False
        try:
            message = input("Insert Message >> ")
        except Exception as e:
            logging.error("Error: " + str(e))
            return False

        print("\n\r...sending SMS")
        if not self.sendAtCommand("AT+CMGF=1"):
            logging.error("To send AT command: AT+CMGF=1")
            return False
        if not self.sendAtCommand('AT+CMGS="' + number + '"'):
            logging.error("To send AT command: AT+CMGS=")
            return False
        if not self.sendAtCommand(message):
            logging.error("To send AT command: message content")
            return False

        if not self.sendAtCommand("1A".decode("hex")):
            logging.error("To send AT command: Ctrl+Z")
            return False

        return True

    def call(self, number=None, timeout=None, duration=0):
        success=0
        if (number==None):
            try:
                number = input("Insert Number >> ")
            except Exception as e:
                logging.error(str(e))
                return success

        logging.info("\n\r...processing call")
        if not self.sendAtCommand("ATD+ " + number + ";"):
        # if not self.sendAtCommand("ATD" + number):
            logging.error("To send AT command: ATD")
            return success
        if not self.sendAtCommand("ATL5"):
            logging.error("To send AT command: ATL")
            return success
        if not self.sendAtCommand("ATM5"):
            logging.error("To send AT command: ATM")
            return success

        success=1
        if timeout==None:
            try:
                number = input("Call established press ENTER if want to END call >> ")
            except Exception as e:
                logging.error(str(e))
                return 0
        else:
            t0 = time.time()
            while time.time() < t0+timeout:
                try:
                    received = (self.ser.read(20).splitlines()[-1]).decode()
                    logging.info('\t'+received)
                except IndexError:
                    received=''
                if "CONN" in received:
                    if duration>=0:
                        time.sleep(duration)
                    success=2
                    break

        if duration>=0:
            if not self.sendAtCommand("ATH"):
                logging.error("To send AT command: ATH")
                return 0            

        return success

    def resetRadio():
        if not self.sendAtCommand("AT+CFUN=0"):
            logging.error("To send AT command: ATM")
            return 0
        if not self.sendAtCommand("AT+CFUN=1"):
            logging.error("To send AT command: ATM")
            return 0
        return 1
