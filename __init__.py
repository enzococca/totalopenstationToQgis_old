# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Totalopenstation
                                 A QGIS plugin
 Total Open Station (TOPS for friends) is a free software program for downloading and processing data from total station devices.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2021-09-01
        copyright            : (C) 2021 by Enzo Cocca adArte srl; Stefano Costa
        email                : enzo.ccc@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
import os
import re
import subprocess
import sys
import traceback
import platform
from qgis.core import QgsMessageLog, Qgis, QgsSettings
L=QgsSettings().value("locale/userLocale")[0:2]
missing_libraries = []
try:
    
    import pkg_resources

    pkg_resources.require("totalopenstation==0.5.2.1_dev_enzo")
    

except Exception as e:
    missing_libraries.append(str(e))
try:
    
    import tqdm

except Exception as e:
    missing_libraries.append(str(e))
install_libraries = []
for l in missing_libraries:
    p = re.findall(r"'(.*?)'", l)
    install_libraries.append(p[0])

if install_libraries:
    from qgis.PyQt.QtWidgets import QMessageBox
    if L=='it':
        res = QMessageBox.warning(None, 'Total Open Station ',
                              "Se vedi questo messaggio significa che il pacchetto totalopenstation deve essere installato\aggiornato\n\n"
                              "alla versione modificata. clicca ok per installare", QMessageBox.Ok | QMessageBox.Cancel)
    
    else:
        res = QMessageBox.warning(None, 'Total Open Station ',
                              "If you see this message it means the required package totalopenstation is missing from your machine:\n\n"
                              "Do you want install the missing package? Remember you need start QGIS like Admin", QMessageBox.Ok | QMessageBox.Cancel)
    if res == QMessageBox.Ok:
        

        python_path = sys.exec_prefix
        python_version = sys.version[:3]
        if platform.system()=='Windows':
            cmd = '{}\python'.format(python_path)
        else:
            cmd = '{}/bin/python{}'.format(python_path, python_version)
        try:
            subprocess.call(
                [cmd, '{}'.format(os.path.join(os.path.dirname(__file__), 'scripts', 'modules_installer.py')),
                 ','.join(install_libraries)], shell=True if platform.system()=='Windows' else False)
        except Exception as e:
            if platform.system()=='Darwin':
                library_path = '/Library/Frameworks/Python.framework/Versions/{}/bin'.format(python_version)
                cmd = '{}/python{}'.format(library_path, python_version)
                subprocess.call(
                    [cmd, '{}'.format(os.path.join(os.path.dirname(__file__), 'scripts', 'modules_installer.py')),
                     ','.join(install_libraries)])
            else:
                error = traceback.format_exc()
                QgsMessageLog.logMessage(error, tag="TotalOpenStation", level=Qgis.Critical)
    else:
        pass

def classFactory(iface):  # pylint: disable=invalid-name
    """Load Totalopenstation class from file Totalopenstation.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .totalstation import Totalopenstation
    return Totalopenstation(iface)
