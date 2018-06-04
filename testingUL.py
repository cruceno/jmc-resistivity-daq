import UniversalLibrary as UL
# import numpy as np
import time, sys
from PyQt4 import QtCore, QtGui
BoardNum = 0
TempChanel = ( 0, 1, 2, 3 )
VoltChanel = ( 0, 1, 2, 3 )
TempRead = 0.0
VoltRead = 0.0
ConfigVal = 0
med = True
# UL.cbDConfigPort( BoardNum, UL.AUXPORT, UL.DIGITALOUT )
# time.sleep( 0.1 )
#
# UL.cbDBitOut( BoardNum, UL.AUXPORT, 0, BitValue = 1 )
# time.sleep( 0.1 )
# print UL.cbDIn( BoardNum, UL.AUXPORT, DataValue = 0 )

# while med:
#     #  print UL.cbGetConfig( UL.BOARDINFO, BoardNum, BoardNum , UL.BIRANGE , ConfigVal )
#     for c in TempChanel:
#         print UL.cbTIn( BoardNum, c, UL.CELSIUS , TempRead, UL.NOFILTER )
#         time.sleep( 0.1 )
#     for c in VoltChanel:
#         print UL.cbVIn( BoardNum, 1, 10, VoltRead, Option = None )
#         time.sleep( 0.1 )
# print UL.cbVIn( BoardNum, 1, UL.cbGetConfig( UL.BOARDINFO, 0, 0, UL.BIRANGE, ConfigVal = 0 ), VoltRead, Option = None )
class USB_TC_AI ( QtCore.QThread ):
    ''' Con esta clase creamos el Hilo que se va a encargar de tomar las lecturas del USB-TC-AI'''
    def __init__ ( self, parent = None ):

        QtCore.QThread.__init__( self, parent )
        self.exiting = False
        self.message = ''
        self.channels = {'USB_TC_AI_T0':0,
                       'USB_TC_AI_T1':1,
                       'USB_TC_AI_T2':2,
                       'USB_TC_AI_T3':3,
                       'USB_TC_AI_V0':0,
                       'USB_TC_AI_V1':1,
                       'USB_TC_AI_V2':2,
                       'USB_TC_AI_V3':3
                       }

#        Se utilizaran solo grados CELSIUS
#         temp_scales = {'CELSIUS':UL.CELSIUS,
#                      'KELVIN':UL.KELVIN,
#                      'FARENHEITH':UL.FAHRENHEIT,
#                      'NOSCALE':UL.NOSCALE
#                      }

    def read_channels ( self, BoardNum, TempChanels, VoltChannels, data_per_second ):

        self.BoardNum = BoardNum
        self.TempChanels = TempChanels
        self.VoltChanels = VoltChannels
        self.delay = 1. / ( data_per_second * ( len ( TempChanels ) + len ( VoltChannels ) ) )
        print self.delay
        self.start()

    def run ( self ):
        TempRead = 0.0
        VoltRead = 0.0
        while not self.exiting:
            for c in self.TempChanels:
                # Probar mediciones con filtro y sin filtro
                print UL.cbTIn( self.BoardNum,
                                self.channels[c],
                                UL.CELSIUS ,
                                TempRead,
                                UL.FILTER )
                time.sleep( self.delay )

            for c in self.VoltChanels:
                print UL.cbVIn( self.BoardNum,
                                self.channels[c],
                                UL.cbGetConfig( UL.BOARDINFO,
                                                self.BoardNum,
                                                self.channels[c],
                                                UL.BIRANGE,
                                                ConfigVal = 0 ),
                                VoltRead,
                                Option = None )
                time.sleep( self.delay )

    def __del__ ( self ):
        self.exiting = True
        self.wait()
USB_TC = USB_TC_AI()

TempChannels = ['USB_TC_AI_T0',
              'USB_TC_AI_T1',
              'USB_TC_AI_T2',
              'USB_TC_AI_T3']
VoltChannels = ['USB_TC_AI_V0',
              'USB_TC_AI_V1',
              'USB_TC_AI_V2',
              'USB_TC_AI_V3']

def main():
    app = QtGui.QApplication( sys.argv )
    DAQ = USB_TC
    DAQ.read_channels( BoardNum, TempChannels, VoltChannels, 80. )
    sys.exit( app.exec_() )
main()
