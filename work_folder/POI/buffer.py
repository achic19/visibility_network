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

    constrains = os.path.join(os.path.dirname(os.path.dirname(__file__)), "general/buildings_0_re.shp")
    if os.path.exists(constrains):

        OUTPUT = os.path.join(os.path.dirname(__file__), "results_file/buffer.shp")

        params = {'INPUT': constrains, 'DISTANCE': 2, 'SEGMENTS': 1, 'END_CAP_STYLE': 2,
                  'JOIN_STYLE': 1, 'MITER_LIMIT': 2,
                  'DISSOLVE': False, 'OUTPUT': OUTPUT}

        processing.run('native:buffer', params, feedback=feedback)
    else:
        print("wrong path" + constrains)
    """For standalone application"""
    # Exit applications
    QgsApplication.exitQgis()
    app.exit()
