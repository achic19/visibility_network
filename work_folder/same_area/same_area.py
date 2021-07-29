# Tell Python where you will get processing from
import json
import os
import sys
import math
from operator import itemgetter

from PyQt5.QtGui import *
# from test_same_area.test_same_area import test_same_area_grid
from qgis.PyQt.QtCore import QVariant
from qgis.core import *
from shapely.geometry import Point
from PolygonPoint import PolygonPoint
from sym_matrix import *
from is_intersect import *

sys.path.append(r'C:\Program Files\QGIS 3.0\apps\qgis\python\plugins')


class Cell:
    def __init__(self, x, y, spacing, i_x, i_y):
        """
        :param x:
        :param y:
        :param spacing: size cell
        :param i_x: cell index in x direction
        :param i_y: cell index in y direction
        """
        self.points = []
        self.extent = {'SW': QgsPointXY(x, y), 'SE': QgsPointXY(x + spacing, y),
                       'NE': QgsPointXY(x + spacing, y + spacing), 'NW': QgsPointXY(x, y + spacing)}
        self.i_e = i_x
        self.i_n = i_y

    def __iter__(self):
        return iter(self.points)


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
        self.num_of_pnt = 0
        n_y = int((self.y_max - self.y_min) / self.size_cell) + 1
        n_x = int((self.x_max - self.x_min) / self.size_cell) + 1
        self.data_set = [
            [Cell(self.x_min + ii * self.size_cell, self.y_min + j * self.size_cell, self.size_cell, ii, j) for j in
             range(n_y)] for ii in range(n_x)]

    def __getitem__(self, inds: list):
        """
        :param inds: tuple of indices
        :return: a cell from the dataset based on the indices
        """
        return self.data_set[inds[0]][inds[1]]

    # this method increments the number of points in our database by 1
    def increment_num_pnts(self):
        self.num_of_pnt += 1
        return self.num_of_pnt

    def add_point(self, pnt: PolygonPoint):
        in_x = int((pnt.x - self.x_min) / self.size_cell)
        in_y = int((pnt.y - self.y_min) / self.size_cell)
        self.data_set[in_x][in_y].points.append(pnt)

    def find_cell(self, pnt: Point):
        in_x = int((pnt.x - self.x_min) / self.size_cell)
        in_y = int((pnt.y - self.y_min) / self.size_cell)
        return [in_x, in_y]

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


class FindSightLine:
    def __init__(self, start_line: Point, end_line: Point, cur_cell: list, end_cell: list, data_base: SameAreaCell,
                 num_of_pnts: int):
        """
        It checks and builds a sight line between two points
        :param start_line:
        :param end_line:
        :param cur_cell:
        :param end_cell:
        :param data_base:
        :param num_of_pnts:
        """
        # ToDo - tart_line  end_line cur_cell end_cell data_base sys_matrix azi_line should be private
        self.start_line = start_line
        self.end_line = end_line
        self.cur_cell = cur_cell
        self.end_cell = end_cell
        self.data_base = data_base
        self.is_sight_line = True
        # s_matrix is a  symarray which allow me to update line both directions
        self.sys_matrix = symarray(numpy.zeros((num_of_pnts, num_of_pnts)))
        self.azi_line = azimuth_calculator(self.start_line, self.end_line)
        # If the current line intersects polygon lines, this line is not sight line
        if self.calculate_intersections():
            self.is_sight_line = False
        elif cell_first == cell_end:
            pass
        # if the points have the same index horizontally or vertically
        elif cell_first[0] == cell_end[0]:
            if cell_first[1] > cell_end[1]:
                self.loop_over_horizontal_vertical_cells(1, -1)
            else:
                self.loop_over_horizontal_vertical_cells(1, 1)
        elif cell_first[1] == cell_end[1]:
            if cell_first[0] > cell_end[0]:
                self.loop_over_horizontal_vertical_cells(0, -1)
            else:
                self.loop_over_horizontal_vertical_cells(0, 1)
        else:
            # A pivot variable is a dictionary.
            # {pointer to the one of the cell corners:
            # [optional next cell: the examined azimuth is smaller/same/larger]}
            if 0 < self.azi_line < 90:
                self.pivot = {'NE': [(0, 1), (1, 1), (1, 0)]}
            elif 90 < self.azi_line < 180:
                self.pivot = {'SE': [(1, 0), (1, -1), (0, -1)]}
            elif 180 < self.azi_line < 270:
                self.pivot = {'SW': [(0, -1), (-1, -1), (-1, 0)]}
            else:
                self.pivot = {'NW': [(-1, 0), (-1, 1), (0, 1)]}
            self.pivot_list = list(self.pivot.values())
            self.loop_over_cell_with_pivot()

    def loop_over_horizontal_vertical_cells(self, dir_ind: int, step: int):
        """
        Loop over cells horizontally or vertically (based on  @dir_ind) from first cell to destination cell
        :param dir_ind:
        :param step forward in the grid(+1) or backward(-1)
        :return:
        """
        while not self.cur_cell == self.end_cell:
            self.cur_cell[dir_ind] += step
            if self.calculate_intersections():
                self.is_sight_line = False
                break

    def loop_over_cell_with_pivot(self):
        """
        It loops over points in the cells from the cell of the current point to the destination cell through the cells
        that are selected based on the direction in the pivot dictionary and the line azimuth.
        :return:
        """
        key = list(self.pivot.keys())[0]
        pivot_point = self.data_base[self.cur_cell].extent[key]
        ex_az = azimuth_calculator(self.start_line, Point(pivot_point))

        if ex_az < self.azi_line:
            self.find_next_cell(self.pivot_list[0][2])

        elif ex_az == self.azi_line:
            self.find_next_cell(self.pivot_list[0][1])
        else:
            try:
                self.find_next_cell(self.pivot_list[0][0])
            except:
                pass
        # calculate_intersection
        if self.calculate_intersections():
            self.is_sight_line = False
            return
        # the next step (if the two cells are not the same check the next cell)
        if self.cur_cell == self.end_cell:
            return
        else:
            self.loop_over_cell_with_pivot()

    def find_next_cell(self, values: tuple):
        """
        find the next cell according to the specified values
        :param values: it added to the current cell to find the next cell
        :return:
        """

        self.cur_cell[0] += values[0]
        self.cur_cell[1] += values[1]

    def calculate_intersections(self):
        """
        It goes over all the points in the current cell and search for intersection between each pair of points and the
        optional sight line
        :return:
        """
        cur_cell = self.data_base[self.cur_cell]
        for point in cur_cell:
            if self.two_lines_intersection(point, point.nxt) or self.two_lines_intersection(point, point.pre):
                return True
        return False

    def two_lines_intersection(self, pnt1: PolygonPoint, pnt2: PolygonPoint):
        """
        It checks if two lines intersect when it hasn't been checked before
        :return:
        """
        if self.sys_matrix[pnt1.id, pnt2.id] == 0:
            if doIntersect(self.start_line, self.end_line, pnt1, pnt2):
                return True
            else:
                self.sys_matrix[pnt1.id, pnt2.id] = 1


def upload_new_layer(path, name):
    """Upload shp layers"""
    layer_name = "layer" + name
    provider_name = "ogr"
    layer = QgsVectorLayer(
        path,
        layer_name,
        provider_name)
    return layer


def azimuth_calculator(pnt1: Point, pnt2: Point) -> float:
    """
    Calculate and return azimuth by two points
    :param pnt1:
    :param pnt2:
    :return:
    """
    azimuth = math.degrees(math.atan2(pnt2.x - pnt1.x, pnt2.y - pnt1.y))
    if azimuth < 0:
        azimuth += 360
    return azimuth


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
    a = symarray(numpy.zeros((3, 3)))
    # Index that is point ID
    index_id = 0

    for feature in input_layers[0].getFeatures():
        feature_list = feature.geometry().asJson()
        attribute = feature.attributes()[0]
        json1_data = json.loads(feature_list)['coordinates']
        for part in json1_data:
            # Create two PolygonPoint objects from the the first two Points in the polygon
            sub_part = part[0]
            index_id += len(sub_part)
            fst_pnt = PolygonPoint(geo_data_base.increment_num_pnts(), sub_part[0])
            nxt_pnt = PolygonPoint(geo_data_base.increment_num_pnts(), sub_part[1])
            # update the next point of the first PolygonPoint object and put it the new database
            fst_pnt.nxt = nxt_pnt
            geo_data_base.add_point(fst_pnt)
            pre_pnt = fst_pnt
            for i in range(1, len(sub_part) - 2):
                # this loop creates new PolygonPoint object (the next index) and update all rest
                # points of the current  PolygonPoint object (the current index)
                # than put it into the database and update the temp variables for the next loop
                new_pnt = PolygonPoint(geo_data_base.increment_num_pnts(), sub_part[i + 1])
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
    # calculate sight line
    # First, upload the gis file to remove old sight lines and make it ready for new sight lines
    path = "sight_line.shp"
    vector_grid = QgsVectorLayer(path, "sight_line", "ogr")
    vector_grid.dataProvider().truncate()
    data_provider = vector_grid.dataProvider()
    # In this list all the new features (sight lines) will be stored
    feats = []
    inter_pnt_list = [Point(feature.geometry().asPoint()) for feature in input_layers[1].getFeatures()]
    # save the cell location of each point in another array
    inter_cell_list = [(geo_data_base.find_cell(feature)) for feature in inter_pnt_list]

    # Code for performance:
    my_time = 0
    n = len(inter_pnt_list)
    run_max = (n * (n + 1)) / 2
    print(run_max)
    for index_i, point_start in enumerate(inter_pnt_list[:-1]):
        print(index_i)
        index_j = index_i
        for point_end in inter_pnt_list[index_i + 1:]:
            my_time += 1
            print("Progress {:3.2%}".format(my_time / run_max))
            cell_first = inter_cell_list[index_i].copy()
            index_j += 1
            print(index_j)
            # if the two points are the same
            if point_start == point_end:
                continue
            # Call to FindSightLine class to check if sight line is exist

            cell_end = inter_cell_list[index_j]
            if FindSightLine(point_start, point_end, cell_first, cell_end, geo_data_base, index_id).is_sight_line:
                feat = QgsFeature()
                feat.setGeometry(
                    QgsGeometry().fromPolylineXY([QgsPointXY(point_start.x, point_start.y), QgsPointXY(point_end.x,
                                                                                                       point_end.y)]))
                feat.setAttributes([1, 2, 3])  # Set attributes for the current id
                feats.append(feat)

    data_provider.addFeatures(feats)
    # Update fields for the vector grid
    vector_grid.updateFields()

    # create line for other points in the list
    """For standalone application"""
    # Exit applications
    QgsApplication.exitQgis()
    app.exit()
