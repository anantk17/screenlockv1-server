import sys
import socket
import re
import os
import pickle
from PySide import QtGui,QtCore
from KThread import *
from IP import *

class MainScreen(QtGui.QWidget):

    def __init__(self):
        self.store ={}
        ### Load persistent data from file 
        try:
            self.store = pickle.load(open(".screenlock.p","rb"))
                   
        ### If pickle file is not present, create a new pickle dump file
        except IOError:
            self.store = {"OS":"", "MAC":"","Name":""}
            self.f = open(".screenlock.p","wb")
            pickle.dump( self.store,f)
        
        self.OS = self.store["OS"]
        self.regMAC = self.store["MAC"]
        self.regName = self.store["Name"]
        
        ###Set host ip and port
        self.host = get_ip()
        self.port = 8082

        ###Running status for the network thread
        self.running = False
        
        super(MainScreen,self).__init__()
        self.initUI()

    def initUI(self):
        
        start = QtGui.QPushButton("Start")
        start.clicked.connect(self.sock_start)
        stop = QtGui.QPushButton("Stop")
        stop.clicked.connect(self.sock_stop)
        self.label1 = QtGui.QLabel('OS')
        self.label2 = QtGui.QLabel('Authorised Device')
        self.label3 = QtGui.QLabel('Device Name')
        self.label4 = QtGui.QLabel('MAC Address')
        self.edit = QtGui.QPushButton("Edit")
        self.edit.clicked.connect(self.butchange1)
        self.textfield1 = QtGui.QLineEdit()
        self.textfield1.setText(self.regName)
        self.textfield1.setReadOnly(True)
        self.textfield1.textChanged[str].connect(self.onChange1)
        self.textfield2 = QtGui.QLineEdit()
        self.textfield2.setText(self.regMAC)
        self.textfield2.setReadOnly(True)
        self.textfield2.textChanged[str].connect(self.onChange2)
        self.textfield2.setInputMask("HH:HH:HH:HH:HH:HH")
        
        combo = QtGui.QComboBox()
        oslist = ["Select OS", "Ubuntu", "Xubuntu", "Kubuntu", "Windows"]
        combo.addItems(oslist)

        if self.OS == "":
            combo.setCurrentIndex(0)
        else:
            combo.setCurrentIndex(oslist.index(self.OS))
        
        combo.activated[str].connect(self.onActivated)

        grid = QtGui.QGridLayout()
        #:grid.setSpacing(5)

        grid.addWidget(start,0,0)
        grid.addWidget(stop,0,3)
        grid.addWidget(self.label2,1,0)
        grid.addWidget(self.edit,1,2)
        grid.addWidget(self.label3,2,0)
        grid.addWidget(self.textfield1,2,2)
        grid.addWidget(self.label4,3,0)
        grid.addWidget(self.textfield2,3,2)
        grid.addWidget(self.label1,4,0)
        grid.addWidget(combo,4,3)
        self.setLayout(grid)
        self.setGeometry(300,300,350,300)
        #self.move(300,150)
        self.setWindowTitle('ScreenLock')
        self.show()

    def onActivated(self,text):
        self. OS = text

    def onChange1(self, text):
        self.regName =  text

    def onChange2(self, text):
        self.regMAC = text

    def butchange1(self):
        self.edit.setText("Save")
        self.edit.clicked.connect(self.butchange2)
        #self.editreg()
        self.textfield1.setReadOnly(False)
        self.textfield2.setReadOnly(False)
    
    def butchange2(self):
        self.edit.setText("Edit")
        self.edit.clicked.connect(self.butchange1)
        #self.editreg()
        self.textfield1.setReadOnly(True)
        self.textfield2.setReadOnly(True)

    def net_op(self,sock):
        if(self.running):
            print "Socket Opened"
            self.sock.bind((self.host,self.port))
            self.sock.listen(1)
            while self.running:        
                    csock, caddr = self.sock.accept()
                    print "Connection from : " + str(caddr)
                    req = csock.recv(1024)
                    req = bytes.decode(req)
                    req =str(req)
                    req = req.split(' ')

                    if(req[0] == 'GET'):
                        url = req[1]
                        urlsplit = url.split('?')

                        if(urlsplit[0] == '/lock'):
                            varstring = urlsplit[1]
                            var, value = varstring.split('=')

                            if(var == 'y' and value == 'true'):
                                if (self.OS == 'Xubuntu'):
                                    os.system("xflock4")
                                elif (self.OS == "Windows"):
                                    os.system("rundll32 user32.dll,LockWorkStation")
                                elif (self.OS == 'Ubuntu'):
                                    os.system("gnome-screensaver-command -l")
                            #elif(var == 'reg'):
                                #    register(value)
                            else:
                                print "Returning 404"
                                csock.sendall("HTTP/1.0 404 Not Found\r\n")
                        else:
                            print "Returning 404"
                            csock.sendall("HTTP/1.0 404 Not Found\r\n")
                    else:
                        print "Returning 404"
                        csock.sendall("HTTP/1.0 404 Not Found\r\n")
            csock.close()


    def sock_start(self):
        if(self.OS == ""):
            msgBox = QtGui.QMessageBox()
            msgBox.setText("Please select your OS")
            msgBox.exec_()
            return

        if(self.running == False):
            self.running  = True
            self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
            self.t = KThread(target = self.net_op,kwargs={'sock':self.sock})
            self.t.start()
            

    def sock_stop(self):
        if(self.running == True):
            self.running = False
            self.t.kill()
            self.sock.shutdown(socket.SHUT_RDWR)
            self.sock.close()
            print "Socket Closed"
  
    def closeEvent(self,event):
        if(self.running == True):
            self.running = False
            self.t.kill()
            self.sock.shutdown(socket.SHUT_RDWR)
            self.sock.close()
        self.store["OS"] = self.OS
        self.store["MAC"] = self.regMAC
        self.store["Name"] = self.regName
        pickle.dump(self.store,open(".screenlock.p","wb"))

        event.accept()

def main():
    app = QtGui.QApplication(sys.argv)
    ex = MainScreen()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

