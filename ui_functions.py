# -*- coding: utf-8 -*-
"""
Created on Thu Sep 16 17:17:47 2021

@author: alecf
"""

from principal import *

## CLASSE RESPOSAVEL PELA ANIMACAO DO MENU LATERAL
#######################################################################
class UIFunctions:

    def toggleMenu(self, maxWidth, enable):
        if enable:

            # PARAMETROS PADROES DO FRAME DO MENU
            width = self.interface_ui.frame_8.width()
            maxExtend = maxWidth
            standard = 70

            # PARAMETROS DE EXPANSAO DO MENU LATERAL
            if width == 70:
                widthExtended = maxExtend
            else:
                widthExtended = standard

            # ANIMACAO
            self.animation = QPropertyAnimation(self.editor_ui.frame_8, b"minimumWidth")
            self.animation.setDuration(350)
            self.animation.setStartValue(width)
            self.animation.setEndValue(widthExtended)
            self.animation.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
            self.animation.start()


    
