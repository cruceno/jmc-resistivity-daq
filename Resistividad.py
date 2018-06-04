# -*- coding: utf-8 -*-
'''
Created on 17/10/2013
Programa de adquisicion de daos para ensayos de ciclotermico modificado
para realizar ensayos de resistividad
@author: Cruceno Javier
    
'''
# Importar librerias necesarias
# interfaz grafica
from PyQt4 import QtCore, QtGui, uic

# Comunicacion con sistema y manejo de puerto serie
import sys, time
import scan_serial

from StringIO import StringIO

# Manejo numerico de datos
import numpy as np

# Librerias para graficar en el ploter
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import UniversalLibrary as UL

# Clase que configura parte de las graficas de datos -----------------------------

class canvas( FigureCanvas ):

    def __init__( self, parent ):
        # Se instancia el objeto figure
        self.fig = Figure()
        # Se define la grafica en coordenadas polares
        self.axes = self.fig.add_subplot( 111 )

        # Se define una grilla
        self.axes.grid( True )

        # se inicializa FigureCanvas
        FigureCanvas.__init__( self, self.fig )
        # se define el widget padre
        self.setParent( parent )
        # se define el widget como expandible
        FigureCanvas.setSizePolicy( self,
                QtGui.QSizePolicy.Expanding,
                QtGui.QSizePolicy.Expanding )
        # se notifica al sistema de la actualizacion
        # de la politica
        FigureCanvas.updateGeometry( self )
        self.fig.canvas.draw()


# Clase que define el subproceso que va a realizar la adquisicion de datos-------------
class Test_Resistividad ( QtCore.QThread ):
    def __init__ ( self ):
        QtCore.QThread.__init__( self )

        self.exiting = False
    def test ( self,
               outfile,
               lock_in_sensitivity,
               multimeter,
               usb_temp_ai_temp_channels,
               usb_temp_ai_volt_channels,
               data_per_second,
               BoardNum,
               s_port ):
        import Multimetros
        if multimeter == 'AG34410A':

            self.multimeter=Multimetros.AG34410A()
            self.multimeter.write( '*RST' )
            time.sleep( 0.1 )
            self.multimeter.write( 'CONF:VOLT:DC AUTO' )
            time.sleep( 0.5 )
            self.time_stamp = 0
            self.delay = 1. / ( float ( data_per_second ) * ( 1 + len ( usb_temp_ai_volt_channels ) ) )
            
        elif multimeter == 'AG34401A':

            self.multimeter= Multimetros.AG34401A(str(s_port))
            self.time_stamp = 0
            self.delay = 1. / ( float ( data_per_second ) * ( 1 + len ( usb_temp_ai_volt_channels ) ) )
            
        else:
            self.multimeter = multimeter
            self.delay = 1. / ( float ( data_per_second ) * ( len ( usb_temp_ai_temp_channels ) + len ( usb_temp_ai_volt_channels ) ) )
            
        self.refresh = data_per_second
        self.BoardNum = BoardNum
        self.TempChannels = usb_temp_ai_temp_channels
        self.VoltChannels = usb_temp_ai_volt_channels
        self.savedata = False
        self.outfile = outfile
        self.zero_time=0
        self.lock_in_sensitivity=lock_in_sensitivity
        self.zero_lockin=False
        self.zero_lock_in = 0
        self.start()

    def run ( self ):
        first = True
        TempVal = 0.0
        VoltVal = 0.0
        self.zero_time = time.time()
        count =0
##        print "en run"
        while not self.exiting:
           # print "en bucle"
            #===================================================================
            # Lectura del dispositivo USB-TEMP-IA
            #===================================================================

            TempRead = []
            VoltRead = []
            if self.multimeter == False:
##                print "Entre en temp channels"
                for c in self.TempChannels:
##                    print "En TempChanesls USB TEM IA"
                    TempRead.append ( UL.cbTIn( self.BoardNum,
                                    c,
                                    UL.CELSIUS ,
                                    TempVal,
                                    UL.FILTER ) )
                    time.sleep( self.delay )

            for c in self.VoltChannels:
                #print "En VoltChanesls USB TEM IA canal:"+str(c)
                VoltRead.append ( UL.cbVIn( self.BoardNum,
                                            c,
                                            UL.cbGetConfig( UL.BOARDINFO,
                                                            self.BoardNum,
                                                            c,
                                                            UL.BIRANGE,
                                                            ConfigVal = 0 ),
                                            VoltVal,
                                            Option = None ) )
                time.sleep( self.delay )
            #==================================================================
            
            if self.multimeter:
                if self.multimeter.name=='AG34410A':
                    self.multimeter.write( 'DISP:WIND2:TEXT "Midiendo ..."' )
                    self.multimeter.write( 'READ?' )
                if self.multimeter.name=='AG34401A':
                    self.multimeter.write( 'DISPLAY:TEXT "Midiendo ..."\n' )
                    self.multimeter.write( 'READ?\n' )
                temp_data = float ( self.multimeter.read() ) * 1000
                print "Valor Multimetro * 1000: "+str(temp_data)
    #           Pasar de milivoltios a gracdos centigrado el valor leido por el multimetro
                # Polinomio para rango intermedio  -272 a 150 C

                if temp_data < 2: 
                    
                    Y = 25.39459 * temp_data 
                    Y-= 0.44494 * temp_data ** 2 
                    Y+= 0.05652 * temp_data ** 3 
                    Y-= 0.00412 * temp_data ** 4 
                    Y+= 0.0011 * temp_data ** 5 
                    Y-= 1.39776E-4 * temp_data ** 6 
                    Y+= 4.40583E-6 * temp_data ** 7 
                    Y+= 7.709E-8 * temp_data ** 8
                    
                #Polinomio para rango positivo 0 a 500 C     
                if temp_data >=2 :
                    
                    Y = 25.26032 * temp_data
                    Y-= 0.57128 * temp_data ** 2
                    Y+= 0.13393 * temp_data ** 3
                    Y-= 0.01411 * temp_data ** 4
                    Y+= 7.7329E-4 * temp_data ** 5
                    Y-= 2.32438E-5 * temp_data ** 6
                    Y+= 3.64924E-7 * temp_data ** 7
                    Y-= 2.34283E-9 * temp_data ** 8
                    
                temp_sample=Y
                
                
            else:
                #  temp_down = TempRead[0]
                temp_sample = TempRead[0]
                #  temp_up = TempRead[2]
                
            #======================================================================
            # Valor del Lock In
            #======================================================================

            Lock_In = VoltRead[0]*self.lock_in_sensitivity/10

            #======================================================================

            timestamp = time.time() - self.zero_time

#           Creando variable (lista) para almacenar datos en un archivo

            data = [timestamp, 
                    temp_sample, 
                    Lock_In]

            #===================================================================
            # Guardando datos en disco duro
            #===================================================================
            if self.savedata:
                
                if first:
                    fsock = open( self.outfile, 'w' )
                    first = False
                else:
                    fsock = open( self.outfile, 'a' )
                    
                if self.multimeter:
                    if self.multimeter.name=='AG34410A':
                        self.multimeter.write( 'DISP:WIND2:TEXT "Guardando..."' )
                    if self.multimeter.name=='AG34401A':
                        self.multimeter.write( 'DISPLAY:TEXT "Guardando..."\n' )
                                            
                line = str ( data[0] ) + '\t' 
                line+= str ( data[1] ) + '\t' 
                line+= str ( data[2] ) + '\n' 
                
                fsock.write( line )
                fsock.close()
            #====================================================================
            else:
                
                tempfsock = open( 'tempdata', 'w' )
                
                line = str ( data[0] ) + '\t' 
                line+= str ( data[1] ) + '\t' 
                line+= str ( data[2] ) + '\n' 
                
                tempfsock.write( line )
                tempfsock.close()            
            if count == self.refresh:
                
                self.emit( QtCore.SIGNAL ( "ready(PyQt_PyObject)" ), data )
                count = 0
            count+=1
        if self.multimeter:
            if self.multimeter.name =='AG34410A':
                self.multimeter.write( '*CLS' )
            if self.multimeter.name =='AG34401A':
                self.multimeter.write( '*CLS\n' )
        tempfsock.close() 
        fsock.close()
        self.exit()

    def __del__( self ):
        self.exiting = True
        self.ser.close()
        self.wait()
        
class Main( QtGui.QMainWindow ):

    def __init__( self ):

        #Inicializamos interfaz graica---------------------------
        QtGui.QMainWindow.__init__( self )

        uic.loadUi( 'Resistividad_UI.ui', self )
        #---------------------------------------------------------------------------

        #Generamos los planos donde graficaremos los datos--------------------------
        # Inicializando base de ploteo para mainplot--------------------------------
        self.vbl_main = QtGui.QVBoxLayout( self.gb_mainplot )
        self.maincanvas = canvas( self.gb_mainplot )
        self.vbl_main.insertWidget( 0, self.maincanvas )
        #--------------------------------------------------------------------------
        # Inicializando base de ploteo para auxplot_1------------------------------
        self.vbl_aux_1 = QtGui.QVBoxLayout( self.gb_auxplot_1 )
        self.auxcanvas_1 = canvas( self.gb_auxplot_1 )
        self.vbl_aux_1.insertWidget( 0, self.auxcanvas_1 )
        #--------------------------------------------------------------------------
        # Inicializando base de ploteo para auxplot_2------------------------------
        self.vbl_aux_2 = QtGui.QVBoxLayout( self.gb_auxplot_2 )
        self.auxcanvas_2 = canvas( self.gb_auxplot_2 )
        self.vbl_aux_2.insertWidget( 0, self.auxcanvas_2 )
        #--------------------------------------------------------------------------

        #Trhead de lectura de datos-------------------------------------------------------------------------------
        self.resistividad = Test_Resistividad()
        self.read_data = False
        self.norm_lock_in = False
        #====================================================================
        # Conectamos seniales de los threads con funciones de manejo de datos

        self.connect(self.resistividad,
                     QtCore.SIGNAL("ready(PyQt_PyObject)" ),
                     self.show_data)

        #=======================================================================

        ports=scan_serial.scan(30, False)
        for i in range(self.cbx_temperature_sample_channel.count()):
            self.cbx_temperature_sample_channel.removeItem(i)
        for port in ports:
            self.cbx_temperature_sample_channel.addItem(port[1])
        self.cbx_temperature_sample_input.activated.connect(self.on_cbx_temperature_sample_input_activated)
    #===========================================================================================
    # Las siguientes 4 funciones son las encargadas de ajustar la escala de la grafica principal
    # por medio de los controles proporcionados al usuario
    
    @QtCore.pyqtSlot()
    def on_sb_xmin_valueChanged( self ):
        self.maincanvas.axes.set_xlim( self.sb_xmin.value(), self.sb_xmax.value() )
        self.maincanvas.draw()
        
    @QtCore.pyqtSlot( int )
    def on_sb_xmax_valueChanged( self ):
        self.maincanvas.axes.set_xlim( self.sb_xmin.value(), self.sb_xmax.value() )
        self.maincanvas.draw()
        
    @QtCore.pyqtSlot( int )
    def on_sb_ymin_valueChanged( self ):
        self.maincanvas.axes.set_ylim( self.sb_ymin.value(), self.sb_ymax.value() )
        self.maincanvas.draw()
        
    @QtCore.pyqtSlot( int )
    def on_sb_ymax_valueChanged( self ):
        self.maincanvas.axes.set_ylim( self.sb_ymin.value(), self.sb_ymax.value() )
        self.maincanvas.draw()    
    #============================================================================================

#===============================================================================
# Funciones de los botones accionados por el usuario para controlar el inicio y el final
# del ensayo
#===============================================================================
    @QtCore.pyqtSlot()
    def on_pb_start_clicked ( self ):
        self.Resistividad_test()
        self.pb_start_save_data.setEnabled(True)
    
    @QtCore.pyqtSlot()
    def on_pb_end_clicked ( self ):
        self.resistividad.exiting = True
        while self.resistividad.isRunning():
            continue
        footer = self.ptx_footer.toPlainText() + '\n'
        self.comented_footer = ''
        for line in footer.split( '\n' ):
            self.comented_footer = self.comented_footer + self.le_output_file_commentchar.text() + line + '\n'


        f = open( self.le_output_file_path.text() + '.txt' )
        s = self.comented_header + f.read() + self.comented_footer
        f.close()

        f = open( self.le_output_file_path.text() + '.txt', 'w' )
        f.write( s )
        f.close()
        self.pb_end.setEnabled(False)
        self.pb_start.setEnabled( True )
        self.pb_start_save_data.setEnabled( False )

    @QtCore.pyqtSlot ()
    def on_pb_start_save_data_clicked ( self ):
        self.pb_start_save_data.setEnabled( False )
        self.resistividad.zero_time = time.time()
        self.maincanvas.axes.cla()
        self.maincanvas.axes.grid( True )
        self.auxcanvas_2.axes.cla()
        self.auxcanvas_2.axes.grid( True )
        self.auxcanvas_1.axes.cla()
        self.auxcanvas_1.axes.grid( True )
        self.resistividad.savedata = True
        self.read_data = True
    
    @QtCore.pyqtSlot()
    def on_pb_normalizar_clicked ( self ):
        if self.read_data:
            
            f = open( self.le_output_file_path.text() + '.txt' )
            s = StringIO( f.read() )
            f.close()
            s.seek( 0 )

            lock_in = np.genfromtxt(   s,
                                            usecols = ( 2 ),
                                            deletechars = "\n",
                                            dtype = float,
                                            autostrip = True,
                                            unpack = True )
            self.norm_lock_in=lock_in[-1]
##            print self.norm_lock_in
            
        else:
            f = open( 'tempdata' )
            s = StringIO( f.read() )
            f.close()
            s.seek( 0 )

            lock_in = np.genfromtxt( s,
                                  #usecols = ( 2 ),
                                  deletechars = "\n",
                                  dtype = float,
                                  autostrip = True)
        
            self.norm_lock_in=lock_in[2]
            
    @QtCore.pyqtSlot()
    def on_tlb_output_file_path_pressed( self ):
        # seleccionar archivo
        self.le_output_file_path.setText( QtGui.QFileDialog.getSaveFileName( parent = None ) )

    @QtCore.pyqtSlot()
    def on_cbx_temperature_sample_input_activated(self):
        if self.cbx_temperature_sample_input.currentText()=='AG34401A':
            ports=scan_serial.scan(30, False)
            for i in range(self.cbx_temperature_sample_channel.count()):
                self.cbx_temperature_sample_channel.removeItem(i)
            for port in ports:
                self.cbx_temperature_sample_channel.addItem(port[1])
                
        if self.cbx_temperature_sample_input.currentText()=='AG34410A':
            for i in range(self.cbx_temperature_sample_channel.count()):
                self.cbx_temperature_sample_channel.removeItem(i)
        
        if self.cbx_temperature_sample_input.currentText()=='USB TEMP AI':
            for i in range(self.cbx_temperature_sample_channel.count()):
                self.cbx_temperature_sample_channel.removeItem(i)
            for i in range(0,4):
                self.cbx_temperature_sample_channel.addItem(str (i), str(i))
                
    def Resistividad_test ( self ):
        # inicializar archivos leer configuraciones inicializar puerto serie
        valid = False
          
        if self.le_output_file_path.text() != '':
            valid = True
        else:
            self.pb_start.setEnabled( True )
            self.statusBar().showMessage( 'El campo que indica el archivo de destino no puede estar vacio' )
        if valid:
            self.pb_start.setEnabled( False )
            outfile = self.le_output_file_path.text()
            outfile += '.txt'
            lock_in_sensitivity=self.dsbx_lock_in_sensitivity.value()
            header = 'Comentarios:' + self.ptx_header.toPlainText() + '\n'
            header += 'Lock in sensitivity: ' + str ( self.dsbx_lock_in_sensitivity.value() ) + '\n'

            header += 'Dispositivos y canales utilizados: \n'

            header += '\t Temperatura de la muestra: ' + str ( self.cbx_temperature_sample_input.currentText() ) + '\n'
            if self.cbx_temperature_sample_input.currentText() != 'USB TEMP AI':
                pass
            else:
                header += '\t\t Canal: ' + str ( self.cbx_temperature_sample_channel.currentText() ) + '\n'        
            header += '\t Lock-In: ' + str ( self.cbx_lock_in_input.currentText() ) + '\n'
            header += '\t\t Canal: ' + str ( self.cbx_lock_in_channel.currentText() ) + '\n'

            header += '\n Datos por segundo: ' + str ( self.sb_data_per_second.value() ) + '\n\n'
            header += 'Tiempo (s) \t T muestra (C) \t Lock-in (mV o uV) \n'

            self.comented_header = ''
            for line in header.split( '\n' ):
                self.comented_header = self.comented_header + self.le_output_file_commentchar.text() + line + '\n'

            if self.cbx_temperature_sample_input.currentText() != 'USB TEMP AI':
                
                multimeter = self.cbx_temperature_sample_input.currentText()
                if self.cbx_temperature_sample_input.currentText()=='AG34401A':
                    s_port=self.cbx_temperature_sample_channel.currentText()
                usb_temp_ai_temp_channels=False

            else:
                multimeter = False
                s_port=False
                usb_temp_ai_temp_channels = [int ( self.cbx_temperature_sample_channel.currentText() )]
                
            usb_temp_ai_volt_channels = [int ( self.cbx_lock_in_channel.currentText() )]

            self.resistividad.test( outfile,
                                    lock_in_sensitivity,
                                    multimeter,
                                    usb_temp_ai_temp_channels,
                                    usb_temp_ai_volt_channels,
                                    self.sb_data_per_second.value(),
                                    self.sb_board_num.value(),
                                    s_port )
            self.count = 0
            self.pb_normalizar.setEnabled( True )
            self.pb_end.setEnabled( True )

    @QtCore.pyqtSlot ()
    
    def show_data ( self, data ):
        del data
        if self.read_data:
            
            f = open( self.le_output_file_path.text() + '.txt' )
            s = StringIO( f.read() )
            f.close()
            s.seek( 0 )

            time_np, temp_sample, lock_in = np.genfromtxt(   s,
                                                             usecols = ( 0, 1, 2 ),
                                                             deletechars = "\n",
                                                             dtype = float,
                                                             autostrip = True,
                                                             unpack = True )
            print [time_np[-1], temp_sample[-1], lock_in[-1]]
            if time_np[-1] < 60:
                self.lcd_time_second.display( str ( int (time_np[-1] ) ) )
            else:
                m = time_np[-1] // 60
                s = time_np[-1] % 60
                if m < 60:
                    self.lcd_time_second.display( str ( int ( s ) ) )
                    self.lcd_time_minute.display( str ( int ( m ) ) )
                else:
                    h = m // 60
                    m = m % 60
                    self.lcd_time_second.display( str ( int ( s ) ) )
                    self.lcd_time_minute.display( str ( int ( m ) ) )
                    self.lcd_time_hour.display( str ( int ( h ) ) )

            if self.norm_lock_in:  # Si esta normalizado nos muestra el lockin normalizado  
                self.lcd_var_2.display( str (float(lock_in[-1])/float(self.norm_lock_in) ))
            else: # Si no esta normalizado nos muestra simplente el lockin
                self.lcd_var_2.display( str ( lock_in[-1] ))

            self.lcd_var_5.display( str(float ( lock_in[-1] ))) # Nos muestra el lockin sin normalizar en mV o uV
            
            self.lcd_var_3.display( str ( float(lock_in[-1])*10 / float (self.dsbx_lock_in_sensitivity.value()) ) ) # Muestra el lock-in en Voltios. 


##==============================IMPORTANTE !!!!=========================================
##======================================================================================
## MODIFICA j PARA CAMBIAR CANTIDAD DE PUNTOS USADOS PARA EL CALCULO DE VELOCIDAD           
##======================================================================================
##======================================================================================
            j=50 * self.sb_data_per_second.value()
##======================================================================================
##======================================================================================
            if np.size( temp_sample) >= j:
           
                temp_a=np.polyfit(time_np[j*(-1):-1]/60, temp_sample[j*-1:-1],1)[0]
                self.lcd_var_4.display( str ( temp_a ) )

            self.lcd_temperature_sample.display( str ( temp_sample[-1] ) )
            
            # Ploteando en los canvas ya definidos con las funciones heredadas de la clase canvas
            # Deformacion en funcion de temperatura
            self.maincanvas.axes.cla()
            self.maincanvas.axes.grid( True )
            self.statusBar().showMessage( 'Ploteando principal...' )
            self.maincanvas.axes.set_xlim( self.sb_xmin.value(), self.sb_xmax.value() )
            self.maincanvas.axes.set_ylim( self.sb_ymin.value(), self.sb_ymax.value() )            
            self.maincanvas.axes.plot( temp_sample, lock_in, 'og' )
            
            for label in self.maincanvas.axes.get_xticklabels():
                # label is a Text instance
                label.set_rotation ( 45 )
            self.maincanvas.fig.canvas.draw()
            min5=300*self.sb_data_per_second.value()

            if np.size( time_np ) < min5:
                temp_range = np.array( [ np.min( temp_sample ),
                                         np.max( temp_sample )] )

                # Temperatura en funcion de tiempo
                self.auxcanvas_2.axes.cla()
                self.auxcanvas_2.axes.grid( True )
                self.statusBar().showMessage( 'Ploteando Auxiliar 2...' )
                self.auxcanvas_2.axes.set_xlim( time_np[0], time_np[-1] )
                self.auxcanvas_2.axes.set_ylim( np.min( temp_range ) - abs (np.min( temp_range )) * 20 / 100,
                                                np.max( temp_range ) + abs (np.max( temp_range )) * 20 / 100 )
                
                self.auxcanvas_2.axes.plot( time_np, temp_sample, 'r')
                
                for label in self.auxcanvas_2.axes.get_xticklabels():
                    # label is a Text instance
                    label.set_visible( False )
                self.auxcanvas_2.fig.canvas.draw()

                # Deformacion en funcion de tiempo
                self.auxcanvas_1.axes.cla()
                self.auxcanvas_1.axes.grid( True )
                self.statusBar().showMessage( 'Ploteando Auxiliar 1...' )
                self.auxcanvas_1.axes.set_xlim( time_np[0], time_np[-1] )
                
                self.auxcanvas_1.axes.set_ylim( np.min( lock_in ) - abs (np.max( lock_in )- np.min( lock_in )) * 20 / 100,
                                                np.max( lock_in ) + abs (np.max( lock_in )- np.min( lock_in )) * 20 / 100 )
                
                self.auxcanvas_1.axes.plot( time_np, lock_in, 'y' )
                
                for label in self.auxcanvas_1.axes.get_xticklabels():
                    # label is a Text instance
                    label.set_visible( False )
                self.auxcanvas_1.fig.canvas.draw()

            else:
                temp_range = np.array( [ np.min(temp_sample[min5*-1:-1]),
                                         np.max(temp_sample[min5*-1:-1]) ] )

                self.auxcanvas_2.axes.cla()
                self.auxcanvas_2.axes.grid( True )
                self.statusBar().showMessage( 'Ploteando 5Auxiliar 2...' )
                self.auxcanvas_2.axes.set_xlim( time_np[min5*-1], time_np[-1] )
                
                self.auxcanvas_2.axes.set_ylim( np.min( temp_range ) - abs (np.max(temp_range)-np.min( temp_range )) * 20 / 100,
                                                np.max( temp_range ) + abs (np.max( temp_range )-np.min(temp_range)) * 20 / 100 )
                
                self.auxcanvas_2.axes.plot( time_np[min5*-1:-1], temp_sample[min5*-1:-1], 'r' )
                
                for label in self.auxcanvas_2.axes.get_xticklabels():
                    # label is a Text instance
                    label.set_visible( False )
                self.auxcanvas_2.fig.canvas.draw()

                # Deformacion en funcion de tiempo
                self.auxcanvas_1.axes.cla()
                self.auxcanvas_1.axes.grid( True )
                self.statusBar().showMessage( 'Ploteando Auxiliar 1...' )
                self.auxcanvas_1.axes.set_xlim( time_np[min5*-1], time_np[-1] )
                
                self.auxcanvas_1.axes.set_ylim( np.min( lock_in[min5*-1:-1] ) - abs (np.min( lock_in[min5*-1:-1] )) * 20 / 100,
                                                np.max( lock_in[min5*-1:-1] ) + abs (np.max( lock_in[min5*-1:-1] )) * 20 / 100 )
                
                self.auxcanvas_1.axes.plot( time_np[min5*-1:-1], lock_in[min5*-1:-1], 'y' )
                
                for label in self.auxcanvas_1.axes.get_xticklabels():
                    # label is a Text instance
                    label.set_visible( False )
                self.auxcanvas_1.fig.canvas.draw()

            del temp_sample, lock_in, time_np, temp_range

### Antes de Inicio de registro de datos 
        else:
            f = open( 'tempdata' )
            s = StringIO( f.read() )
            f.close()
            s.seek( 0 )

            data = np.genfromtxt( s,
                                  deletechars = "\n",
                                  dtype = float,
                                  autostrip = True,
                                  unpack = True )
            print data
            if data[0] < 60:
                self.lcd_time_second.display( str ( int (data[0] ) ) )
            else:
                m = data[0] // 60
                s = data[0] % 60
                if m < 60:
                    self.lcd_time_second.display( str ( int ( s ) ) )
                    self.lcd_time_minute.display( str ( int ( m ) ) )
                else:
                    h = m // 60
                    m = m % 60
                    self.lcd_time_second.display( str ( int ( s ) ) )
                    self.lcd_time_minute.display( str ( int ( m ) ) )
                    self.lcd_time_hour.display( str ( int ( h ) ) )
            if self.norm_lock_in:
                mostrame = data[2]/self.norm_lock_in
                self.lcd_var_2.display( str (mostrame))

            else:
                self.lcd_var_2.display( str (  float ( data[2] ) ))
            self.lcd_var_3.display( str ( float ( data[2])*10/ float (self.dsbx_lock_in_sensitivity.value() )))
            self.lcd_var_5.display( str ( float ( data[2])))
            self.lcd_temperature_sample.display( str ( data[1] ) )

def main():
    app = QtGui.QApplication( sys.argv )
    DAQ = Main()
    DAQ.show()
    sys.exit( app.exec_() )
if __name__ == '__main__':
    main()
