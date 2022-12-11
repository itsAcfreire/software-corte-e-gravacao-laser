# -*- coding: utf-8 -*-
"""
Created on Mon Aug 29 00:43:43 2022

@author: CAD01
"""

import interface
import os
import pathlib
from ui_functions import *
from svgtogcode import *
from PyQt5.QtCore import (QCoreApplication, QPropertyAnimation, QDate, QDateTime, QMetaObject, QObject, QPoint, QRect, QSize, QTime, QUrl, Qt, QEvent)
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import cv2, imutils
import sys
from PIL import Image
import numpy
from svg_to_gcode.svg_parser import parse_file
from svg_to_gcode.compiler import Compiler, interfaces
from svg_to_gcode.formulas import linear_map


## CLASSE CONTROLADORA
########################################################################

class Controller:
    def __init__(self):
        ## CONFIGURAÇÃO DE TELA
        # Tela 1 - Principal
        self.interface_Window = QtWidgets.QMainWindow()
        self.interface_ui = interface.Ui_MainWindow()
        self.interface_ui.setupUi(self.interface_Window)
       
        ##CONFIGURAÇÃO DE BOTÕES
        # botões menu lateral
        self.interface_ui.btn_toggle.clicked.connect(lambda: UIFunctions.toggleMenu(self, 180, True)) # Animação
        self.interface_ui.btn_home.clicked.connect(self.show_pagina1)
        self.interface_ui.btn_info.clicked.connect(self.show_pagina2)

        # botões de edição de imagem
        self.interface_ui.load_btn.clicked.connect(self.loadImage)
        self.interface_ui.sharpness_btn.clicked.connect(self.nitz)
        self.interface_ui.invert_btn.clicked.connect(self.inverter)
        self.interface_ui.resize_btn.clicked.connect(lambda: self.resizeImage(self.image, self.height_px, self.width_px))
        self.interface_ui.verticalSlider.valueChanged['int'].connect(self.brightness_value)

        # botões para arquivos de saída
        self.interface_ui.gcode_btn.clicked.connect(self.image2gcode)
        self.interface_ui.save_btn.clicked.connect(self.savePhoto)
        
    ## PÁGINAS TELA PRINCIPAL    
    def show_pagina1(self):
        self.interface_ui.stackedWidget.setCurrentWidget(self.interface_ui.page_1)
        
    def show_pagina2(self):
        self.interface_ui.stackedWidget.setCurrentWidget(self.interface_ui.page_3)
    
    ## FUNÇÃO DE EXIBIÇÃO
    def show_Inicio(self):
        self.interface_Window.show()
    
    ######################################################################################################################################################################
    # FUNÇÕES PRINCIPAIS DO CÓDIGO ########################################################################################################################################
    ######################################################################################################################################################################
    ## CARREGA IMAGEM USUÁRIO
    def loadImage(self):
        self.filename = QFileDialog.getOpenFileName(filter="Image Files (*.png *.jpg *.jpeg)")[0]
        print(self.filename)
        self.image = cv2.imread(self.filename)
        self.interface_ui.verticalSlider.setValue(0)
        self.setPhoto(self.image)

    ## POSICIONA A IMAGEM NA TELA
    def setPhoto(self,image):
        # Posiciona a imagem no widget gráfico
        self.tmp = image
        frame = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = QImage(frame, frame.shape[1],frame.shape[0],frame.strides[0],QImage.Format_RGB888)
        scene = QGraphicsScene()
        a = scene.addPixmap(QtGui.QPixmap.fromImage(image))
        a.setFlag(QGraphicsItem.ItemIsMovable)
        self.interface_ui.graphicsView.setScene(scene)

        # calcula e exibe as dimensões da imagem
        dimensions = self.tmp.shape
        self.height_px = self.tmp.shape[0]
        self.width_px = self.tmp.shape[1]
        h = round(self.height_px*0.2645833333, 2)
        w = round(self.width_px*0.2645833333, 2)
        print('Image Dimension [px]: ',dimensions)
        print('Image Height    [mm]: ',h)
        print('Image Width     [mm]: ',w) 
        self.interface_ui.altura_box.setValue(h)
        self.interface_ui.largura_box.setValue(w)
        
    ## RESIMENCIONAMENTO DA IMAGEM
    def resizeImage(self, image, height, width):
        try:
            height_input = round(self.interface_ui.altura_box.value()* 3.7795275591, None)
            width_input = round(self.interface_ui.largura_box.value()* 3.7795275591, None)
            self.resized = cv2.imread(self.filename)
            if height_input != height and width_input == width:
                new_height = height_input
                self.image = imutils.resize(self.resized, None, new_height)
            elif width_input != width and height_input == height:
                new_width = width_input
                self.image = imutils.resize(self.resized, new_width, None)
            self.interface_ui.verticalSlider.setValue(0)
            self.setPhoto(self.image)
        except:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
          
            # setting message for Message Box
            msg.setText("Por favor, insira uma imagem!")
              
            # setting Message box window title
            msg.setWindowTitle("Aviso!")
              
            # declaring buttons on Message Box
            msg.setStandardButtons(QMessageBox.Ok)
              
            # start the app
            retval = msg.exec_()
    
    ## FUNÇÕES PARA ALTERAR NÍVEL DE PRETO E BRANCO DA IMAGEM (brightness_value, changeBrightness e  update)
    # recebe o valor do slider de preto e branco
    def brightness_value(self,value):
    		""" This function will take value from the slider
    			for the brightness from 0 to 99
    		"""
    		self.brightness_value_now = value
    		print('Brightness: ',value)
    		self.update()

    # recebe o valor da função brightness_value e envia a imagem e valor para função 
    # changeBrightness
    def update(self):
        """ This function will update the photo according to the 
            current values of blur and brightness and set it to photo label.
        """
        
        img_up = self.changeBrightness(self.image,self.brightness_value_now)
        self.setPhoto(img_up)
    
    # altera as cores da imagem para preto e branco. Retornando-a para função update
    def changeBrightness(self,img,value):
            originalImage = img
            grayImage = cv2.cvtColor(originalImage, cv2.COLOR_BGR2GRAY)
            (thresh, blackAndWhiteImage) = cv2.threshold(grayImage, value, 255, cv2.THRESH_BINARY)
            image = imutils.resize(blackAndWhiteImage,width=640)
            frame = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image = QImage(frame, frame.shape[1],frame.shape[0],frame.strides[0],QImage.Format_RGB888)
            return blackAndWhiteImage
    ## 
        
    ## ALTERA A NiTIDEZ DA IMAGEM
    def nitz(self):
        try:
            nitidez = cv2.detailEnhance(self.tmp, sigma_s=10, sigma_r=0.3)
            self.setPhoto(nitidez)
        except:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
          
            # setting message for Message Box
            msg.setText("Por favor, insira uma imagem!")
              
            # setting Message box window title
            msg.setWindowTitle("Aviso!")
              
            # declaring buttons on Message Box
            msg.setStandardButtons(QMessageBox.Ok)
              
            # start the app
            retval = msg.exec_()
            
    ## INVERTE AS CORES DA IMAGEM
    def inverter(self):
        try:
            img_not = cv2.bitwise_not(self.tmp)
            self.setPhoto(img_not)        
            
        except:
           msg = QMessageBox()
           msg.setIcon(QMessageBox.Warning)
         
           # setting message for Message Box
           msg.setText("Por favor, insira uma imagem!")
             
           # setting Message box window title
           msg.setWindowTitle("Aviso!")
             
           # declaring buttons on Message Box
           msg.setStandardButtons(QMessageBox.Ok)
             
           # start the app
           retval = msg.exec_()
    
    ## SALVAR A FOTO INSERIDA NO CANVAS, A FOTO É SALVA COM AS EDIÇÕES (FORMATOS: JPG, PNG, TIFF E BMP)
    def savePhoto(self):
       
        try:
           filename = QFileDialog.getSaveFileName(filter="JPG(*.jpg);;PNG(*.png);;TIFF(*.tiff);;BMP(*.bmp)")[0]
           cv2.imwrite(filename,self.tmp)
           print('Image saved as:',filename)      
            
        except:
           msg = QMessageBox()
           msg.setIcon(QMessageBox.Warning)
         
           # setting message for Message Box
           msg.setText("Por favor, insira uma imagem!")
             
           # setting Message box window title
           msg.setWindowTitle("Aviso!")
             
           # declaring buttons on Message Box
           msg.setStandardButtons(QMessageBox.Ok)
             
           # start the app
           retval = msg.exec_()
                

    ## GERAÇÃO DO CÓDIGO G. IMAGEM DO CANVA É SALVA NO MESMO DIRETÓRIO DO PROGRAMA,
    ## EXECUTA COMMAND LINES NO PROMPT DE COMANDO PARA UTILIZAR AS FERRAMENTAS
    ## IMAGE MAGICK E POTRACE, PARA TRANSFORMAR A IMAGEM EM SVG. DEPOIS UTILIZA A BIBLIOTECA
    ## SVG_TO_GCODE PARA CRIAR O CÓDIGO DE OPERAÇÃO
    def image2gcode(self):
        # try:
            cv2.imwrite('imagem.png',self.tmp)
            
            h = str(round(self.height_px*0.2645833333, 2))
            
            os.system ("magick convert imagem.png imagem.pgm")
            
            cmd = print("potrace imagem.pgm -s -H "+h+"pt -o imagem.svg")
            os.system("potrace imagem.pgm -s -H "+h+"pt -o imagem.svg")
            
            moviment_speed = self.interface_ui.vel_deslocamento.value()
            cutting_speed = self.interface_ui.vel_laser.value()
            
            gcode_compiler = Compiler(CustomInterface, moviment_speed, cutting_speed, pass_depth=5)
            curves = parse_file('imagem.svg')
            gcode_compiler.append_curves(curves) 
            gcode_file = QFileDialog.getSaveFileName(filter="gcode(*.gcode)")[0]
            gcode_compiler.compile_to_file(gcode_file)
            
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
          
            # setting message for Message Box
            msg.setText("G-code criado com sucesso!")
              
            # setting Message box window title
            msg.setWindowTitle("Sucesso!")
              
            # declaring buttons on Message Box
            msg.setStandardButtons(QMessageBox.Ok)
              
            # start the app
            retval = msg.exec_()
        # except:
        #     msg = QMessageBox()
        #     msg.setIcon(QMessageBox.Warning)
          
        #     # setting message for Message Box
        #     msg.setText("Por favor, insira uma imagem!")
              
        #     # setting Message box window title
        #     msg.setWindowTitle("Aviso!")
              
        #     # declaring buttons on Message Box
        #     msg.setStandardButtons(QMessageBox.Ok)
              
        #     # start the app
        #     retval = msg.exec_()
    
    
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    controller = Controller()
    controller.show_Inicio()
    sys.exit(app.exec_())
    
    
