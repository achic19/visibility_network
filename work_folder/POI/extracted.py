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
    return layer


if __name__ == "__main__":
    app = QGuiApplication([])
    QgsApplication.setPrefixPath(r'C:\Program Files\QGIS 3.0\apps\qgis', True)
    QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())
    QgsApplication.initQgis()
    feedback = QgsProcessingFeedback()

    """Upload input data"""

    input_extract = os.path.dirname(os.path.dirname(__file__)) + r'\general\poi_re.shp'
    intersect = os.path.dirname(os.path.dirname(__file__)) + r'\general\buildings_0_re.shp'
    output = os.path.dirname(__file__) + r'\results_file\extracted.shp'
    params = {'INPUT': input_extract, 'PREDICATE': [6], 'INTERSECT': intersect, 'OUTPUT': output}

    processing.run('native:extractbylocation', params, feedback=feedback)

    """For standalone application"""
    # Exit applications
    QgsApplication.exitQgis()
    app.exit()
