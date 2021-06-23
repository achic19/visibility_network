from shapely.geometry import Point


class LineParameters:
    def __init__(self, p1: Point, p2: Point):
        """
        It creates slope object using two points coordinates (:param p1 and :param p2)
        """
        self.slope = (p2.y - p1.y) / (p2.x - p1.x)
        self.intersect = p1.y - p1.x * self.slope

    def __repr__(self):
        return "the slope is: {:.2f}, intersect is: {:.2f}".format(self.slope, self.intersect)


class PolygonPoint:
    def __init__(self, pnt: list):
        """
        The PolygonPoint class object contains the current point (:param pnt)
        and the lines connecting it to the adjacent points
        in  the  polygon ( another two PolygonPoint point and line parameters)
        """
        self.pnt = Point(pnt[0], pnt[1])
        self.nxt = None
        self.pre = None

        self.nxt_line_params = None
        self.pre_line_params = None

    def __repr__(self):
        if self.nxt is not None and self.pre is not None:
            return "point {}: previous  point is: {}, next point is:{}\n".format(self.pnt, self.pre.pnt,
                                                                                 self.nxt.pnt)
        else:
            return "point {}\n".format(self.pnt)


if __name__ == '__main__':
    my_polygon = [[7, 12], [4, 12], [7, 3], [12, 8], [2, 2], [0, 8], [7, 12]]
    print(my_polygon)
    new_list = []
    # Create two PolygonPoint objects from the the first two Points in the polygon
    fst_pnt = PolygonPoint(my_polygon[0])
    nxt_pnt = PolygonPoint(my_polygon[1])
    # update the next point of the first PolygonPoint object and put it the new database
    fst_pnt.nxt = nxt_pnt
    new_list.append(fst_pnt)
    pre_pnt = fst_pnt
    for i in range(1, len(my_polygon) - 2):
        # this loop creates new PolygonPoint object (the next index) and update all rest
        # points of the current  PolygonPoint object (the current index)
        # than put it into the database and update the temp variables for the next loop
        new_pnt = PolygonPoint(my_polygon[i + 1])
        nxt_pnt.nxt = new_pnt
        nxt_pnt.pre = pre_pnt
        new_list.append(nxt_pnt)
        pre_pnt = nxt_pnt
        nxt_pnt = new_pnt

    # operation for the last point in the polygon
    nxt_pnt.pre = pre_pnt
    nxt_pnt.nxt = fst_pnt
    new_list.append(nxt_pnt)
    fst_pnt.pre = nxt_pnt
    print(new_list)

    for temp_pnt in new_list:
        # Update the line parameters for the current point as well as the connected points
        if temp_pnt.pre_line_params is None:
            temp_pnt.pre_line_params = LineParameters(temp_pnt.pnt, temp_pnt.pre.pnt)
            temp_pnt.pre.nxt_line_params = temp_pnt.pre_line_params
        if temp_pnt.nxt_line_params is None:
            temp_pnt.nxt_line_params = LineParameters(temp_pnt.pnt, temp_pnt.nxt.pnt)
            temp_pnt.nxt.pre_line_params = temp_pnt.nxt_line_params
    for temp_pnt in new_list:
        print(temp_pnt.pre_line_params)
        print(temp_pnt.nxt_line_params)
        print(temp_pnt)
