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

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterRasterLayer
from qgis.core import QgsProcessingParameterNumber
from qgis.core import QgsProcessingParameterRasterDestination
from qgis.core import QgsProcessingParameterDefinition
import processing


class LandslideShalstab(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterRasterLayer('dtm', 'DTM', defaultValue=None))
        self.addParameter(QgsProcessingParameterNumber('cell_dtm', 'Cell DTM', type=QgsProcessingParameterNumber.Integer, defaultValue=5))
        self.addParameter(QgsProcessingParameterRasterLayer('friction_angle__', 'Friction angle_ϕ’ (°)', defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('depth_z_m', 'Depth_z (m)', defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('permeability_k_mh', 'Permeability_K (m/h)', defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('unit_weight__nm3', 'Unit Weight_γ (N/m3)', defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('soil_cohesion_nm2', 'Soil cohesion (N/m2)', defaultValue=None))
        param = QgsProcessingParameterRasterLayer('root_cohesion_nm2', 'Root cohesion (N/m2)', optional=True, defaultValue=None)
        param.setFlags(param.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(param)
        self.addParameter(QgsProcessingParameterRasterDestination('Critical_rainfallMmday', 'Critical_rainfall (mm/day)', createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterDestination('StabilityCells', 'Stability cells', createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterDestination('InstabilityCells', 'Instability cells', createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterDestination('Susceptibility', 'Susceptibility', createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(17, model_feedback)
        results = {}
        outputs = {}

        # absolute_stability
        alg_params = {
            'BAND_A': 1,
            'BAND_B': 1,
            'BAND_C': None,
            'BAND_D': None,
            'BAND_E': None,
            'BAND_F': None,
            'EXTENT_OPT': 0,  # Ignore
            'EXTRA': '',
            'FORMULA': '(1-(10000/A))*tan(radians(B))',
            'INPUT_A': parameters['unit_weight__nm3'],
            'INPUT_B': parameters['friction_angle__'],
            'INPUT_C': None,
            'INPUT_D': None,
            'INPUT_E': None,
            'INPUT_F': None,
            'NO_DATA': None,
            'OPTIONS': '',
            'PROJWIN': None,
            'RTYPE': 5,  # Float32
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Absolute_stability'] = processing.run('gdal:rastercalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Teta_slope
        alg_params = {
            'AS_PERCENT': False,
            'BAND': 1,
            'COMPUTE_EDGES': False,
            'EXTRA': None,
            'INPUT': parameters['dtm'],
            'OPTIONS': None,
            'SCALE': 1,
            'ZEVENBERGEN': False,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Teta_slope'] = processing.run('gdal:slope', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Condition_stability
        # Angoli in gradi
        alg_params = {
            'GRASS_RASTER_FORMAT_META': '',
            'GRASS_RASTER_FORMAT_OPT': '',
            'GRASS_REGION_CELLSIZE_PARAMETER': parameters['cell_dtm'],
            'GRASS_REGION_PARAMETER': parameters['dtm'],
            'a': outputs['Absolute_stability']['OUTPUT'],
            'b': outputs['Teta_slope']['OUTPUT'],
            'c': None,
            'd': None,
            'e': None,
            'expression': 'if(A>tan(B),9999,0)',
            'f': None,
            'output': parameters['StabilityCells']
        }
        outputs['Condition_stability'] = processing.run('grass7:r.mapcalc.simple', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['StabilityCells'] = outputs['Condition_stability']['output']

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # T_hydraulic transmission (m2/day)
        # (*24) perchè si riferisce al giorno
        alg_params = {
            'BAND_A': 1,
            'BAND_B': 1,
            'BAND_C': 1,
            'BAND_D': None,
            'BAND_E': None,
            'BAND_F': None,
            'EXTENT_OPT': 0,  # Ignore
            'EXTRA': None,
            'FORMULA': 'A*B*24*cos(radians(C))',
            'INPUT_A': parameters['permeability_k_mh'],
            'INPUT_B': parameters['depth_z_m'],
            'INPUT_C': outputs['Teta_slope']['OUTPUT'],
            'INPUT_D': None,
            'INPUT_E': None,
            'INPUT_F': None,
            'NO_DATA': None,
            'OPTIONS': None,
            'PROJWIN': None,
            'RTYPE': 5,  # Float32
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['T_hydraulicTransmissionM2day'] = processing.run('gdal:rastercalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # C
        alg_params = {
            'BAND_A': 1,
            'BAND_B': 1,
            'BAND_C': 1,
            'BAND_D': 1,
            'BAND_E': 1,
            'BAND_F': None,
            'EXTENT_OPT': 0,  # Ignore
            'EXTRA': '',
            'FORMULA': '(A+B)/(C*(cos(radians(D))*(E)))',
            'INPUT_A': parameters['soil_cohesion_nm2'],
            'INPUT_B': parameters['root_cohesion_nm2'],
            'INPUT_C': parameters['depth_z_m'],
            'INPUT_D': outputs['Teta_slope']['OUTPUT'],
            'INPUT_E': parameters['unit_weight__nm3'],
            'INPUT_F': None,
            'NO_DATA': None,
            'OPTIONS': None,
            'PROJWIN': None,
            'RTYPE': 5,  # Float32
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['C'] = processing.run('gdal:rastercalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # r.terraflow
        # Da cui si prende in considerazione solo "Flow accumulation"
        alg_params = {
            '-s': False,
            'GRASS_RASTER_FORMAT_META': None,
            'GRASS_RASTER_FORMAT_OPT': None,
            'GRASS_REGION_CELLSIZE_PARAMETER': parameters['cell_dtm'],
            'GRASS_REGION_PARAMETER': parameters['dtm'],
            'd8cut': None,
            'elevation': parameters['dtm'],
            'memory': 300,
            'accumulation': QgsProcessing.TEMPORARY_OUTPUT,
            'direction': QgsProcessing.TEMPORARY_OUTPUT,
            'filled': QgsProcessing.TEMPORARY_OUTPUT,
            'stats': QgsProcessing.TEMPORARY_OUTPUT,
            'swatershed': QgsProcessing.TEMPORARY_OUTPUT,
            'tci': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Rterraflow'] = processing.run('grass7:r.terraflow', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # Constant raster_Cell size DEM
        alg_params = {
            'EXTENT': parameters['dtm'],
            'NUMBER': parameters['cell_dtm'],
            'OUTPUT_TYPE': 5,  # Float32
            'PIXEL_SIZE': parameters['cell_dtm'],
            'TARGET_CRS': parameters['dtm'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ConstantRaster_cellSizeDem'] = processing.run('native:createconstantrasterlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # A_contribution area
        alg_params = {
            'BAND_A': 1,
            'BAND_B': 1,
            'BAND_C': None,
            'BAND_D': None,
            'BAND_E': None,
            'BAND_F': None,
            'EXTENT_OPT': 0,  # Ignore
            'EXTRA': None,
            'FORMULA': 'abs(A*B*B)',
            'INPUT_A': outputs['Rterraflow']['accumulation'],
            'INPUT_B': outputs['ConstantRaster_cellSizeDem']['OUTPUT'],
            'INPUT_C': None,
            'INPUT_D': None,
            'INPUT_E': None,
            'INPUT_F': None,
            'NO_DATA': None,
            'OPTIONS': None,
            'PROJWIN': None,
            'RTYPE': 5,  # Float32
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['A_contributionArea'] = processing.run('gdal:rastercalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}

        # absolute_instability
        # Angoli in gradi
        alg_params = {
            'GRASS_RASTER_FORMAT_META': '',
            'GRASS_RASTER_FORMAT_OPT': '',
            'GRASS_REGION_CELLSIZE_PARAMETER': 0,
            'GRASS_REGION_PARAMETER': None,
            'a': outputs['C']['OUTPUT'],
            'b': outputs['Teta_slope']['OUTPUT'],
            'c': parameters['friction_angle__'],
            'd': None,
            'e': None,
            'expression': '(A/cos(B))+(tan(C))',
            'f': None,
            'output': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Absolute_instability'] = processing.run('grass7:r.mapcalc.simple', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(9)
        if feedback.isCanceled():
            return {}

        # Condition_instability
        alg_params = {
            'GRASS_RASTER_FORMAT_META': '',
            'GRASS_RASTER_FORMAT_OPT': '',
            'GRASS_REGION_CELLSIZE_PARAMETER': parameters['cell_dtm'],
            'GRASS_REGION_PARAMETER': parameters['dtm'],
            'a': outputs['Absolute_instability']['output'],
            'b': outputs['Teta_slope']['OUTPUT'],
            'c': None,
            'd': None,
            'e': None,
            'expression': 'if(A<tan(B),-9999,0)',
            'f': None,
            'output': parameters['InstabilityCells']
        }
        outputs['Condition_instability'] = processing.run('grass7:r.mapcalc.simple', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['InstabilityCells'] = outputs['Condition_instability']['output']

        feedback.setCurrentStep(10)
        if feedback.isCanceled():
            return {}

        # q_critic 02
        # (+ Condizione_Stabilità + Condizione_Instabilità)
        # 
        # Angoli in gradi
        alg_params = {
            'GRASS_RASTER_FORMAT_META': '',
            'GRASS_RASTER_FORMAT_OPT': '',
            'GRASS_REGION_CELLSIZE_PARAMETER': parameters['cell_dtm'],
            'GRASS_REGION_PARAMETER': parameters['dtm'],
            'a': parameters['unit_weight__nm3'],
            'b': outputs['C']['OUTPUT'],
            'c': outputs['Teta_slope']['OUTPUT'],
            'd': parameters['friction_angle__'],
            'e': None,
            'expression': '((A/10000)*(1-(1-(B/(sin(C)))))*tan(C)/tan(D))',
            'f': None,
            'output': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Q_critic02'] = processing.run('grass7:r.mapcalc.simple', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(11)
        if feedback.isCanceled():
            return {}

        # q_critic 01
        # Formula divisa in due parti
        alg_params = {
            'BAND_A': 1,
            'BAND_B': 1,
            'BAND_C': 1,
            'BAND_D': 1,
            'BAND_E': None,
            'BAND_F': None,
            'EXTENT_OPT': 0,  # Ignore
            'EXTRA': '',
            'FORMULA': '(A)*(sin(radians(B)))*(C/D)',
            'INPUT_A': outputs['T_hydraulicTransmissionM2day']['OUTPUT'],
            'INPUT_B': outputs['Teta_slope']['OUTPUT'],
            'INPUT_C': outputs['ConstantRaster_cellSizeDem']['OUTPUT'],
            'INPUT_D': outputs['A_contributionArea']['OUTPUT'],
            'INPUT_E': None,
            'INPUT_F': None,
            'NO_DATA': None,
            'OPTIONS': '',
            'PROJWIN': None,
            'RTYPE': 5,  # Float32
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Q_critic01'] = processing.run('gdal:rastercalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(12)
        if feedback.isCanceled():
            return {}

        # q_critic (mm/day)
        alg_params = {
            'BAND_A': 1,
            'BAND_B': 1,
            'BAND_C': 1,
            'BAND_D': 1,
            'BAND_E': None,
            'BAND_F': None,
            'EXTENT_OPT': 0,  # Ignore
            'EXTRA': '',
            'FORMULA': '((A*B)+(C)+(D))*1000',
            'INPUT_A': outputs['Q_critic01']['OUTPUT'],
            'INPUT_B': outputs['Q_critic02']['output'],
            'INPUT_C': outputs['Condition_stability']['output'],
            'INPUT_D': outputs['Condition_instability']['output'],
            'INPUT_E': None,
            'INPUT_F': None,
            'NO_DATA': None,
            'OPTIONS': '',
            'PROJWIN': None,
            'RTYPE': 5,  # Float32
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Q_criticMmday'] = processing.run('gdal:rastercalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(13)
        if feedback.isCanceled():
            return {}

        # Reclassifies stab and instab cells
        alg_params = {
            'DATA_TYPE': 5,  # Float32
            'INPUT_RASTER': outputs['Q_criticMmday']['OUTPUT'],
            'NODATA_FOR_MISSING': False,
            'NO_DATA': -9999,
            'RANGE_BOUNDARIES': 0,  # min < valore <= max
            'RASTER_BAND': 1,
            'TABLE': ['-99999999','0','0','0','9999','1','9999','9999999999999','nan'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ReclassifiesStabAndInstabCells'] = processing.run('native:reclassifybytable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(14)
        if feedback.isCanceled():
            return {}

        # Critical_rainfall (mm/day)
        alg_params = {
            'BAND_A': 1,
            'BAND_B': 1,
            'BAND_C': None,
            'BAND_D': None,
            'BAND_E': None,
            'BAND_F': None,
            'EXTENT_OPT': 0,  # Ignore
            'EXTRA': '',
            'FORMULA': 'A*B',
            'INPUT_A': outputs['Q_criticMmday']['OUTPUT'],
            'INPUT_B': outputs['ReclassifiesStabAndInstabCells']['OUTPUT'],
            'INPUT_C': None,
            'INPUT_D': None,
            'INPUT_E': None,
            'INPUT_F': None,
            'NO_DATA': None,
            'OPTIONS': '',
            'PROJWIN': None,
            'RTYPE': 5,  # Float32
            'OUTPUT': parameters['Critical_rainfallMmday']
        }
        outputs['Critical_rainfallMmday'] = processing.run('gdal:rastercalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Critical_rainfallMmday'] = outputs['Critical_rainfallMmday']['OUTPUT']

        feedback.setCurrentStep(15)
        if feedback.isCanceled():
            return {}

        # log((qcr/1000)/T) [1/m]
        alg_params = {
            'BAND_A': 1,
            'BAND_B': 1,
            'BAND_C': None,
            'BAND_D': None,
            'BAND_E': None,
            'BAND_F': None,
            'EXTENT_OPT': 0,  # Ignore
            'EXTRA': '',
            'FORMULA': 'log((A/1000)/B)',
            'INPUT_A': outputs['Critical_rainfallMmday']['OUTPUT'],
            'INPUT_B': outputs['T_hydraulicTransmissionM2day']['OUTPUT'],
            'INPUT_C': None,
            'INPUT_D': None,
            'INPUT_E': None,
            'INPUT_F': None,
            'NO_DATA': None,
            'OPTIONS': '',
            'PROJWIN': None,
            'RTYPE': 5,  # Float32
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Logqcr1000t1m'] = processing.run('gdal:rastercalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(16)
        if feedback.isCanceled():
            return {}

        # Reclassifies
        # Classificazione:
        # 
        # 1: [-inf, -3.4]
        # 2: [-3.4, -3.1]
        # 3: [-3.1, -2.8]
        # 4: [-2.8, -2.5]
        # 5: [-2.5, -2.2]
        # 5: [-2.2, -1.9]
        # 5: [-1.9, +inf]
        alg_params = {
            'DATA_TYPE': 5,  # Float32
            'INPUT_RASTER': outputs['Logqcr1000t1m']['OUTPUT'],
            'NODATA_FOR_MISSING': False,
            'NO_DATA': -9999,
            'RANGE_BOUNDARIES': 0,  # min < valore <= max
            'RASTER_BAND': 1,
            'TABLE': ['-inf','-3.4','1','-3.4','-3.1','2','-3.1','-2.8','3','-2.8','-2.5','4','-2.5','-2.2','5','-2.2','-1.9','6','-1.9','+inf','7'],
            'OUTPUT': parameters['Susceptibility']
        }
        outputs['Reclassifies'] = processing.run('native:reclassifybytable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Susceptibility'] = outputs['Reclassifies']['OUTPUT']
        return results

    def name(self):
        return 'Landslide - Shalstab'

    def displayName(self):
        return 'Landslide - Shalstab'

    def group(self):
        return 'Landslide'

    def groupId(self):
        return 'Landslide'

    def shortHelpString(self):
        return """<html><body><p><!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li { white-space: pre-wrap; }
</style></head><body style=" font-family:'MS Shell Dlg 2'; font-size:8.25pt; font-weight:400; font-style:normal;">
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:18pt;">SHALSTAB</span></p>
<p style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Shalstab is a physically-based model used to assess the triggering of shallow landslides due to infiltrated rainfall, following the method proposed by MONTGOMERY &amp; DIETRICH (1994) and DIETRICH &amp; MONTGOMERY (1998). The method combin a limit equilibrium stability model for infinite slopes with a steady-state hydrological model.</p>
<p style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">The algorithm enables the assessment of slope instability hazard by obtaining the net infiltrated rainfall component and classifying the terrain into seven classes based on susceptibility. This algorithm evaluates relative hazard, spatial in nature, without considering the temporal dimension related to the probability of the event occurring (susceptibility). In any case, the predictions resulting from this algorithm should be compared with the characteristics of mapped landslides whenever possible.</p>
<p style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">ATTENTION! Before running the model it is necessary to insert in the project the Dem and the raster of the input data (hydrological and physical-mechanical parameters) making sure that they have the same resolution.</p>
<p style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">The conditions of absolute stability are set, which identifies those topographical elements that are classified as stable even when the soil is completely saturated</p>
<p style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">tan (θ) ≤ (1- γ<span style=" vertical-align:sub;">w</span>/γ) * tan (φ)</p>
<p style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt;"> and absolute instability, which is defined for those topographical elements classified as unstable even in the absence of rain</span></p>
<p style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">tan (θ) ≥ C/cos (θ) + tan (φ)</p>
<p style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">By imposing a safety factor of 1, the daily critical infiltration threshold is obtained which leads to limit equilibrium conditions:</p>
<p style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">q<span style=" vertical-align:sub;">cr</span> = T * sen (θ) * (cell size raster)/A * [γ/ γ<span style=" vertical-align:sub;">w</span> * (1 - (1 – C/sen (θ)))] * tan (θ)/tan (φ) + cond.stab. + cond.instab.</p>
<p style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">In the model, this equation was simply divided into two parts.</p>
<p style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Shalstab algorithm provides the spatial distribution of the absolute stable and absolute unstable cells, as well as the critical effective (infiltrated) rainfall that leads each cell to a Fs of 1.</p></body></html></p>
<h2>Parametri in ingresso
</h2>
<h3>DTM</h3>
<p>Raster layer of the DTM</p>
<h3>Cell DTM</h3>
<p>Dimension of the DTM cell (m)</p>
<h3>Friction angle_ϕ’ (°)</h3>
<p>Raster layer of the friction angle of the soil ϕ’ (°)</p>
<h3>Depth_z (m)</h3>
<p>Raster layer of the thickness of the potentially unstable layer (m)</p>
<h3>Permeability_K (m/h)</h3>
<p>Raster layer of the permeability coefficient of the soil Ks (m/h)</p>
<h3>Unit Weight_γ (N/m3)</h3>
<p>Raster layer of the weight per unit volume of the soil γ (N/m3)</p>
<h3>Soil cohesion (N/m2)</h3>
<p>Raster layer of soil cohesion c_soil (N/m2)</p>
<h3>Root cohesion (N/m2)</h3>
<p>Raster layer of root cohesion c_root (N/m2)</p>
<h2>Risultati</h2>
<h3>Critical_rainfall (mm/day)</h3>
<p>Distribution of critical infiltrated rainfall qcr (mm/day).
In the qcr map absolute stable cells assume no data values and absolute unstable cells assume qcr = 0.
</p>
<h3>Stability cells</h3>
<p>Absolute stable zones.
Absolutely stable cells have a value of 9999.</p>
<h3>Instability cells</h3>
<p>Absolute unstable zones.
Absolutely unstable cells have a value of -9999.</p>
<h3>Susceptibility</h3>
<p>The susceptibility raster map is a reclassification of qcr as suggested by Montgomery and Dietrich (1998). This classification into seven classes provides the values of qcr/T in logarithmic form. This ratio reflects the magnitude of the precipitation event, represented by q, in relation to the subsurface's ability to move water downslope, i.e., the transmissivity (T). </p>
<h2>Esempi</h2>
<p><!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li { white-space: pre-wrap; }
</style></head><body style=" font-family:'MS Shell Dlg 2'; font-size:8.25pt; font-weight:400; font-style:normal;">
<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><br /></p></body></html></p><br><p align="right">Autore della guida: Claudio Fasciano</p></body></html>"""

    def createInstance(self):
        return LandslideShalstab()
