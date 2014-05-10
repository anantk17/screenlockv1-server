import sys
import socket
import re
import os
from PySide import QtGui,QtCore
from KThread import *
from IP import *

class MainScreen(QtGui.QWidget):

    def __init__(self):
        self.OS = ""
        #self.host = '10.0.0.6'
        self.host = get_ip()
        self.port = 8082 
        self.running = False
        self.regMAC = ""
        self.regName =  ""
        super(MainScreen,self).__init__()
        self.initUI()

    def initUI(self):
        
        #print "HELLO"
        start = QtGui.QPushButton("Start")
        start.clicked.connect(self.sock_start)
        stop = QtGui.QPushButton("Stop")
        stop.clicked.connect(self.sock_stop)
        self.label1 = QtGui.QLabel('OS')
        self.label2 = QtGui.QLabel('Authorised Device')
        self.label3 = QtGui.QLabel('Device Name')
        self.label4 = QtGui.QLabel('MAC Address')
        self.textfield1 = QtGui.QLineEdit()
        self.textfield1.textChanged[str].connect(self.onChange1)
        self.textfield2 = QtGui.QLineEdit()
        self.textfield2.textChanged[str].connect(self.onChange2)

        combo = QtGui.QComboBox()
        combo.addItem("Select OS")
        combo.addItem("Ubuntu")
        combo.addItem("Xubuntu")
        combo.addItem("Kubuntu")
        combo.addItem("Windows")
        
        combo.activated[str].connect(self.onActivated)

        grid = QtGui.QGridLayout()
        #:grid.setSpacing(5)

        grid.addWidget(start,0,0)
        grid.addWidget(stop,0,3)
        grid.addWidget(self.label2,1,0)
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
        #self.label1.setText(text)
        #self.label1.adjustSize()

    def onChange1(self, text):
        self.regName =  text

    def onChange2(self, text):
        self.regMAC = text

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

        event.accept()

def main():
    app = QtGui.QApplication(sys.argv)
    ex = MainScreen()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

