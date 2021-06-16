from shapely.geometry import Point


class Slope:
    def __init__(self, p1: Point, p2: Point):
        self.slope = (p2.y - p1.y) / (p2.x - p1.x)
        self.intersect = p1.y - p1.x * self.slope

    def __repr__(self):
        return "the slope is: {:.2f}, intersect is: {:.2f}".format(self.slope, self.intersect)


class PolygonPoint:
    def __init__(self, pnt):
        self.pnt = pnt
        self.nxt = None
        self.pre = None

        self.nxt_slp = None
        self.pre_slp = None

    def __repr__(self):
        if self.nxt is not None:
            return "point {}: previous  point is: {}, next point is:{}\n".format(self.pnt, self.pre.pnt,
                                                                                 self.nxt.pnt)
        else:
            return "point {}: previous  point is: {}, next point is:{}\n".format(self.pnt, self.pre, self.nxt)


if __name__ == '__main__':
    my_polygon = [Point(7, 12), Point(4, 12), Point(7, 3), Point(12, 8), Point(2, 2), Point(0, 8), Point(7, 12)]
    print(my_polygon)
    new_list = []
    fst_pnt = PolygonPoint(my_polygon[0])
    nxt_pnt = PolygonPoint(my_polygon[1])
    fst_pnt.nxt = nxt_pnt
    new_list.append(fst_pnt)
    pre_pnt = fst_pnt
    for i in range(1, len(my_polygon) - 2):
        new_pnt = PolygonPoint(my_polygon[i + 1])
        nxt_pnt.nxt = new_pnt
        nxt_pnt.pre = pre_pnt
        new_list.append(nxt_pnt)
        pre_pnt = nxt_pnt
        nxt_pnt = new_pnt

    nxt_pnt.pre = pre_pnt
    nxt_pnt.nxt = fst_pnt
    new_list.append(nxt_pnt)
    fst_pnt.pre = nxt_pnt
    print(new_list)
    for temp_pnt in new_list:
        if temp_pnt.pre_slp is None:
            temp_pnt.pre_slp = Slope(temp_pnt.pnt, temp_pnt.pre.pnt)
            temp_pnt.pre.nxt_slp = temp_pnt.pre_slp
        if temp_pnt.nxt_slp is None:
            temp_pnt.nxt_slp = Slope(temp_pnt.pnt, temp_pnt.nxt.pnt)
            temp_pnt.nxt.pre_slp = temp_pnt.nxt_slp
    for temp_pnt in new_list:
        print(temp_pnt.pre_slp)
        print(temp_pnt.nxt_slp)
        print(temp_pnt)

