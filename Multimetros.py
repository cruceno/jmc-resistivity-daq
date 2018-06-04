# -*- coding: utf-8 -*-
'''
Created on 17/10/2013

@author: Cruceno Javier
    
'''

class AG34410A():
    '''
    classdocs
    '''
    def __init__(self, params):
        '''
        Constructor
        '''
        # Importar librerias para manejo de protocolos VISA
        from pyvisa.vpp43 import visa_library
        visa_library.load_library( "visa32.dll" )
        import visa
        self.multimeter = visa.instrument( 'USB0::2391::1543::my47030898::0' )
        self.name="AG34410A"

class AG34401A ():
    def __init__(self, s_port):
        '''Multimetro Agilen 34401A, Comunicacion por RS-232'''
        import serial
        self.S_34401A= serial.Serial(
                                port=s_port,
                                baudrate=9600,
                                bytesize=serial.EIGHTBITS,
                                parity=serial.PARITY_NONE,
                                stopbits=serial.STOPBITS_TWO,
                                timeout=None,
                                xonxoff=0,
                                rtscts=0,
                                writeTimeout=None,
                                dsrdtr=1,
                                interCharTimeout=None
                                )
        self.S_34401A.close()
        self.S_34401A.open()
        self.S_34401A.write('SYST:REM\n')
        self.S_34401A.write('*CLS\n')
        self.S_34401A.write('DISPLAY:TEXT "Conectado"\n')
        self.name="AG34401A"
        
    def read(self):
        return self.S_34401A.readline()
    
    def write (self, command):
        self.S_34401A.write(command)
        
    def __del__(self):
        self.S_34401A.close()
