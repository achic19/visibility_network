import sys


from PyQt5.QtGui import *
from qgis.analysis import QgsNativeAlgorithms
from qgis.core import *


from qgis.core import *


# Tell Python where you will get processing from
sys.path.append(r'C:\Program Files\QGIS 3.0\apps\qgis\python\plugins')
# Reference the algorithm you want to run
from plugins.processing.algs.qgis.PointDistance import *


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

    QgsApplication.setPrefixPath(r'C:\Program Files\QGIS 3.0\apps\qgis', True)
    app = QGuiApplication([])
    QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())
    QgsApplication.initQgis()
    feedback = QgsProcessingFeedback()

    """Upload input data"""
    work_folder = os.path.dirname(__file__)
    input = os.path.join(os.path.split(os.path.split(work_folder)[0])[0], r'general/intersections.shp')
    input = 'C:/Users/achituv/AppData/Roaming/QGIS/QGIS3/profiles/default/python/plugins/visibilitysyntax/processing/intersections.shp'
    
    INPUT_FIELD = 'vis_id'
    TARGET = 'C:/Users/achituv/AppData/Roaming/QGIS/QGIS3/profiles/default/python/plugins/visibilitysyntax/processing/intersections.shp'
    TARGET_FIELD = 'vis_id'
    OUTPUT = r'C:\Users\achituv\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\visibilitysyntax\test\mean_close_point/distance_matrix.shp'
    params = {'INPUT': input, 'INPUT_FIELD': INPUT_FIELD, 'TARGET': TARGET, 'TARGET_FIELD': TARGET_FIELD,
              'OUTPUT': OUTPUT,
              'MATRIX_TYPE': 0, 'NEAREST_POINTS': 10, 'OUTPUT': OUTPUT}
    
    alg = PointDistance()
    alg.initAlgorithm()
    
    # Some preprocessing for context
    project = QgsProject.instance()
    
    target_crs = QgsCoordinateReferenceSystem()
    layer_1 = upload_new_layer(input, "test")
    target_crs.createFromOgcWmsCrs(layer_1.crs().authid())
    project.setCrs(target_crs)
    context = QgsProcessingContext()
    context.setProject(project)
    alg.processAlgorithm(params, context, feedback=feedback)

    """For standalone application"""
    # Exit applications
    QgsApplication.exitQgis()
    app.exit()
