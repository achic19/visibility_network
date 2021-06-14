class PolygonPoint:
    def __init__(self, pnt):
        self.pnt = pnt
        self.nxt = ''
        self.pre = ''

    def __repr__(self):
        return "point {}: previous  point is: {}, next point is:{}\n".format(self.pnt, self.pre.pnt, self.nxt.pnt)


if __name__ == '__main__':
    my_polygon = [7, 4, 3, 8, 2, 1, 7]
    print(my_polygon)
    new_list = []
    fst_pnt = PolygonPoint(my_polygon[0])
    nxt_pnt = PolygonPoint(my_polygon[1])
    fst_pnt.nxt = nxt_pnt
    new_list.append(fst_pnt)
    pre_pnt = fst_pnt
    for i in range(len(my_polygon) - 2):
        new_pnt = PolygonPoint(my_polygon[i + 1])
        nxt_pnt.nxt = new_pnt
        nxt_pnt.pre = pre_pnt
        new_list.append(nxt_pnt)
        pre_pnt = nxt_pnt
        nxt_pnt = new_pnt

    nxt_pnt.nxt = fst_pnt
    fst_pnt.pre = nxt_pnt
    nxt_pnt.pre = pre_pnt
    print(new_list)
