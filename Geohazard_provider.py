# -*- coding: utf-8 -*-

"""
/***************************************************************************
 Geohazard
                                 A QGIS plugin
 Plugin with various tools for landslide analysis and management
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2024-11-29
        copyright            : (C) 2024 by Campus S., Castelli M., Fasciano C., Filipello A.
        email                : andrea.filipello@arpa.piemonte.it
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

__author__ = 'Campus S., Castelli M., Fasciano C., Filipello A.'
__date__ = '2024-11-29'
__copyright__ = '(C) 2024 by Campus S., Castelli M., Fasciano C., Filipello A.'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from qgis.core import QgsProcessingProvider
from PyQt5.QtGui import QIcon, QPixmap
from .Cindex_algorithm import GroundmotionCIndex
from .Shalstab_algorithm import LandslideShalstab
from .Shalstabinputcreator_algorithm import LandslideShalstabInputRasterCreator
from .Drokabasic_algorithm import RockfallDrokaBasic
from .Drokaflow_algorithm import RockfallDrokaFlow

class GeohazardProvider(QgsProcessingProvider):

    def __init__(self):
        """
        Default constructor.
        """
        QgsProcessingProvider.__init__(self)

    def unload(self):
        """
        Unloads the provider. Any tear-down steps required by the provider
        should be implemented here.
        """
        pass

    def loadAlgorithms(self):
        """
        Loads all algorithms belonging to this provider.
        """
        self.addAlgorithm(GroundmotionCIndex())
        self.addAlgorithm(LandslideShalstab())
        self.addAlgorithm(LandslideShalstabInputRasterCreator())
        self.addAlgorithm(RockfallDrokaBasic())
        self.addAlgorithm(RockfallDrokaFlow())
        # add additional algorithms here
        # self.addAlgorithm(MyOtherAlgorithm())

    def id(self):
        """
        Returns the unique provider id, used for identifying the provider. This
        string should be a unique, short, character only string, eg "qgis" or
        "gdal". This string should not be localised.
        """
        return 'Geohazard'

    def name(self):
        """
        Returns the provider name, which is used to describe the provider
        within the GUI.

        This string should be short (e.g. "Lastools") and localised.
        """
        return self.tr('Geohazard')

    def icon(self):
        """
        Should return a QIcon which is used for your provider inside
        the Processing toolbox.
        """
        icon_path = r"C:\Users\fasci\Desktop\geohazard\icon.png"
        return QIcon(QPixmap(icon_path))

    def longName(self):
        """
        Returns the a longer version of the provider name, which can include
        extra details such as version numbers. E.g. "Lastools LIDAR tools
        (version 2.2.1)". This string should be localised. The default
        implementation returns the same string as name().
        """
        return self.name()
