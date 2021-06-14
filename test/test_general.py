# 2.6.2021
import sys

from PyQt5.QtGui import *
from qgis.analysis import QgsNativeAlgorithms
from qgis.core import *

from qgis.core import *

sys.path.append(r'C:\Program Files\QGIS 3.16\apps\qgis-ltr\python\plugins')
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
    QgsApplication.setPrefixPath(r'C:\Program Files\QGIS 3.16\apps\qgis-ltr', True)
    app = QGuiApplication([])
    QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())
    QgsApplication.initQgis()
    feedback = QgsProcessingFeedback()
    processing.run("native:deleteduplicategeometries", {
        'INPUT': 'C:/Users/achituv/AppData/Roaming/QGIS/QGIS3/profiles/default/python/plugins'
                 '/poi_visibility_network/test/new_test/grid.shp',
        'OUTPUT': 'C:/Users/achituv/Downloads/dd3.shp'})


    """For standalone application"""
    # Exit applications
    QgsApplication.exitQgis()
    app.exit()

import sys
sys.path.append(r'C:\Program Files\QGIS 3.16\apps\qgis-ltr\python\plugins')
# Reference the algorithm you want to run
from plugins import processing
from PyQt5.QtGui import *

from qgis.analysis import QgsNativeAlgorithms
from qgis.core import *

app = QGuiApplication([])
QgsApplication.setPrefixPath(r'C:\Program Files\QGIS 3.0\apps\qgis', True)
QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())
QgsApplication.initQgis()


"""For standalone application"""
# Exit applications
QgsApplication.exitQgis()
app.exit()

# 25.05.2021
n_x = 5
y = 10
# test_array = [
#     [(i, j) for i in range(n_x)] for j in range(y)]
# print(test_array)

extent = {'x_min_y_max': (7, 8), 'x_max_y_max': (72, 8),
          'x_max_y_min': (7, 83), 'x_min_y_min': (74, 8)}
print(list(extent.values()))
