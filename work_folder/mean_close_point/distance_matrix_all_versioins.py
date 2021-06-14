# -*- coding: utf-8 -*-

"""
***************************************************************************
    PointDistance.py
    ---------------------
    Date                 : August 2012
    Copyright            : (C) 2012 by Victor Olaya
    Email                : volayaf at gmail dot com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

__author__ = 'Victor Olaya'
__date__ = 'August 2012'
__copyright__ = '(C) 2012, Victor Olaya'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import math

from qgis.PyQt.QtCore import QVariant
from qgis.core import (QgsFeatureRequest,
                       QgsField,
                       QgsFields,
                       QgsFeature,
                       QgsGeometry,
                       QgsDistanceArea,
                       QgsFeatureSink,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessing,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterField,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterFeatureSink,
                       QgsSpatialIndex,
                       QgsWkbTypes)



def linearMatrix(parameters, context, source, inField, target_source, targetField,
                 matType, nPoints, feedback):
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


    out_wkb = QgsWkbTypes.multiType(source.wkbType()) if matType == 0 else source.wkbType()
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
        # Save the geomerty of the current points and its id
        inGeom = inFeat.geometry()
        inID = str(inFeat.attributes()[inIdx])
        # with index.nearestNeighbor the nPoints relate to the current  points are calculated
        featList = index.nearestNeighbor(inGeom.asPoint(), nPoints)
        distList = []
        vari = 0.0
        request = QgsFeatureRequest().setFilterFids(featList).setSubsetOfAttributes([outIdx]).setDestinationCrs(
            source.sourceCrs(), context.transformContext())
        for outFeat in target_source.getFeatures(request):
            if feedback.isCanceled():
                break

            outID = outFeat.attributes()[outIdx]
            outGeom = outFeat.geometry()
            dist = distArea.measureLine(inGeom.asPoint(),
                                        outGeom.asPoint())

            if matType == 0:
                out_feature = QgsFeature()
                out_geom = QgsGeometry.unaryUnion([inFeat.geometry(), outFeat.geometry()])
                out_feature.setGeometry(out_geom)
                out_feature.setAttributes([inID, outID, dist])
                sink.addFeature(out_feature, QgsFeatureSink.FastInsert)
            else:
                distList.append(float(dist))

        if matType != 0:
            mean = sum(distList) / len(distList)
            for i in distList:
                vari += (i - mean) * (i - mean)
            vari = math.sqrt(vari / len(distList))

            out_feature = QgsFeature()
            out_feature.setGeometry(inFeat.geometry())
            out_feature.setAttributes([inID, mean, vari, min(distList), max(distList)])
            sink.addFeature(out_feature, QgsFeatureSink.FastInsert)

        feedback.setProgress(int(current * total))

    return {self.OUTPUT: dest_id}
