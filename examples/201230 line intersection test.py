from gkernel.dtype.geometric.primitive import *
from numpy import inf


def test_intx(pnt_s, pnt_e, ray_o, ray_n):
    line = Lin.from_pnts(pnt_s, pnt_e)
    ray = Ray.from_pnt_vec(ray_o, ray_n)

    intx = line.intx_ray(ray)
    if intx is None:
        print('intersection yield no result')
    elif isinstance(intx, Lin):
        print(f"intersection yield a line {intx} and is the line {intx == line}")
    else:
        # compare vectors to check result
        vec_to_p = Vec.from_pnts(ray_o, intx).normalize()
        ray_norm = ray_n.normalize()
        print(f"intersecting at {intx}")
        print(f"vector correct? {vec_to_p == ray_norm}")
    print()

print('TESTS ON XY(2D) PLANE:')
ps, pe, ro = Pnt(0, 0, 0), Pnt(12, 0, 0), Pnt(0, 6, 0)
print('test: ray crossing middle of axis line')
test_intx(ps, pe, ro, Vec(1, -1, 0))
print('test: ray crossing start of line')
test_intx(ps, pe, ro, Vec(0, -1, 0))
print('test: ray crossing end of line')
test_intx(ps, pe, ro, Vec(2, -1, 0))
print('test: ray directing to the line but over parameter')
test_intx(ps, pe, ro, Vec(10, -1, 0))
print('test: ray directing to the line but under parameter')
test_intx(ps, pe, ro, Vec(-1, -1, 0))
print('test: ray not directing to the line')
test_intx(ps, pe, ro, Vec(1, 1, 0))
print('test: ray parallel to the line and not crossing')
test_intx(ps, pe, ro, Vec(1, 0, 0))
print('test: ray parallel opposite to the line and not crossing')
test_intx(ps, pe, ro, Vec(-1, 0, 0))

print()
print('TEST ON 1D(LINE ON RAY):')
ps, pe, rn = Pnt(0, 0, 0), Pnt(20, 10, 0), Vec(2, 1, 0)
print('test: ray collinear with line and directions equal')
test_intx(ps, pe, ps, rn)
test_intx(ps, pe, pe, -rn)
print('test: ray starts on the line but directions do not follow line')
test_intx(ps, pe, ps, Vec(0, 1, 0))
test_intx(ps, pe, pe, Vec(0, 1, 0))
print('test: ray collinear with line and ray starts outside')
test_intx(ps, pe, ps + rn*-100, rn)
test_intx(ps, pe, ps + rn*100, -rn)
print('test: ray starts at third of line')
test_intx(ps, pe, ps + Vec.from_pnts(ps, pe) / 3, rn)
test_intx(ps, pe, ps + Vec.from_pnts(ps, pe) / 3, -rn)

print()
print('TEST ON 3D USING SIMPLE CUBE:')
ps, pe, ro = Pnt(0, 0, 0), Pnt(0, 10, 10), Pnt(10, 0, 0)
print('test: ray intersecting middle of the line on yz plane')
test_intx(ps, pe, ro, Vec.from_pnts(ro, Lin.from_pnts(ps, pe).pnt_at(0.5)))
print('test: ray missing middle of the line')
test_intx(ps, pe, ro, Vec.from_pnts(ro, Lin.from_pnts(ps, pe).pnt_at(0.5)) + Vec(z=1))
print('test: ray missing middle of the line but pointing at the line')
test_intx(ps, pe, ro, Vec.from_pnts(ro, Lin.from_pnts(ps, pe).pnt_at(4))/5)

