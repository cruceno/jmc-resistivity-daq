# -*- coding: utf-8 -*-

'''
Created on 05/09/2016

@author: Cruceno Javier
    
'''
from time import sleep
              
class SR530():
    '''
    SOFTWARE DE COMUNICACION CON LOCK-IN SR530
    
    INTERFACE: RS232
    
    '''
         
    def getSerialConn(self,s_port):
        import serial
        try:
            self.serial = serial.Serial(
                            port=s_port,
                            baudrate=19200,
                            bytesize=serial.EIGHTBITS,
                            parity=serial.PARITY_ODD,
                            stopbits=serial.STOPBITS_ONE

                            )

            self.serial.close()
            sleep(1)
            self.serial.open()
            #self.write('Z\r')#Resetea el Lock-In la luz ERR se encendera por 3 seg
            #sleep(4)
            self.write('W 1\r')#Pone el valor de espera entre envio de caracteres del lock-in en 4ms
            jcmd='J '+str(ord('\n'))#especifica el fin de linea enviado por el lock in en <cr>
            self.write(jcmd)
            #self.write('W\r')
            #print 'Line:' + self.serial.readline()
            return 'Conectado.'
            
        except:
            return 'Error al conectar al puerto serie'
    def getSensitivity(self):
        sensitivitys={
                      '1':('10','nV',1e9),
                      '2':('20','nV',1e9),
                      '3':('50','nV',1e9),
                      '4':('100','nV',1e9),
                      '5':('200','nV',1e9),
                      '6':('500','nV',1e9),
                      '7':('1','uV',1e6),
                      '8':('2','uV',1e6),
                      '9':('5','uV',1e6),
                      '10':('10','uV',1e6),
                      '11':('20','uV',1e6),
                      '12':('50','uV',1e6),
                      '13':('100','uV',1e6),
                      '14':('200','uV',1e6),
                      '15':('500','uV',1e6),
                      '16':('1','mV',1e3),
                      '17':('2','mV',1e3),
                      '18':('5','mV',1e3),
                      '19':('10','mV',1e3),
                      '20':('20','mV',1e3),
                      '21':('50','mV',1e3),
                      '22':('100','mV',1e3),
                      '23':('200','mV',1e3),
                      '24':('500','mV',1e3),
                      }
        self.write('G')    
        s=self.read().strip('\n')
        return sensitivitys[s]
    
    def read(self):

        return self.serial.readline()

    def write(self,command):

        self.serial.write(command+'\r')

    def getStatus(self):
        '''
        Funcion para obtener el estado de todas las configuraciones del lock-in.
        Utiliza: read() write(). 
        Devuelve: Diccionario con los parametros de configuracion.
        '''
        sr530commands={'bandpass':'B',
                       'dyn':'D',
                       'ref-display':'C',
                       'expandch1':'E1',
                       'expandch2':'E2',
                       'frequency':'F',
                       'gain':'G',
                       'pre-amplifier':'H',
                       'remote':'I',
                       'line-filter':'L1',
                       'linex2-filter':'L2',
                       'ref-mode':'M',
                       'enbw':'N',
                       'offsertx':'OX',
                       'offserty':'OY',
                       'offsertr':'OR',
                       'phase-shift':'P',
                       'ref-trigger':'R',
                       'pre-time':'T1',
                       'post-time':'T2',
                       'aportx1':'X1',
                       'aportx2':'X2',
                       'aportx3':'X3',
                       'aportx4':'X4',
                       'aportx5':'X5',
                       'aportx6':'X6',
                  }           
        state=""
        for cfg, value in sr530commands.items():
            self.write(value+'\r')
            state +=cfg+': '+ self.read()
        
        
        return state
    
    def __del__(self):
        self.serial.close()

