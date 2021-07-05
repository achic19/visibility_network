# 5.7.2021
import numpy


class SymNDArray(numpy.ndarray):
    """
    NumPy array subclass for symmetric matrices.

    A SymNDArray arr is such that doing arr[i,j] = value
    automatically does arr[j,i] = value, so that array
    updates remain symmetrical.
    """

    def __setitem__(self, index, value):
        super(SymNDArray, self).__setitem__(index, value)
        super(SymNDArray, self).__setitem__((index[1], index[0]), value)


def symmetrize(a):
    """
    Return a symmetrized version of NumPy array a.

    Values 0 are replaced by the array value at the symmetric
    position (with respect to the diagonal), i.e. if a_ij = 0,
    then the returned array a' is such that a'_ij = a_ji.

    Diagonal values are left untouched.

    a -- square NumPy array, such that a_ij = 0 or a_ji = 0,
    for i != j.
    """
    return a + a.T - numpy.diag(a.diagonal())


def symarray(input_array):
    """
    Return a symmetrized version of the array-like input_array.

    The returned array has class SymNDArray. Further assignments to the array
    are thus automatically symmetrized.
    """
    return symmetrize(numpy.asarray(input_array)).view(SymNDArray)


# Example:
a = symarray(numpy.zeros((3, 3)))
a[0, 1] = 42
print(a)  # a[1, 0] == 42 too!
# 2.6.2021
import sys

from PyQt5.QtGui import *
from qgis.analysis import QgsNativeAlgorithms
from qgis.core import *

from qgis.core import *

# sys.path.append(r'C:\Program Files\QGIS 3.16\apps\qgis-ltr\python\plugins')
# # Reference the algorithm you want to run
# from plugins import processing
#
#
#
#
# def upload_new_layer(path, name):
#     """Upload shp layers"""
#     layer_name = "layer" + name
#     provider_name = "ogr"
#     layer = QgsVectorLayer(
#         path,
#         layer_name,
#         provider_name)
#     return layer
#
#
# if __name__ == "__main__":
#     QgsApplication.setPrefixPath(r'C:\Program Files\QGIS 3.16\apps\qgis-ltr', True)
#     app = QGuiApplication([])
#     QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())
#     QgsApplication.initQgis()
#     feedback = QgsProcessingFeedback()
#     processing.run("native:deleteduplicategeometries", {
#         'INPUT': 'C:/Users/achituv/AppData/Roaming/QGIS/QGIS3/profiles/default/python/plugins'
#                  '/poi_visibility_network/test/new_test/grid.shp',
#         'OUTPUT': 'C:/Users/achituv/Downloads/dd3.shp'})
#
#
#     """For standalone application"""
#     # Exit applications
#     QgsApplication.exitQgis()
#     app.exit()
#
# import sys
# sys.path.append(r'C:\Program Files\QGIS 3.16\apps\qgis-ltr\python\plugins')
# # Reference the algorithm you want to run
# from plugins import processing
# from PyQt5.QtGui import *
#
# from qgis.analysis import QgsNativeAlgorithms
# from qgis.core import *
#
# app = QGuiApplication([])
# QgsApplication.setPrefixPath(r'C:\Program Files\QGIS 3.0\apps\qgis', True)
# QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())
# QgsApplication.initQgis()
#
#
# """For standalone application"""
# # Exit applications
# QgsApplication.exitQgis()
# app.exit()

# 25.05.2021
# n_x = 5
# y = 10
# # test_array = [
# #     [(i, j) for i in range(n_x)] for j in range(y)]
# # print(test_array)
#
# extent = {'x_min_y_max': (7, 8), 'x_max_y_max': (72, 8),
#           'x_max_y_min': (7, 83), 'x_min_y_min': (74, 8)}
# print(list(extent.values()))
