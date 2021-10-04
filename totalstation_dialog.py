# -*- coding: utf-8 -*-
"""
/***************************************************************************
 TotalopenstationDialog
                                 A QGIS plugin
 Total Open Station (TOPS for friends) is a free software program for downloading and processing data from total station devices.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2021-09-01
        git sha              : $Format:%H$
        copyright            : (C) 2021 by Enzo Cocca adArte srl; Stefano Costa
        email                : enzo.ccc@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import io
import os
import time, sys
import tqdm
from tqdm import tqdm
from time import sleep
from datetime import date
import threading
import subprocess
import platform
import csv
import tempfile
from qgis.PyQt import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtCore import  *
from qgis.PyQt.QtWidgets import QVBoxLayout, QApplication, QDialog, QMessageBox, QFileDialog,QLineEdit,QWidget,QCheckBox,QProgressBar,QInputDialog
from qgis.PyQt.QtSql import *
from qgis.PyQt.uic import loadUiType
from qgis.PyQt import  QtWidgets 
from qgis.core import  *
from qgis.gui import  *
from qgis.utils import iface
from numpy import interp
import processing
# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'totalstation_dialog_base.ui'))


class TotalopenstationDialog(QtWidgets.QDialog, FORM_CLASS):
    
    
    def __init__(self, parent=None):
        """Constructor."""
        super(TotalopenstationDialog, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.model = QtGui.QStandardItemModel(self)
        self.tableView.setModel(self.model)
        self.toolButton_input.clicked.connect(self.setPathinput)
        self.toolButton_output.clicked.connect(self.setPathoutput)
        self.toolButton_save_raw.clicked.connect(self.setPathsaveraw)
        self.mDockWidget.setHidden(True)
        self.comboBox_model.currentIndexChanged.connect(self.tt)
        self.lineEdit_save_raw.textChanged.connect(self.connect)
        self.pushButton_connect.setEnabled(False)
    

    def connect(self):
        
        
        if str(self.lineEdit_save_raw.text()):
            
            self.pushButton_connect.setEnabled(True)
        
        else:
            self.pushButton_connect.setEnabled(False)
    

    def tt(self):    
        if self.comboBox_model.currentIndex()!=6:
            
            self.mDockWidget.setHidden(True)
        else:
            
            self.mDockWidget.show()
        
    def setPathinput(self):
        s = QgsSettings()
        input_ = QFileDialog.getOpenFileName(
            self,
            "Set file name",
            '',
            "(*.*)"
        )[0]
        #filename=dbpath.split("/")[-1]
        if input_:

            self.lineEdit_input.setText(input_)
            s.setValue('',input_)
            
    def setPathoutput(self):
        s = QgsSettings()
        output_ = QFileDialog.getSaveFileName(
            self,
            "Set file name",
            '',
            "(*.{})".format(self.comboBox_format2.currentText())
        )[0]
        #filename=dbpath.split("/")[-1]
        if output_:

            self.lineEdit_output.setText(output_)
            s.setValue('',output_)
            
    def setPathsaveraw(self):
        s = QgsSettings()
        output_ = QFileDialog.getSaveFileName(
            self,
            "Set file name",
            '',
            "(*.tops)"
        )[0]
        #filename=dbpath.split("/")[-1]
        if output_:

            self.lineEdit_save_raw.setText(output_)
            s.setValue('',output_)
    
    def loadCsv(self, fileName):
        self.tableView.clearSpans()
        
        with open(fileName, "r") as fileInput:
            for row in csv.reader(fileInput):    
                
                items = [
                    QtGui.QStandardItem(field)
                    for field in row
                ]
                self.model.appendRow(items)
                
               
                
    def delete(self):
        if self.tableView.selectionModel().hasSelection():
            indexes =[QPersistentModelIndex(index) for index in self.tableView.selectionModel().selectedRows()]
            for index in indexes:
                #print('Deleting row %d...' % index.row())
                self.model.removeRow(index.row())
    

    
    def on_pushButton_export_pressed(self):
        
        self.delete()
        if platform.system() == "Windows":
            b=QgsApplication.qgisSettingsDirPath().replace("/","\\")
                
                
            cmd = os.path.join(os.sep, b, 'python', 'plugins', 'totalopenstationToQgis', 'scripts', 'totalopenstation-cli-parser.py')
            cmd2= ' -i '+str(self.lineEdit_input.text())+' '+'-o '+str(self.lineEdit_output.text())+' '+'-f'+' '+self.comboBox_format.currentText()+' '+'-t'+' '+self.comboBox_format2.currentText()+' '+'--overwrite'
            try:#os.system("start cmd /k" + ' python ' +cmd+' '+cmd2)
                p=subprocess.check_call(['python',cmd, '-i',str(self.lineEdit_input.text()),'-o',str(self.lineEdit_output.text()),'-f',self.comboBox_format.currentText(),'-t',self.comboBox_format2.currentText(),'--overwrite'], shell=True)
                
            
                
                   
                if self.comboBox_format2.currentIndex()== 0:
                    
                    layer = QgsVectorLayer(str(self.lineEdit_output.text()), 'totalopenstation', 'ogr')
                    
                    layer.isValid() 

                    QgsProject.instance().addMapLayer(layer)

                    QMessageBox.warning(self, 'Total Open Station luncher',
                                              'data loaded into panel Layer', QMessageBox.Ok)
                
                    self.progressBar.reset()
                    temp=tempfile.mkstemp(suffix = '.csv')
                    QgsVectorFileWriter.writeAsVectorFormat(layer, 'test.csv', "utf-8", driverName = "CSV")
                    
                    self.loadCsv('test.csv')
                elif self.comboBox_format2.currentIndex()== 1:
                    
                    layer = QgsVectorLayer(str(self.lineEdit_output.text()), 'totalopenstation', 'ogr')
                    
                    layer.isValid() 

                    
                    QgsProject.instance().addMapLayer(layer)

                    QMessageBox.warning(self, 'Total Open Station luncher',
                                              'data loaded into panel Layer', QMessageBox.Ok)
                    self.progressBar.reset()                          
                    temp=tempfile.mkstemp(suffix = '.csv')
                    QgsVectorFileWriter.writeAsVectorFormat(layer, 'test.csv', "utf-8", driverName = "CSV")
                    self.loadCsv('test.csv')                     
                
                elif self.comboBox_format2.currentIndex()== 2:
                    uri = "file:///"+str(self.lineEdit_output.text())+"?type=csv&xField=x&yField=y&spatialIndex=no&subsetIndex=no&watchFile=no"
                    layer = QgsVectorLayer(uri, "totalopenstation Pyarchinit Quote", "delimitedtext")
                    
                    layer.isValid() 

                    
                    QgsProject.instance().addMapLayer(layer)

                    QMessageBox.warning(self, 'Total Open Station',
                                              'data loaded into panel Layer', QMessageBox.Ok)
                

                    self.loadCsv(str(self.lineEdit_output.text()))
                    
                    ##copy anpast from totalstation to pyarchinit###############
                    sourceLYR = QgsProject.instance().mapLayersByName('totalopenstation Pyarchinit Quote')[0]
                    destLYR = QgsProject.instance().mapLayersByName('Quote US disegno')[0]
                    #Dialog Box for input "ID del Predio" to select it...
                    ID_Sito = QInputDialog.getText(None, 'Sito', 'Input Nome del sito archeologico')
                    Sito = str(ID_Sito [0])
                    ID_Disegnatore = QInputDialog.getText(None, 'Disegnatore', 'Input Nome del Disegnatore')
                    Disegnatore = str(ID_Disegnatore [0])
                    features = []
                    for feature in sourceLYR.getFeatures():
                        features.append(feature)
                        feature.setAttribute('sito_q', Sito)
                        feature.setAttribute('area_q', '1')
                        feature.setAttribute('x', str(date.today().isoformat()))
                        feature.setAttribute('y', Disegnatore)
                        #i += 1
                        sourceLYR.updateFeature(feature)
                    destLYR.startEditing()
                    data_provider = destLYR.dataProvider()
                    data_provider.addFeatures(features)
                    iface.mapCanvas().zoomToSelected()
                    destLYR.commitChanges()
                    # params = {'SOURCE_LAYER': sourceLYR, 
                              # 'TARGET_LAYER': destLYR,
                              # 'ACTION_ON_DUPLICATE' : 1}  # 0: Just append all features

                    # processing.run("etl_load:appendfeaturestolayer", params)
                    
                    QgsProject.instance().removeMapLayer(sourceLYR)
                    ###########finish############################################
                elif self.comboBox_format2.currentIndex()== 3:
                    uri = "file:///"+str(self.lineEdit_output.text())+"?type=csv&xField=x&yField=y&spatialIndex=no&subsetIndex=no&watchFile=no"
                    layer1 = QgsVectorLayer(uri, 'totalopenstation', "delimitedtext")
                    
                    #layer.isValid() 

                    
                    QgsProject.instance().addMapLayer(layer1)

                    QMessageBox.warning(self, 'Total Open Station',
                                              'data loaded into panel Layer', QMessageBox.Ok)
                

                    self.loadCsv(str(self.lineEdit_output.text()))
                
                

                
                else:
                    
                    pass
        
            except Exception as e:
                
                QMessageBox.warning(self, 'Total Open Station',
                                          "Error:\n"+str(e), QMessageBox.Ok)
        else:
            try:
                b=QgsApplication.qgisSettingsDirPath()
                cmd = os.path.join(os.sep, b, 'python', 'plugins', 'totalopenstationToQgis', 'scripts', 'totalopenstation-cli-parser.py')
                cmd2= ' -i '+str(self.lineEdit_input.text())+' '+'-o '+str(self.lineEdit_output.text())+' '+'-f'+' '+self.comboBox_format.currentText()+' '+'-t'+' '+self.comboBox_format2.currentText()+' '+'--overwrite'
                #os.system("start cmd /k" + ' python ' +cmd+' '+cmd2)
                subprocess.check_call(['python',cmd, '-i',str(self.lineEdit_input.text()),'-o',str(self.lineEdit_output.text()),'-f',self.comboBox_format.currentText(),'-t',self.comboBox_format2.currentText(),'--overwrite'], shell=True)
                
                #Load the layer if the format is geojson or dxf or csv           
                if self.comboBox_format2.currentIndex()== 0:
                    
                    layer = QgsVectorLayer(str(self.lineEdit_output.text()), 'totalopenstation', 'ogr')
                    
                    layer.isValid() 

                    QgsProject.instance().addMapLayer(layer)

                    QMessageBox.warning(self, 'Total Open Station',
                                              'data loaded into panel Layer', QMessageBox.Ok)
                
                
                    r=open(str(self.lineEdit_output.text()),'r')
                    lines = r.read().split(',')
                    self.textEdit.setText(str(lines))
                elif self.comboBox_format2.currentIndex()== 1:
                    
                    layer = QgsVectorLayer(str(self.lineEdit_output.text()), 'totalopenstation', 'ogr')
                    
                    layer.isValid() 

                    
                    QgsProject.instance().addMapLayer(layer)

                    QMessageBox.warning(self, 'Total Open Station',
                                              'data loaded into panel Layer', QMessageBox.Ok)
                                              
                    r=open(str(self.lineEdit_output.text()),'r')
                    lines = r.read().split(',')
                    self.textEdit.setText(str(lines))                          
                
                
                    
                
                    
                    
                elif self.comboBox_format2.currentIndex()== 2:
                    uri = "file:///"+str(self.lineEdit_output.text())+"?type=csv&xField=x&yField=y&spatialIndex=no&subsetIndex=no&watchFile=no"
                    layer = QgsVectorLayer(uri, layer.name(), "delimitedtext")
                    
                    layer.isValid() 

                    
                    QgsProject.instance().addMapLayer(layer)

                    QMessageBox.warning(self, 'Total Open Station',
                                              'data loaded into panel Layer', QMessageBox.Ok)
                

                    self.loadCsv(str(self.lineEdit_output.text()))
                
                elif self.comboBox_format2.currentIndex()== 3:
                    uri = "file:///"+str(self.lineEdit_output.text())+"?type=csv&xField=x&yField=y&spatialIndex=no&subsetIndex=no&watchFile=no"
                    layer1 = QgsVectorLayer(uri, 'totalopenstation', "delimitedtext")
                    
                    #layer.isValid() 

                    
                    QgsProject.instance().addMapLayer(layer1)

                    QMessageBox.warning(self, 'Total Open Station',
                                              'data loaded into panel Layer', QMessageBox.Ok)
                

                    self.loadCsv(str(self.lineEdit_output.text()))
                
                
                else:
                    pass
    
    
            except Exception as e:
                
                QMessageBox.warning(self, 'Total Open Station',
                                          "Error:\n"+str(e), QMessageBox.Ok)
    
    def rmvLyr(lyrname):
        qinst = QgsProject.instance()
        qinst.removeMapLayer(qinst.mapLayersByName(lyrname)[0].id())
    def on_pushButton_connect_pressed(self):
        self.textEdit.clear()
            
        if platform.system() == "Windows":
            b=QgsApplication.qgisSettingsDirPath().replace("/","\\")
            cmd = os.path.join(os.sep, b , 'python', 'plugins', 'totalopenstationToQgis', 'scripts', 'totalopenstation-cli-connector.py')
            
            try:
                c=subprocess.check_call(['python', cmd,'-m',self.comboBox_model.currentText(),'-p',self.comboBox_port.currentText(),'-o',str(self.lineEdit_save_raw.text())], shell=True)
                
                
                
            except Exception as e:
                if self.comboBox_port.currentText()=='':
                    self.textEdit.appendPlainText('Insert port please!')
                
                self.textEdit.appendPlainText('Connection falied!')   
                
            else:
                self.textEdit.appendPlainText('Connection OK.................!\n\n')
                self.textEdit.appendPlainText('Start dowload data.................!\n\n')
                s = io.StringIO()
                for i in tqdm(range(3), file=s):    
                    sleep(.1)
                self.textEdit.appendPlainText(s.getvalue())
                
                self.textEdit.appendPlainText('Dowload finished.................!\n\n')
                self.textEdit.appendPlainText('Result:\n')
                r=open(str(self.lineEdit_save_raw.text()),'r')
                lines = r.read().split(',')
                self.textEdit.appendPlainText(str(lines))
            
        else:
            b=QgsApplication.qgisSettingsDirPath()
            cmd = os.path.join(os.sep, b , 'python', 'plugins', 'totalopenstationToQgis', 'scripts', 'totalopenstation-cli-connector.py')
            #os.system("start cmd /k" + ' python ' +cmd)
            try:
                c=subprocess.check_call(['python', cmd,'-m',self.comboBox_model.currentText(),'-p',self.comboBox_port.currentText(),'-o',str(self.lineEdit_save_raw.text())], shell=True)
                
                
                
            except Exception as e:
                if self.comboBox_port.currentText()=='':
                    self.textEdit.appendPlainText('Insert port please!')
                
                self.textEdit.appendPlainText('Connection falied!')   
                
            else:
                self.textEdit.appendPlainText('Connection OK.................!\n\n\n')
                self.textEdit.appendPlainText('Start dowload data.................!\n\n\n')
                s = io.StringIO()
                for i in tqdm(range(3), file=s):    
                    sleep(.1)
                self.textEdit.appendPlainTextPlainText(s.getvalue())
                
                self.textEdit.appendPlainText('Dowload finished.................!\n\n\n')
                self.textEdit.appendPlainText('Result:\n')
                r=open(str(self.lineEdit_save_raw.text()),'r')
                lines = r.read().split(',')
                self.textEdit.appendPlainText(str(lines))
        
