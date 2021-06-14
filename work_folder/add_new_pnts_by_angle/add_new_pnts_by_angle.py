import json
import math
import os
import sys

import pandas as pd
from PyQt5.QtGui import *

from qgis.analysis import QgsNativeAlgorithms
from qgis.core import *

# Tell Python where you will get processing from
sys.path.append(r'C:\Program Files\QGIS 3.0\apps\qgis\python\plugins')
sys.path.append(r'C:\Program Files\QGIS 3.4\apps\qgis-ltr\python\plugins')
sys.path.append(r'C:\Program Files\QGIS 3.10\apps\qgis-ltr\python\plugins')
from plugins import processing


# Reference the algorithm you want to run


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
    # Initialize QGIS app
    app = QGuiApplication([])
    QgsApplication.setPrefixPath(r'C:\Program Files\QGIS 3.10\apps\qgis', True)
    QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())
    QgsApplication.initQgis()
    feedback = QgsProcessingFeedback()

    """multipart to single parts"""
    line_path = os.path.dirname(os.path.dirname(__file__)) + r'/fix_geometry/results_file/dissolve_0.shp'
    single_part = os.path.dirname(__file__) + r'/single_part.shp'
    params = {'INPUT': line_path, 'OUTPUT': single_part}
    processing.run('native:multiparttosingleparts', params, feedback=feedback)

    """split with lines"""
    split_with_lines = os.path.dirname(__file__) + r'/splitwithlines.shp'
    processing.run("native:splitwithlines", {'INPUT': single_part,
                                             'LINES': single_part,
                                             'OUTPUT': split_with_lines})
    lines = upload_new_layer(split_with_lines, "lines")
    temp_list = []


    # calculate azimuth and save points with azimuth larger than 30 degrees
    for feature in lines.getFeatures():
        feature_list = feature.geometry().asJson()
        json1_data = json.loads(feature_list)['coordinates']
        for cor_set in json1_data:
            for i in range(0, len(cor_set) - 2):
                # calc slope as  an angle
                x1 = cor_set[i][0]
                y1 = cor_set[i][1]
                x2 = cor_set[i + 1][0]
                y2 = cor_set[i + 1][1]
                x3 = cor_set[i + 2][0]
                y3 = cor_set[i + 2][1]
                angle1 = math.atan2(x2 - x1, y2 - y1) * 180 / math.pi
                angle2 = math.atan2(x3 - x2, y3 - y2) * 180 / math.pi
                # calc angle between two lines
                angleB = 180 - angle1 + angle2
                if angleB < 0:
                    angleB = angleB + 360
                if angleB > 360:
                    angleB = angleB - 360
                if abs(angleB - 180) > 30:
                    feat = QgsFeature()
                    point = QgsPointXY(x2, y2)
                    g_pnt = QgsGeometry.fromPointXY(point)
                    feat.setGeometry(g_pnt)
                    temp_list.append(feat)
                    print(abs(angleB - 180))


    """For standalone application"""
    # Exit applications
    QgsApplication.exitQgis()
    app.exit()
