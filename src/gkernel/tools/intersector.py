from warnings import warn

from ..dtype.geometric.primitive import *


class Intersector:
    """
    for example, in case of intersecting ray and plane, where the method should be?
    inside `Pln` or inside `Ray`? That is why this class is created.
    """

    def __new__(cls):
        """
        ignore instance creation
        """
        warn("no instance for `Intersector`")
        return cls

    @classmethod
    def intx(cls, a, b):
        """
        intersect two objects and return result

        :param a: object a
        :param b: object b
        :return:
        """
        # find single concrete intersection method
        cls_names = [a.__class__.__name__, b.__class__.__name__]
        method_name = '_Intersector__' + '_'.join(cls_names)
        if hasattr(cls, method_name):
            return getattr(cls, method_name)(a, b)
        else:
            method_name = '_Intersector__' + '_'.join(reversed(cls_names))
            if hasattr(cls, method_name):
                return getattr(cls, method_name)(b, a)
        raise NotImplementedError("intersection between given class is not implemented")

    @classmethod
    def __Ray_Pln(cls, ray, plane):
        """
        ray plane intersection

        referenced from Scratchapixel 2.0 :
        https://www.scratchapixel.com/lessons/3d-basic-rendering/minimal-ray-tracer-rendering-simple-shapes/ray-plane-and-ray-disk-intersection

        :param ray: to intersect with
        :return: Pnt if intersects else None
        """
        # 0 dot means perpendicular and
        # ray perpendicular plane normal means they are parallel
        plane_normal = plane.axis_z
        ray_normal = ray.normal
        denom = Vec.dot(plane_normal, ray_normal)
        if abs(denom) < ATOL:  # check if value is 0
            return None
        # if not ray is not parallel with plane
        # check if ray is pointing at plane, not away
        ray_to_origin = plane.origin - ray.origin
        # scalar distance describing intersection point from ray origin
        dist = Vec.dot(plane_normal, ray_to_origin) / denom
        if dist >= 0:
            return ray.origin + ray_normal.amplify(dist)
        else:
            return None

    @classmethod
    def __Ray_Tgl(cls, ray, tgl):
        """
        intersection between ray and triangle

        implementing Moller-Trumbore algorithm
        reference: https://www.scratchapixel.com/lessons/3d-basic-rendering/ray-tracing-rendering-a-triangle/why-are-triangles-useful
        :param ray:
        :param tgl:
        :return:
        """
        (v0, v1, v2), tn = tgl.vertices, tgl.normal
        ray_o, ray_v = ray.origin, ray.normal
        A = v1 - v0
        B = v2 - v0

        pvec = Vec.cross(ray_v, B)
        det = Vec.dot(A, pvec)

        heading = Vec.dot(tn, ray_o - v0)   # to disable culling
        # print(heading, det)
        if heading == 0 and Vec.dot(ray_v, tn) == 0:    # check if ray is on the plane
            raise NotImplementedError("ray on triangle plane")
        # zero heading means ray touching the triangle plane
        if not(0 < det and 0 <= heading or det < 0 and heading <= 0):
            return None
        if -ATOL < det < ATOL:
            # what if ray is on the plane
            # and crosses the triangle drawing intersection as a line?
            if tgl.pln.pnt_is_on(ray_o):
                raise NotImplementedError
            else:   # else line parallel to the plane and do not intersect
                return None

        inv_det = 1 / det

        tvec = ray_o - v0
        u = Vec.dot(tvec, pvec) * inv_det
        if u < 0 or 1 < u:
            return None

        qvec = Vec.cross(tvec, A)
        v = Vec.dot(ray_v, qvec) * inv_det
        if v < 0 or 1 < v + u:
            return None

        t = Vec.dot(B, qvec) * inv_det

        return ray_o + ray_v * t

    @classmethod
    def __Ray_Pnt(cls, ray, pnt):
        """
        ray point intersection

        :param ray: ray to intersect with
        :return: self as an intersection point else None
        """
        # 0 cross product means parallel
        ray_to_pnt = pnt - ray.origin
        if Vec.cross(ray.normal, ray_to_pnt).is_zero():
            return pnt
        else:
            return None

    @classmethod
    def __Ray_Lin(self, ray):
        """
        ray line intersection

        refer to: https://stackoverflow.com/questions/563198/how-do-you-detect-where-two-line-segments-intersect/565282#565282

        :param ray: ray to intersect with
        :return: point if intersects else None
        """

        r = self.as_vec()   # line's vector
        s = ray.normal      # ray's vector
        p, q = self.start, ray.origin
        pq_vec = q - p

        pq_r_norm = Vec.cross(pq_vec, r)
        r_s_norm = Vec.cross(r, s)
        if r_s_norm.is_zero(): # means line and ray is parallel
            if pq_r_norm.is_zero(): # means collinearity. notice parallel != collinear
                # may be three cases
                # 1. ray covers whole line -> return line itself
                # 2. ray covers line fragment -> return new line fragment
                # 3. ray covers no line -> return None
                n, m = Vec.dot(pq_vec, r), Vec.dot(pq_vec, s)
                line_param = n / r.length**2
                if 0 <= line_param <= 1:    # ray starts at on the line
                    if (line_param == 0 and m >= 0) or (line_param == 1 and m < 0): # 1.
                        return self
                    else:   # 2.
                        start = self.start + r*line_param
                        end = self.end if m >= 0 else self.start
                        return Lin.from_pnts(start, end)
                else:
                    if line_param < 0 and m < 0:   # 1.
                        return self
                    elif line_param > 1 and m < 0:
                        return self.reversed()
                    else:   # 3.
                        return None
            else:
                return None
        else:   # may be point intersection or not
            param_l = Vec.cross(pq_vec, s).length/Vec.cross(r, s).length
            param_r = Vec.cross(pq_vec, r).length/Vec.cross(r, s).length
            if param_l == 0:
                return self.start
            elif param_l == 1:
                return self.end
            elif 0 < param_l < 1:
                lin_intx_pnt = self.start + r*param_l
                pnt_intx_lin = ray.origin + s*param_r
                # check for coplanarity here
                if lin_intx_pnt == pnt_intx_lin:
                    return lin_intx_pnt
                else:
                    return None
            else:
                return None
