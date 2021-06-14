# Tell Python where you will get processing from
import json
import os
import sys
from operator import itemgetter

from PyQt5.QtGui import *
# from test.test_same_area import test_same_area_grid
from qgis.PyQt.QtCore import QVariant
from qgis.core import *
from shapely.geometry import Point

sys.path.append(r'C:\Program Files\QGIS 3.0\apps\qgis\python\plugins')


# Reference the algorithm you want to run

class PolygonPoint(Point):
    """
    The class store the point and the equation_params to the previous and next points based on their order
     in the polygon
    """

    def __init__(self, **kwargs):
        print(kwargs)
        super().__init__(kwargs['pnt'][0], kwargs['pnt'][1])

        # self.eq_params_pre = self.calc_equation_params(kwargs['pre_pnt'][0], kwargs['pre_pnt'][1])
        # self.eq_params_ne = self.calc_equation_params(kwargs['nxt_pnt'][0], kwargs['nxt_pnt'][1])

    def calc_equation_params(self, x_1, y_1):
        """
        The method return the equation_params(slope and distance) from two points (the object points and another
        given points)
        :param x_1:
        :param y_1:
        :return:
        """
        slope = (y_1 - self.y) / (x_1 - self.x)
        intersect = self.y - self.x * slope
        print([slope, intersect])
        return [slope, intersect]


class Cell:
    def __init__(self, x, y, spacing, i_x, i_y):
        self.points = []
        self.extent = {'x_y': QgsPointXY(x, y), 'x_max_y': QgsPointXY(x + spacing, y),
                       'x_max_y_max': QgsPointXY(x + spacing, y + spacing), 'x_y_max': QgsPointXY(x, y + spacing)}
        self.i_e = i_x
        self.i_n = i_y


class SameAreaCell:

    def __init__(self, points_list, size):
        """
        The class gets a points list and build SameAreaCell upon it with the specified cell size
        :param points_list:
        """
        # Number of cell in each dimension
        self.size_cell = size
        self.x_min = min(points_list, key=itemgetter(0))[0]
        self.y_min = min(points_list, key=itemgetter(1))[1]
        self.x_max = max(points_list, key=itemgetter(0))[0]
        self.y_max = max(points_list, key=itemgetter(1))[1]

        n_y = int((self.y_max - self.y_min) / self.size_cell) + 1
        n_x = int((self.x_max - self.x_min) / self.size_cell) + 1
        self.data_set = [
            [Cell(self.x_min + ii * self.size_cell, self.y_min + j * self.size_cell, self.size_cell, ii, j) for ii in
             range(n_x)] for j in range(n_y)]

    def add_point(self, pnt: PolygonPoint):

        in_x = int((pnt.x - self.x_min) / self.size_cell)
        in_y = int((pnt.y - self.y_min) / self.size_cell)
        self.data_set[in_y][in_x].points.append(pnt)

    def find_cell(self, pnt):
        in_x = int((pnt.x - self.x_min) / self.size_cell)
        in_y = int((pnt.y - self.y_min) / self.size_cell)
        return in_x, in_y

    def create_grid_shapefile(self):
        # Create the grid layer
        # vector_grid = QgsVectorLayer('Polygon?crs=' + crs, 'vector_grid', 'memory')
        path = os.getcwd() + "/test/new_test/grid.shp"
        if os.path.exists(path):
            print(path)
        else:
            print("path not exist - {}".format(path))
            return
        vector_grid = QgsVectorLayer(path, "grid", "ogr")
        vector_grid.dataProvider().truncate()
        prov = vector_grid.dataProvider()

        # Add ids and coordinates fields
        if vector_grid.fields()[-1].name() != 'num_of_pnt':
            fields = QgsFields()
            fields.append(QgsField('id_east', QVariant.Int, '', 20, 0))
            fields.append(QgsField('id_north', QVariant.Int, '', 20, 0))
            fields.append(QgsField('num_of_pnt', QVariant.Int, '', 20, 0))
            prov.addAttributes(fields)
        my_id = 0
        for cell_row in self.data_set:
            for cell in cell_row:
                feat = QgsFeature()
                feat.setGeometry(
                    QgsGeometry().fromPolygonXY([list(cell.extent.values())]))  # Set geometry for the current id
                print(list(cell.extent.values()))
                feat.setAttributes([my_id, cell.i_e, cell.i_n, len(cell.points)])  # Set attributes for the current id
                print('{},{} :{}'.format(cell.i_e, cell.i_n, len(cell.points)))
                prov.addFeatures([feat])
                my_id += 1
        # Update fields for the vector grid
        vector_grid.updateFields()


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
    QgsApplication.initQgis()

    input_constrains = 'work_folder/general/constrains.shp'
    input_in = 'work_folder/general/intersections.shp'

    input_layers = [upload_new_layer(input_constrains, 'file'), upload_new_layer(input_in, 'file')]

    # Get  the layers' rectangle extent
    rectangle_points = []
    for input_layer in input_layers:
        extent = input_layer.extent()
        rectangle_points.append((extent.xMaximum(), extent.yMaximum()))
        rectangle_points.append((extent.xMinimum(), extent.yMinimum()))

    # Build SameAreaCell object
    geo_data_base = SameAreaCell(rectangle_points, 100)

    # Build an grid layer (test)
    # test_same_area_grid([geo_data_base.x_min, geo_data_base.x_max, geo_data_base.y_min, geo_data_base.y_max],
    #                     geo_data_base.size_cell)

    # Print the points polygon
    for feature in input_layers[0].getFeatures():
        feature_list = feature.geometry().asJson()
        attribute = feature.attributes()[0]
        json1_data = json.loads(feature_list)['coordinates']
        cor_sets = json1_data[0]
        # Next row is for adding the line equations for the previous and next points latter
        for cor_set in cor_sets:
            len_list_no_last = len(cor_set) - 1
            geo_data_base.add_point(PolygonPoint(pnt=cor_set[0], nxt_pnt=cor_set[1]))
            for i in range(0, len_list_no_last):
                if i != 0:
                    if i == len_list_no_last - 1:
                        second_point.nexr_pnt = cor_set[0]
                    second_point.nexr_pnt(cor_set[i + 1])
                    geo_data_base.add_point(second_point)
                second_point = PolygonPoint(pnt=cor_set[i + 1], pre_pnt=cor_set[i])

                # elif i == len_list_no_last:
                #     pass

    # geo_data_base.create_grid_shapefile()
    """For standalone application"""
    # Exit applications
    QgsApplication.exitQgis()
    app.exit()
