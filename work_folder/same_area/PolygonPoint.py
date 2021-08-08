from shapely.geometry import Point



class PolygonPoint(Point):
    def __init__(self, id_local: int, pnt: list):
        """
        The PolygonPoint class object contains the current point (:param pnt)
        and the lines connecting it to the adjacent points
        in  the  polygon ( another two PolygonPoint point)
        """
        self.id = id_local
        Point.__init__(self, pnt[0], pnt[1])
        self.nxt = None
        self.pre = None



if __name__ == '__main__':
    my_polygon = [[7, 12], [4, 12], [7, 3], [12, 8], [2, 2], [0, 8], [7, 12]]
    print(my_polygon)
    new_list = []
    # Create two PolygonPoint objects from the the first two Points in the polygon
    fst_pnt = PolygonPoint(0, my_polygon[0])
    nxt_pnt = PolygonPoint(1, my_polygon[1])
    # update the next point of the first PolygonPoint object and put it the new database
    fst_pnt.nxt = nxt_pnt
    new_list.append(fst_pnt)
    pre_pnt = fst_pnt
    for i in range(1, len(my_polygon) - 2):
        # this loop creates new PolygonPoint object (the next index) and update all rest
        # points of the current  PolygonPoint object (the current index)
        # than put it into the database and update the temp variables for the next loop
        new_pnt = PolygonPoint(i, my_polygon[i + 1])
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

