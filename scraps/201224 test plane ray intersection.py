import mkernel.shapes.simple.primitive_wrapper as w

p = w.Pln((0,0,0), (1,0,0), (0,1,0), (0,0,1))
a = w.Pnt(0,0,0)
b = w.Pnt(10,10,0)

r = w.Ray((10,10,10), (0,0,-1))
k= w.Pnt
print(type(k(0,0,0)))
# print(p.intersect(r))
print(a, type(a))
print(r, type(r))
print(p, type(p))
print(a)
print(a.intersect(r))
print(b.intersect(r))