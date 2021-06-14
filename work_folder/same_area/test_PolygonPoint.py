from shapely.geometry import Point


class PolygonPoint:
    def __init__(self, pnt):
        self.pnt = pnt
        self.pre = ''
        self.next = ''


if __name__ == '__main__':
    array = [7, 4, 3, 8, 2, 1, 7]
    first = PolygonPoint(array[0])
    nxt = PolygonPoint(array[1])