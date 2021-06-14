import sys

from PyQt5.QtGui import *
from qgis.analysis import QgsNativeAlgorithms
from qgis.core import *

# Tell Python where you will get processing from
sys.path.append(r'C:\Program Files\QGIS 3.0\apps\qgis\python\plugins')
# Reference the algorithm you want to run
from plugins.processing.algs.qgis.HubDistanceLines import *


def upload_new_layer(path, name):
    """Upload shp layers"""
    layer_name = "layer" + name
    provider_name = "ogr"
    layer = QgsVectorLayer(
        path,
        layer_name,
        provider_name)
    return layer


def distance_to_nearest_hub():
    app = QGuiApplication([])
    QgsApplication.setPrefixPath(r'C:\Program Files\QGIS 3.0\apps\qgis', True)
    QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())
    QgsApplication.initQgis()
    feedback = QgsProcessingFeedback()

    """Upload input data"""

    input_path = r'C:\Users\achituv\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\visibilitysyntax' \
                 r'\test\POI\results_file/cliped.shp'
    input = upload_new_layer(input_path, "test_input")
    hubs_path = r'C:\Users\achituv\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\visibilitysyntax' \
                r'\test\POI\results_file/points_along.shp'
    hubs = upload_new_layer(hubs_path, "test_hubs_")
    output = r'C:\Users\achituv\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\visibilitysyntax' \
             r'\test\POI\results_file/line_to_points.shp'

    alg = HubDistanceLines()
    alg.initAlgorithm()
    # Some preprocessing for context
    project = QgsProject.instance()

    target_crs = QgsCoordinateReferenceSystem()
    target_crs.createFromOgcWmsCrs(input.crs().authid())
    project.setCrs(target_crs)
    context = QgsProcessingContext()
    context.setProject(project)
    params = {'INPUT': input, 'HUBS': hubs, 'FIELD': 'vis_id', 'UNIT': 4, 'OUTPUT': output}
    alg.processAlgorithm(params, context, feedback=feedback)

    """For standalone application"""
    # Exit applications
    QgsApplication.exitQgis()
    app.exit()


if __name__ == "__main__":
    distance_to_nearest_hub()
