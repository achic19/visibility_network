# Tell Python where you will get processing from
import json
import os
import sys
from operator import itemgetter

from PyQt5.QtGui import *
# from test_same_area.test_same_area import test_same_area_grid
from qgis.PyQt.QtCore import QVariant
from qgis.core import *
from shapely.geometry import Point
from PolygonPoint import PolygonPoint, LineParameters

sys.path.append(r'C:\Program Files\QGIS 3.0\apps\qgis\python\plugins')


class Cell:
    def __init__(self, x, y, spacing, i_x, i_y):
        self.points = []
        self.extent = {'SW': QgsPointXY(x, y), 'SE': QgsPointXY(x + spacing, y),
                       'NE': QgsPointXY(x + spacing, y + spacing), 'NW': QgsPointXY(x, y + spacing)}
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
        in_x = int((pnt.pnt.x - self.x_min) / self.size_cell)
        in_y = int((pnt.pnt.y - self.y_min) / self.size_cell)
        self.data_set[in_y][in_x].points.append(pnt)

    def find_cell(self, pnt):
        in_x = int((pnt.x - self.x_min) / self.size_cell)
        in_y = int((pnt.y - self.y_min) / self.size_cell)
        return in_x, in_y

    def create_grid_shapefile(self):
        # Create the grid layer
        # vector_grid = QgsVectorLayer('Polygon?crs=' + crs, 'vector_grid', 'memory')
        path = "test_same_area/grid.shp"
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

    # This code is contributed by ash264


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

    # input_constrains = 'test_same_area/multiparts.shp'
    input_constrains = 'constrains.shp'
    input_in = 'intersections.shp'

    input_layers = [upload_new_layer(input_constrains, 'file'), upload_new_layer(input_in, 'file')]

    # Get  the layers' rectangle extent
    rectangle_points = []
    for input_layer in input_layers:
        extent = input_layer.extent()
        rectangle_points.append((extent.xMaximum(), extent.yMaximum()))
        rectangle_points.append((extent.xMinimum(), extent.yMinimum()))

    # Build SameAreaCell object
    geo_data_base = SameAreaCell(rectangle_points, 100)

    # Print the points polygon
    for feature in input_layers[0].getFeatures():
        feature_list = feature.geometry().asJson()
        attribute = feature.attributes()[0]
        json1_data = json.loads(feature_list)['coordinates']
        for part in json1_data:
            # Create two PolygonPoint objects from the the first two Points in the polygon
            sub_part = part[0]
            fst_pnt = PolygonPoint(sub_part[0])
            nxt_pnt = PolygonPoint(sub_part[1])
            # update the next point of the first PolygonPoint object and put it the new database
            fst_pnt.nxt = nxt_pnt
            geo_data_base.add_point(fst_pnt)
            pre_pnt = fst_pnt
            for i in range(1, len(sub_part) - 2):
                # this loop creates new PolygonPoint object (the next index) and update all rest
                # points of the current  PolygonPoint object (the current index)
                # than put it into the database and update the temp variables for the next loop
                new_pnt = PolygonPoint(sub_part[i + 1])
                nxt_pnt.nxt = new_pnt
                nxt_pnt.pre = pre_pnt
                geo_data_base.add_point(nxt_pnt)
                pre_pnt = nxt_pnt
                nxt_pnt = new_pnt

            # operation for the last point in the polygon
            nxt_pnt.pre = pre_pnt
            nxt_pnt.nxt = fst_pnt
            geo_data_base.add_point(nxt_pnt)
            fst_pnt.pre = nxt_pnt

    # geo_data_base.create_grid_shapefile()
    inter_pnt_list = [feature.geometry().asPoint() for feature in input_layers[1].getFeatures()]
    # for index_i, feature in enumerate inter_pnts:
    #     pass
    # for each point in the @input_in
    # create line for other points in the list
    """For standalone application"""
    # Exit applications
    QgsApplication.exitQgis()
    app.exit()
