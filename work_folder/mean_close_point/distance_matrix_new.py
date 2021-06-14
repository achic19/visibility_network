import sys

from PyQt5.QtGui import *
from qgis.analysis import QgsNativeAlgorithms
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


def processAlgorithm(self, parameters, context, feedback):
    source = self.parameterAsSource(parameters, self.INPUT, context)
    source_field = self.parameterAsString(parameters, self.INPUT_FIELD, context)
    target_source = self.parameterAsSource(parameters, self.TARGET, context)
    target_field = self.parameterAsString(parameters, self.TARGET_FIELD, context)
    nPoints = self.parameterAsInt(parameters, self.NEAREST_POINTS, context)

    if nPoints < 1:
        nPoints = target_source.featureCount()

    # Linear distance matrix
    return linearMatrix(self,parameters, context, source, source_field, target_source, target_field,
                              nPoints, feedback)


def linearMatrix(self, parameters, context, source, inField, target_source, targetField,
                 nPoints, feedback):


    inIdx = source.fields().lookupField(inField)
    outIdx = target_source.fields().lookupField(targetField)

    fields = QgsFields()
    input_id_field = source.fields()[inIdx]
    input_id_field.setName('InputID')
    fields.append(input_id_field)

    target_id_field = target_source.fields()[outIdx]
    target_id_field.setName('TargetID')
    fields.append(target_id_field)
    fields.append(QgsField('Distance', QVariant.Double))


    out_wkb = QgsWkbTypes.multiType(source.wkbType())
    (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT, context,
                                           fields, out_wkb, source.sourceCrs())

    index = QgsSpatialIndex(target_source.getFeatures(
        QgsFeatureRequest().setSubsetOfAttributes([]).setDestinationCrs(source.sourceCrs(),
                                                                        context.transformContext())), feedback)

    distArea = QgsDistanceArea()
    distArea.setSourceCrs(source.sourceCrs(), context.transformContext())
    distArea.setEllipsoid(context.project().ellipsoid())

    features = source.getFeatures(QgsFeatureRequest().setSubsetOfAttributes([inIdx]))
    total = 100.0 / source.featureCount() if source.featureCount() else 0
    for current, inFeat in enumerate(features):
        if feedback.isCanceled():
            break

        inGeom = inFeat.geometry()
        inID = str(inFeat.attributes()[inIdx])
        featList = index.nearestNeighbor(inGeom.asPoint(), nPoints)
        request = QgsFeatureRequest().setFilterFids(featList).setSubsetOfAttributes([outIdx]).setDestinationCrs(
            source.sourceCrs(), context.transformContext())
        for outFeat in target_source.getFeatures(request):
            if feedback.isCanceled():
                break

            outID = outFeat.attributes()[outIdx]
            outGeom = outFeat.geometry()
            dist = distArea.measureLine(inGeom.asPoint(),
                                        outGeom.asPoint())


            out_feature = QgsFeature()
            out_geom = QgsGeometry.unaryUnion([inFeat.geometry(), outFeat.geometry()])
            out_feature.setGeometry(out_geom)
            out_feature.setAttributes([inID, outID, dist])
            sink.addFeature(out_feature, QgsFeatureSink.FastInsert)

        feedback.setProgress(int(current * total))

    return {self.OUTPUT: dest_id}


if __name__ == "__main__":
    QgsApplication.setPrefixPath(r'C:\Program Files\QGIS 3.0\apps\qgis', True)
    app = QGuiApplication([])
    QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())
    QgsApplication.initQgis()
    feedback = QgsProcessingFeedback()

    """Upload input data"""
    work_folder = os.path.dirname(__file__)
    param_input = os.path.join(os.path.split(work_folder)[0], r'general\intersections.shp')
    param_output = os.path.join(work_folder, r'results_file\distance_matrix4.shp')

    params = {'INPUT': param_input, 'INPUT_FIELD': 'vis_id', 'TARGET': param_input, 'TARGET_FIELD': 'vis_id',
              'MATRIX_TYPE': 0, 'NEAREST_POINTS': 10, 'OUTPUT': param_output}

    alg = PointDistance()
    alg.initAlgorithm()

    # Some preprocessing for context
    project = QgsProject.instance()

    target_crs = QgsCoordinateReferenceSystem()
    layer_1 = upload_new_layer(param_input, "test")
    target_crs.createFromOgcWmsCrs(layer_1.crs().authid())
    project.setCrs(target_crs)
    context = QgsProcessingContext()
    context.setProject(project)

    processAlgorithm(alg,params, context, feedback=feedback)

    """For standalone application"""
    # Exit applications
    QgsApplication.exitQgis()
    app.exit()
