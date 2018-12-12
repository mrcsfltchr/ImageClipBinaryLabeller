#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 11 14:26:21 2018

@author: MarcusF
"""

from qtpy import QtWidgets, QtGui, QtCore
from qtpy.QtCore import Qt, QPoint
from PyQt5.QtCore import pyqtSignal
import tifffile as tf
import numpy as np
import qimage2ndarray as qnd
import sys


class LabellerMW(QtWidgets.QMainWindow):
    
    def __init__(self):
        
        super().__init__()
        
        self.content = Labeller()
    
        self.setCentralWidget(self.content)
        
        self.show()
        
        
        
        
class Labeller(QtWidgets.QWidget):
    
    #GUI which allows the user to flick through randomly sampled images and assign a label of Vesicle or No vesicle 
    success = pyqtSignal()
    def __init__(self):
        
        super().__init__()
        
        
        layout = QtWidgets.QGridLayout()
        
        self.imageview = Label()
        
        self.image_nav = ImageNavigation()
        
        self.label_select = LabelSelector()
        
        self.loadsavecontrol = LoadSave()
        

        self.index = 0
        
        self.ImageHandler = ImageCollection()
        
        
        self.loadsavecontrol.load_btn.clicked.connect(self.load_images)
        
        layout.addWidget(self.loadsavecontrol,0,0)
        layout.addWidget(self.label_select,1,0)
        layout.addWidget(self.imageview,0,1)
        layout.addWidget(self.image_nav,1,1)
        
        self.setLayout(layout)
        
        
    
    def check_index(self):
        
        if self.index == self.ImageHandler.imagecollection.shape[0]:
            save_prompt = QtWidgets.QMessageBox()
            save_prompt.setText('You have reached the end of the image collection, please save the class labels')
            save_prompt.exec_()
            return True
        else:
            return False
        
    def assign_class_label_vesicle(self):
        

        if self.check_index():
            return
        
        self.ImageHandler.class_labels[self.index] = 1
        
    def assign_class_label_not_vesicle(self):
        
        if self.check_index():
            return
        
        self.ImageHandler.class_labels[self.index] =0
        
        
    def increment_image_by_one(self):
        
        self.index +=1
        self.label_select.set_activeframe(self.ImageHandler.imagecollection[self.index])
        
        
    def decrement_image_by_one(self):
        
        self.index -=1
        self.label_select.set_activeframe(self.ImageHandler.imagecollection[self.index])

        
    def load_images(self):
        
        ret, images = self.loadsavecontrol.load()
        if ret == -1:
            return 
        else:
            
            self.ImageHandler.set_imagecollection(images)
            
            self.image_nav.next.clicked.connect(self.increment_image_by_one)
            self.image_nav.previous.clicked.connect(self.decrement_image_by_one)
            
        
    def raise_invalid_file_error(self):
        
        warning_box = QtWidgets.QMessageBox()
        warning_box.setText('Load attempt failed. File must have extension ".npy".')
        warning_box.exec_()
        
        
class ImageCollection():

    imagesloaded = pyqtSignal()
    
    def __init__(self):
        
        #need to upload an compressed numpy ndarray which should have shape of the form NumImages x width x height
        
        self.imagecollection = None
            
        

    def set_imagecollection(self,images):
        
        self.imagecollection = images
            
        #construct array to house labels. This is the same size as the number of images.
        
        self.class_labels = np.zeros((self.image_collection.shape[0],))
        #input into neural network will be numpy arrays Xdata (image clips) and ydata (labels)
        

        self.count = self.image_collection.shape[0]
        
    def unlabelled_images_left(self):
        
        self.count -= 1
        
class Label(QtWidgets.QLabel):
    
    #class which draws a numpy array into a QLabel by first converting it into the QPixmap object via an external package
    
    def __init__(self, parent=None):
        super(Label, self).__init__(parent=parent)
        self.activeframe = None
        self.maxintens = None
        self.h = None
        self.w = None
        self.size = None
        self.pixsize = None
        
        
        
    def set_activeframe(self,frame):
        
        warning_box = QtWidgets.QMessageBox()
        try:
            assert len(self.frame.shape) ==2
        except AssertionError:
            warning_box.setText('Invalid frame selected')
            warning_box.exec_()
            
            
        self.activeframe = frame
        self.h = frame.shape[0]
        self.w = frame.shape[1]
        
        self.maxintens = np.ax(self.activeframe)
        
        self.update()
        
        
    def paintEvent(self, e):
        super().paintEvent(e)
        qp = QtGui.QPainter(self)
        
        if self.activeframe is not None:
            img = qnd.gray2qimage(self.activeframe,normalize = (0,self.maxintens))
            self.size = img.size()
            pix = QtGui.QPixmap.fromImage(img).scaled(self.h,self.w,Qt.KeepAspectRatio)
            self.pixsize = pix.size()
            
            
            pos = QtCore.QPoint(0,0)        
            qp.drawPixmap(pos,pix) 
            
        else:
            pos = QtCore.QPoint(0.5,0.5)
            qp.drawText(pos,"Load Video to Display")
        
        
class ImageNavigation(QtWidgets.QWidget):
    
    
    def __init__(self):
        super().__init__()
        layout = QtWidgets.QHBoxLayout()
        self.previous = QtWidgets.QPushButton('Previous')
        self.next = QtWidgets.QPushButton('Next')
        
        layout.addWidget(self.previous)
        layout.addWidget(self.next)
        
        self.setLayout(layout)
        
        
        
class LabelSelector(QtWidgets.QWidget):
    
    def __init__(self):
        
        super().__init__()
        layout = QtWidgets.QVBoxLayout()
        
        self.vesicle = QtWidgets.QPushButton('Vesicle')
        self.vesicle.setSizePolicy(QtWidgets.QSizePolicy.Minimum,QtWidgets.QSizePolicy.Minimum)
        self.vesicle.setMinimumSize(100,100)
        self.novesicle = QtWidgets.QPushButton('NOT Vesicle')
        self.novesicle.setSizePolicy(QtWidgets.QSizePolicy.Minimum,QtWidgets.QSizePolicy.Minimum)
        self.novesicle.setMinimumSize(100,100)
        layout.addWidget(self.vesicle)
        layout.addWidget(self.novesicle)
        
        self.setLayout(layout)
        
        
        
class LoadSave(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()        
        layout = QtWidgets.QGridLayout()
        
        self.loadinput = QtWidgets.QLineEdit('Input image collection path "XXX.npy"')
        self.load_btn = QtWidgets.QPushButton('Load')
        
        self.saveinput = QtWidgets.QLineEdit('Input saving path for labels')
        
        self.save_btn = QtWidgets.QPushButton('Save')
        
        layout.addWidget(self.loadinput,0,0)
        layout.addWidget(self.load_btn,1,0)
        layout.addWidget(self.saveinput,0,1)
        layout.addWidget(self.save_btn,1,1)
        
        self.setLayout(layout)
        
        
    def load(self):
        if '.npy' == self.loadinput.text()[-4:]:
            
            return 1,np.load(self.loadinput.text())
    
        else:
            warning = QtWidgets.QMessageBox()
            warning.setText('Make sure file path has file type ".npy"')
            warning.exec_()
            return -1,None
    
    def save(self,class_labels):
        
        warning = QtWidgets.QMessageBox()
        try:
            np.save(self.saveinput.text(),class_labels)
        except:
            warning.setText('Save failed')
            warning.exec_()
            
            
            
            
if __name__ == '__main__':
    
    app = QtWidgets.QApplication(sys.argv)
      
    LabellingTool = LabellerMW()
    app.exec_()      
        
