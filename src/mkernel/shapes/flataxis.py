from .base import NongeoShape



class FlatAxis(NongeoShape):
    def __init__(self, renderer, model):
        self.__vrtx_block = renderer.vbo.cache.request_block(size=4)
        self.__indx_block = renderer.ibo.cache.request_block(size=4)
        self.__indx_block['idx'] = self.__vrtx_block.indices
        self.__vrtx_block['pos'] = (-1, -1), (1, -1), (1, 1), (-1, 1)

        # pixel thickness
        self.__thk = self.thk = 5

    @property
    def thk(self):
        return self.__thk

    @thk.setter
    def thk(self, v):
        self.__thk = v
        self.__vrtx_block['thk'] = v

    def draw_at(self, ray):
        self.__vrtx_block['ori'] = ray.origin.T
        self.__vrtx_block['dir'] = ray.as_vec().T

    def delete(self):
        raise NotImplementedError

"""

def intersect_ray_pln(self, ray, pln):
    rori = ray.origin
    pori = pln.origin

    rvec = ray.as_vec()
    pnormal = pln.axis_z
    t = gt.Vec.dot(pnormal, pori - rori) / gt.Vec.dot(pnormal, rvec)
    return rori + t * rvec
        
if coord != (.5, .5, .5):
    # find eye
    cam = self.devices.cameras[0]
    vm = cam.tripod.VM
    eye = gt.Pnt(0, 0, cam.body.near)
    pln = gt.Pln.from_ori_axies(gt.Pnt(*coord), gt.XVec(), gt.YVec(), gt.ZVec())    # plane mouse pointing at

    # plane normal pointing at the camera
    picked_pnt = gt.Pnt(*coord)
    new_normal = cam.tripod.plane.axis_z
    axis_z = gt.Vec.cross(pln.axis_x, new_normal)
    axis_y = gt.Vec.cross(axis_z, pln.axis_x)
    facing_pln = gt.Pln.from_ori_axies(pln.origin, pln.axis_x, axis_y, axis_z)
    self.ref_pln.geo = facing_pln
    facing_pln = vm * facing_pln

    # find covering flat line
    l, r, b, t, n, f = cam.body.dim
    dia = max(r - l, t - b)
    flat_p = self.intersect_ray_pln(gt.Ray.from_pnts(eye, facing_pln.origin), gt.Pln())
    flat_pt = self.intersect_ray_pln(gt.Ray.from_pnt_vec(facing_pln.origin, facing_pln.axis_x), gt.Pln())
    flat_v = (flat_pt - flat_p).normalize()
    t = gt.Vec.dot(flat_v, gt.Pnt(0, 0, 0) - flat_p)
    closest_pnt = flat_p + t * flat_v

    p0 = closest_pnt - flat_v.amplify(dia)
    p1 = closest_pnt + flat_v.amplify(dia)
    # normal for thickness 10
    ht = 0.001 # half thickness
    n = closest_pnt.as_vec().amplify(ht)

    # rectangle line covering whole screen
    vrtxs = p0 + n, p0 - n, p1 + n, p1 - n

    # find world space intersection
    wcs_vrtxs = []
    for vrtx in vrtxs:
        # ray = gt.Ray.from_pnts(eye, vrtx)
        # intx_pnt = self.intersect_ray_pln(ray, facing_pln)
        wcs_vrtxs.append(vm.I * (vrtx-gt.Vec(0, 0, 10)))
    # print(wcs_vrtxs)
    a = 0.2
    # self.axis0.geo = gt.Lin.from_pnts(vm.I * (p0+gt.Vec(0, 0, a)), vm.I * (p1 + gt.Vec(0, 0, a)))
    # self.axis0.geo = gt.Lin.from_pnts(p0, p1)
    ps = [vm.I * (p - gt.Vec(0, 0, 6)) for p in (p0, p1)]
    self.axis0.geo = gt.Lin.from_pnts(*ps)
"""