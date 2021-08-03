# Tell Python where you will get processing from

import sys

from qgis.core import *

import time

sys.path.append(r'C:\Program Files\QGIS 3.0\apps\qgis\python\plugins')
# Reference the algorithm you want to run
sys.path.append(r'C:\Program Files\QGIS 3.0\apps\qgis\python\plugins')
sys.path.append(r'C:\Program Files\QGIS 3.4\apps\qgis-ltr\python\plugins')
sys.path.append(r'C:\Program Files\QGIS 3.10\apps\qgis-ltr\python\plugins')
sys.path.append(r'C:\Program Files\QGIS 3.16\apps\qgis-ltr\python\plugins')
from plugins import processing


class classicFindSightLine:
    def __init__(self, pnts_layer, intersect):

        # Save points with python dataset
        junctions_features = pnts_layer.getFeatures()
        # Get the geometry of each element into a list
        python_geo = list(map(lambda x: x.geometry(), junctions_features))
        # Populate line file with potential sight of lines
        # First, upload the gis file to remove old sight lines and make it ready for new sight lines
        path = "new_lines.shp"
        vector_grid = QgsVectorLayer(path, "sight_line", "ogr")
        vector_grid.dataProvider().truncate()

        feature_list = []
        for i, feature in enumerate(python_geo):
            for j in range(i + 1, len(python_geo)):
                # Add geometry to lines' features  - the nodes of each line
                feat = QgsFeature()
                point1 = feature.asPoint()
                point2 = python_geo[j].asPoint()
                gLine = QgsGeometry.fromPolylineXY([point1, point2])
                feat.setGeometry(gLine)
                # Add  the nodes id as attributes to lines' features
                feat.setAttributes([i, j])
                feature_list.append(feat)
        vector_grid.dataProvider().addFeatures(feature_list)

        sight_line_output = "new_lines.shp"
        params = {'INPUT': path, 'PREDICATE': [2], 'INTERSECT': intersect,
                  'OUTPUT': sight_line_output}
        self.res = processing.run('native:extractbylocation', params, feedback=self.feedback)
