# -*-encoding: utf-8 -*-
from PyQt4 import QtCore, QtGui
import RPi.GPIO as GPIO
import numpy as np
import pyqtgraph as pg
import random
import scipy
from pyqtgraph.ptime import time
import os, sys





class MainWindow(QtGui.QMainWindow):
    # ============== GPIO CONFIGURAÇÕES ============== #
    GPIO.setwarnings(False)                            #
    GPIO.setmode(GPIO.BOARD)                           #
    GPIO.cleanup()                                     #
    pinos = [37,35,33,31,29,23,21,19]                  # > LSB to MSB.
    for p in pinos:                                    #
        GPIO.setup(p,GPIO.IN,pull_up_down=GPIO.PUD_UP) #
    leituras = [0,0,0,0,0,0,0,0]
    usuario = 'Gabriel Vargas'
    idade = '18'
    sexo = 'Masculino'
    sangue = 'AB-'
    started = 0
    stop = 0
    fps = None
    windowWidth = 200
    max = 10
    cutOffD = 3
    cutOffT = 8
    cutOffA = 13
    cutOffB = 17
    Freq = 300
    Xm = np.zeros(windowWidth)
    Ym = np.zeros(windowWidth)

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.central_widget = QtGui.QStackedWidget()
        self.setCentralWidget(self.central_widget)
        self.login_widget = LoginWidget(self)
        self.login_widget.user.setText('Nome: {}'.format(self.usuario).decode('utf-8'))
        self.login_widget.age.setText('Idade: {} anos'.format(self.idade))
        self.login_widget.sex.setText('Sexo: {}'.format(self.sexo))
        self.login_widget.blood.setText('Tipo Sanguíneo: {}'.format(self.sangue).decode('utf-8'))

        self.login_widget.start.clicked.connect(self.plotter) #Geral
        self.login_widget.button.clicked.connect(self.Geral) #Geral
        self.login_widget.button1.clicked.connect(self.Entrada)
        self.login_widget.button2.clicked.connect(self.Beta)
        self.login_widget.button3.clicked.connect(self.Alfa)
        self.login_widget.button4.clicked.connect(self.Theta)
        self.login_widget.button5.clicked.connect(self.Delta)
        self.login_widget.button6.clicked.connect(self.Pause)
        self.login_widget.button7.clicked.connect(QtCore.QCoreApplication.instance().quit)
        self.central_widget.addWidget(self.login_widget)

    def Entrada(self):
        self.login_widget.entrada.show()
        self.login_widget.sinal.hide()
        self.login_widget.fft.hide()
        self.login_widget.delta.hide()
        self.login_widget.theta.hide()
        self.login_widget.alfa.hide()
        self.login_widget.beta.hide()
        self.login_widget.delta2.hide()
        self.login_widget.theta2.hide()
        self.login_widget.alfa2.hide()

    def Geral(self):
        self.login_widget.entrada.hide()
        self.login_widget.sinal.hide()
        self.login_widget.fft.hide()
        self.login_widget.delta.show()
        self.login_widget.theta.show()
        self.login_widget.alfa.show()
        self.login_widget.beta.show()
        self.login_widget.delta2.hide()
        self.login_widget.theta2.hide()
        self.login_widget.alfa2.hide()

    def Delta(self):
        self.login_widget.entrada.hide()
        self.login_widget.sinal.show()
        self.login_widget.fft.show()
        self.login_widget.delta.hide()
        self.login_widget.theta.hide()
        self.login_widget.alfa.hide()
        self.login_widget.beta.hide()
        self.login_widget.delta2.show()
        self.login_widget.theta2.hide()
        self.login_widget.alfa2.hide()

    def Theta(self):
        self.login_widget.entrada.hide()
        self.login_widget.sinal.show()
        self.login_widget.fft.show()
        self.login_widget.delta.hide()
        self.login_widget.theta.hide()
        self.login_widget.alfa.hide()
        self.login_widget.beta.hide()
        self.login_widget.delta2.hide()
        self.login_widget.theta2.show()
        self.login_widget.alfa2.hide()

    def Alfa(self):
        self.login_widget.entrada.hide()
        self.login_widget.sinal.show()
        self.login_widget.fft.show()
        self.login_widget.delta.hide()
        self.login_widget.theta.hide()
        self.login_widget.alfa.hide()
        self.login_widget.beta.hide()
        self.login_widget.delta2.hide()
        self.login_widget.theta2.hide()
        self.login_widget.alfa2.show()

    def Beta(self):
        self.login_widget.entrada.hide()
        self.login_widget.sinal.show()
        self.login_widget.fft.show()
        self.login_widget.delta.hide()
        self.login_widget.theta.hide()
        self.login_widget.alfa.hide()
        self.login_widget.beta.show()
        self.login_widget.delta2.hide()
        self.login_widget.theta2.hide()
        self.login_widget.alfa2.hide()

    def Pause(self):
        if self.stop == 1:
            self.stop = 0
        else:
            self.stop = 1

    def plotter(self):
        if self.started == 0:
            self.started = 1
            self.firstTime = time()
            self.lastTime = time()
            self.testTime = time()

            self.data = [0]
            self.curve = self.login_widget.sinal.getPlotItem().plot(pen='y')
            self.curve2 = self.login_widget.entrada.getPlotItem().plot(pen='y')
            self.curvefft = self.login_widget.fft.getPlotItem().plot(pen='r')
            self.curveD = self.login_widget.delta.getPlotItem().plot(pen='g')
            self.curveT = self.login_widget.theta.getPlotItem().plot(pen={'color':(139,0,139)})
            self.curveA = self.login_widget.alfa.getPlotItem().plot(pen='w')
            self.curveB = self.login_widget.beta.getPlotItem().plot(pen='b')
            self.curveD2 = self.login_widget.delta2.getPlotItem().plot(pen='g')
            self.curveT2 = self.login_widget.theta2.getPlotItem().plot(pen={'color':(139,0,139)})
            self.curveA2 = self.login_widget.alfa2.getPlotItem().plot(pen='w')
            self.Entrada()

            self.timer = QtCore.QTimer()
            self.timer.timeout.connect(self.updater)
            self.timer.start(0)
        else:
            pass

    def updater(self):
        self.now = time()
        self.dt = self.now - self.lastTime
        self.lastTime = self.now
        if self.fps is None:
            self.fps = 1.0/self.dt
        else:
            self.s = np.clip(self.dt*3., 0, 1)
            self.fps = self.fps * (1-self.s) + (1.0/self.dt) * self.s
        self.login_widget.fps.setText('Velocidade de Leitura: {fps:.3f} FPS'.format(fps=self.fps))
        # ----------------------------------------------- #

        # ------------ EIXO Y ------------- #
        self.Ym[:-1] = self.Ym[1:]
        
        self.idx = 0                                                 # > Variável do index da matriz.
        self.conversao = 0                                           # > Variável para salvar conversão.
        for p in self.pinos:                                         # > Passa por todos os pinos enquanto,
            self.leituras[self.idx] = GPIO.input(p)                       # salva seus valores na matriz.
            self.conversao = self.conversao + (self.leituras[self.idx]*(2**self.idx))    # > Converte de binário para decimal
            self.idx += 1                                            #


        self.valorLido = self.conversao
        self.rawsignal = self.conversao
        self.Ym[-1] = float(self.rawsignal)
        # --------------------------------- #

        # -------------- FFT -------------- #
        self.fft = scipy.fft(self.Ym)
        self.bpD = list(self.fft)
        self.bpT = list(self.fft)
        self.bpA = list(self.fft)
        self.bpB = list(self.fft)

        for i in range(len(self.bpD)): # (H-red)
            if i>self.cutOffD:
                self.bpD[i]=0
        self.ibpD=scipy.ifft(self.bpD)

        for i in range(len(self.bpT)): # (H-red)
            if i>self.cutOffT or i <= self.cutOffD:
                self.bpT[i]=0
        self.ibpT=scipy.ifft(self.bpT)

        for i in range(len(self.bpA)): # (H-red)
            if i>self.cutOffA or i <= self.cutOffT:
                self.bpA[i]=0
        self.ibpA=scipy.ifft(self.bpA)

        for i in range(len(self.bpB)): # (H-red)
            if i>self.cutOffB or i <= self.cutOffA:
                self.bpB[i]=0
        self.ibpB=scipy.ifft(self.bpB)

        self.f = np.fft.fft(self.Ym) / len(self.Ym)
        self.yf = abs(self.f[1:len(self.f)/2])
        self.dt = self.Xm[-1] - self.Xm[0]
        self.xf = np.linspace(0, 0.5*len(self.Xm)/self.dt, len(self.yf))
        # --------------------------------- #

        # ------------ EIXO X ------------- #
        self.Xm[:-1] = self.Xm[1:]
        self.value = self.now-self.firstTime
        self.Xm[-1] = float(self.value)
        # --------------------------------- #

        # ------------------- PLOTAGEM ------------------- #
        if self.stop == 0:
            if (time() - self.testTime) >= 0.95:
                self.testTime = time()
                self.curve.setData(y=self.Ym, x=self.Xm)
                self.curve2.setData(y=self.Ym, x=self.Xm)
                self.curvefft.setData(y=self.yf, x=self.xf)
                self.curveD.setData(y=self.ibpD.real, x=self.Xm)
                self.curveT.setData(y=self.ibpT.real, x=self.Xm)
                self.curveA.setData(y=self.ibpA.real, x=self.Xm)
                self.curveB.setData(y=self.ibpB.real, x=self.Xm)
                self.curveD2.setData(y=self.ibpD.real, x=self.Xm)
                self.curveT2.setData(y=self.ibpT.real, x=self.Xm)
                self.curveA2.setData(y=self.ibpA.real, x=self.Xm)
            # else:
            #     pass
        else:
            pass
        # ------------------------------------------------ #

class LoginWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super(LoginWidget, self).__init__(parent)

        layout = QtGui.QGridLayout() # 20x20
        layout.setSpacing(0)

        vbox = QtGui.QVBoxLayout()
        vbox.addStretch(0)

        vbox2 = QtGui.QVBoxLayout()
        vbox2.addStretch(0)

        vbox3 = QtGui.QVBoxLayout()
        vbox3.addStretch(0)

        grid = QtGui.QGridLayout()
        grid.setSpacing(0)

        self.start = QtGui.QPushButton('Iniciar')
        self.button = QtGui.QPushButton('Visão Geral'.decode('utf-8'))
        self.button1 = QtGui.QPushButton('Sinal de Entrada')
        self.button2 = QtGui.QPushButton('Ondas Beta')
        self.button3 = QtGui.QPushButton('Ondas Alpha')
        self.button4 = QtGui.QPushButton('Ondas Theta')
        self.button5 = QtGui.QPushButton('Ondas Delta')
        self.button6 = QtGui.QPushButton('Parar/Continuar')
        self.button7 = QtGui.QPushButton('Sair')

        self.text = QtGui.QLabel()
        self.text.setText('Sistema de Análise de Sinais Neurais'.decode('utf-8'))
        self.text.setStyleSheet("color: #2c3e50; font-weight: bold; font-size: 50px; font-family: Impact")

        self.logo = QtGui.QLabel()
        self.logo.setPixmap(QtGui.QPixmap("brainIcon.png").scaledToWidth(90))
        self.logo.setStyleSheet("margin:none")

        self.entrada = pg.PlotWidget(title="Sinal de Entrada")
        self.entrada.getPlotItem().setLabel('bottom', 'Tempo', units='s')
        self.sinal = pg.PlotWidget(title="Sinal de Entrada")
        self.sinal.getPlotItem().setLabel('bottom', 'Tempo', units='s')
        self.fft = pg.PlotWidget(title="FFT")
        self.fft.getPlotItem().setLabel('bottom', 'Frequência', units='Hz')
        self.delta = pg.PlotWidget(title="Onda Delta")
        self.delta.getPlotItem().setLabel('bottom', 'Tempo', units='s')
        self.theta = pg.PlotWidget(title="Onda Theta")
        self.theta.getPlotItem().setLabel('bottom', 'Tempo', units='s')
        self.alfa = pg.PlotWidget(title="Onda Alpha")
        self.alfa.getPlotItem().setLabel('bottom', 'Tempo', units='s')
        self.beta = pg.PlotWidget(title="Onda Beta")
        self.beta.getPlotItem().setLabel('bottom', 'Tempo', units='s')
        self.delta2 = pg.PlotWidget(title="Onda Delta")
        self.delta2.getPlotItem().setLabel('bottom', 'Tempo', units='s')
        self.theta2 = pg.PlotWidget(title="Onda Theta")
        self.theta2.getPlotItem().setLabel('bottom', 'Tempo', units='s')
        self.alfa2 = pg.PlotWidget(title="Onda Alpha")
        self.alfa2.getPlotItem().setLabel('bottom', 'Tempo', units='s')

        self.campo1 = QtGui.QLabel('DADOS DO USUÁRIO'.decode('utf-8'))
        self.campo1.setStyleSheet("color: #2c3e50;font-size: 30px; font-family: Impact")
        self.user = QtGui.QLabel('Nome: '.decode('utf-8'))
        self.user.setStyleSheet("font-size: 20px")
        self.age = QtGui.QLabel('Idade: ')
        self.age.setStyleSheet("font-size: 20px")
        self.sex = QtGui.QLabel('Sexo: ')
        self.sex.setStyleSheet("font-size: 20px")
        self.blood = QtGui.QLabel('Tipo Sanguíneo: '.decode('utf-8'))
        self.blood.setStyleSheet("font-size: 20px")

        self.campo2 = QtGui.QLabel('DADOS DO SINAL'.decode('utf-8'))
        self.campo2.setStyleSheet("color: #2c3e50;font-size: 30px; font-family: Impact")
        self.onda = QtGui.QLabel('Onda Ativa: ')
        self.onda.setStyleSheet("font-size: 20px")
        self.estado = QtGui.QLabel('Estado: ')
        self.estado.setStyleSheet("font-size: 20px")
        self.fps = QtGui.QLabel('Velocidade de Leitura: ')
        self.fps.setStyleSheet("font-size: 20px")

        layout.addWidget(self.text,0,0,1,17)

        layout.addWidget(self.logo,0,17,1,3)

        vbox2.addWidget(self.campo1)
        vbox2.addWidget(self.user)
        vbox2.addWidget(self.age)
        vbox2.addWidget(self.sex)
        vbox2.addWidget(self.blood)
        vbox2.setAlignment(QtCore.Qt.AlignTop)

        vbox3.addWidget(self.campo2)
        vbox3.addWidget(self.onda)
        vbox3.addWidget(self.estado)
        vbox3.addWidget(self.fps)
        vbox3.setAlignment(QtCore.Qt.AlignTop)

        grid.addWidget(self.start,0,0,1,2)
        grid.addWidget(self.button,2,0,1,2)
        grid.addWidget(self.button1,1,0,1,2)
        grid.addWidget(self.button5,3,0)
        grid.addWidget(self.button4,3,1)
        grid.addWidget(self.button3,4,0)
        grid.addWidget(self.button2,4,1)
        grid.addWidget(self.button6,5,0)
        grid.addWidget(self.button7,5,1)

        vbox.addLayout(grid)
        layout.addLayout(vbox3,2,0,3,6)
        layout.addLayout(vbox2,0,0,3,6)
        layout.addLayout(vbox,3,0,6,6)

        layout.addWidget(self.entrada,1,6,8,14)
        layout.addWidget(self.sinal,1,6,4,14)
        layout.addWidget(self.fft,5,6,4,7)
        layout.addWidget(self.delta,1,6,4,7)
        layout.addWidget(self.theta,1,13,4,7)
        layout.addWidget(self.alfa,5,6,4,7)
        layout.addWidget(self.beta,5,13,4,7)
        layout.addWidget(self.delta2,5,13,4,7)
        layout.addWidget(self.theta2,5,13,4,7)
        layout.addWidget(self.alfa2,5,13,4,7)

        self.setLayout(layout)

if __name__ == '__main__':
    app = QtGui.QApplication([])
    window = MainWindow()
    window.showFullScreen()
    app.exec_()
