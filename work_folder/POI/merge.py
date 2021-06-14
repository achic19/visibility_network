import os
import sys

from PyQt5.QtGui import *
from qgis.analysis import QgsNativeAlgorithms
from qgis.core import *

# Tell Python where you will get processing from
sys.path.append(r'C:\Program Files\QGIS 3.0\apps\qgis\python\plugins')
# Reference the algorithm you want to run
from plugins import processing


def upload_new_layer(path, name):
    """Upload shp layers"""
    layer_name = "layer" + name
    provider_name = "ogr"
    layer = QgsVectorLayer(
        path,
        layer_name,
        provider_name)
    if not layer:
        print("Layer failed to load!-" + path)
    return layer


if __name__ == "__main__":
    app = QGuiApplication([])
    QgsApplication.setPrefixPath(r'C:\Program Files\QGIS 3.0\apps\qgis', True)
    QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())
    QgsApplication.initQgis()
    feedback = QgsProcessingFeedback()

    """Upload input data"""

    layer_1 = os.path.dirname(os.path.dirname(__file__)) + r'\mean_close_point\results_file\mean_close_coor.shp'
    layer_2 = os.path.dirname(__file__) + r'\results_file\off_pnts.shp'
    layer_3 = os.path.dirname(__file__) + r'\results_file\extracted.shp'

    merge_layers = [layer_1, layer_2, layer_3]

    OUTPUT = os.path.dirname(__file__) + r'\results_file\merge.shp'
    params = {'LAYERS': merge_layers, 'CRS': 'EPSG:3857', 'OUTPUT': OUTPUT}

    tt = processing.run('native:mergevectorlayers', params, feedback=feedback)
    """For standalone application"""
    # Exit applications
    QgsApplication.exitQgis()
    app.exit()
