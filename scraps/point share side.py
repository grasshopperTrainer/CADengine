import gkernel.dtype.geometric as gt


l = gt.Lin([0, 0, 0], [10, 0, 0])
print(l.pnts_share_side(gt.Pnt(10, 10, 10), gt.Pnt(-10, -10, 0)))
print(l.pnts_share_side(gt.Pnt(10, 10, 10), gt.Pnt(-10, 10, 0)))
print(l.pnts_share_side(gt.Pnt(10, 10, 10), gt.Pnt(-10, 0, 0)))