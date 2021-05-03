import os
import ctypes

from ckernel.render_context.opengl_context.context_stack import get_current_ogl
import ckernel.render_context.opengl_context.entities.meta as meta
import ckernel.render_context.opengl_context.opengl_hooker as gl

from global_tools.singleton import Singleton
from .base import Renderer, get_shader_fullpath
import weakref as wr

"""
Three renderers of dimensional primitives.

A primitive renderer does not only render of its kind.
High dimensional entity is a combination of lower dimensional primitives.
So, a triangle can be viewed in lines and points.
This is why three renderers are atomic.

Shape holdes buffer, buffer cache and vertex array(vao)
, while,
renderer holds prgrm and global uniform cache

"""


class PointRenderer(Renderer):
    """
    this is not an expandable, simple functionality wrapper

    prgrm parameter layout:

    ! follow fixed attribute location
    layout (location = 0) in vec4 vtx;
    layout (location = 1) in vec4 clr;
    layout (location = 2) in float dia;
    ... add more to expand render possibility
    :return:

    :param self.__~_prgrm: program drawing sized square points
    :param self.__~_indx_bffr: index buffer storing drawing index of its type
    :param self.__~_ufrm_cache: buffer cache of transformation matrices

    """
    __square_prgrm = meta.MetaPrgrm(
        vrtx_path=os.path.join(os.path.dirname(__file__), 'shaders/pnts/pntSqr_vrtx_shdr.glsl'),
        geom_path=os.path.join(os.path.dirname(__file__), 'shaders/pnts/pntSqr_geom_shdr.glsl'),
        frgm_path=os.path.join(os.path.dirname(__file__), 'shaders/pnts/pntSqr_frgm_shdr.glsl'))

    __circle_prgrm = meta.MetaPrgrm(
        vrtx_path=os.path.join(os.path.dirname(__file__), 'shaders/pnts/pntCir_vrtx_shdr.glsl'),
        frgm_path=os.path.join(os.path.dirname(__file__), 'shaders/pnts/pntCir_frgm_shdr.glsl'))

    __triangle_prgrm = meta.MetaPrgrm(
        vrtx_path=os.path.join(os.path.dirname(__file__), 'shaders/pnts/pntTgl_vrtx_shdr.glsl'),
        geom_path=os.path.join(os.path.dirname(__file__), 'shaders/pnts/pntTgl_geom_shdr.glsl'),
        frgm_path=os.path.join(os.path.dirname(__file__), 'shaders/pnts/pntTgl_frgm_shdr.glsl'))

    def __init__(self):
        super().__init__()

        self.__vbo = self.__square_prgrm.vrtx_attr_schema.create_vrtx_bffr()
        self.__circle_ibo = meta.MetaIndxBffr('uint')
        self.__circle_vao = meta.MetaVrtxArry(self.__vbo, indx_bffr=self.__circle_ibo)
        self.__square_ibo = meta.MetaIndxBffr('uint')
        self.__square_vao = meta.MetaVrtxArry(self.__vbo, indx_bffr=self.__square_ibo)
        self.__triangle_ibo = meta.MetaIndxBffr('uint')
        self.__triangle_vao = meta.MetaVrtxArry(self.__vbo, indx_bffr=self.__triangle_ibo)

        self.__ibos = {'s': self.__square_ibo,
                       't': self.__triangle_ibo,
                       'c': self.__circle_ibo}

    def update_cache(self, shape, arg_name, val):
        if arg_name in ('geo', 'clr', 'dia'):
            self.datasets[shape]['vrtx'][arg_name] = val
        elif arg_name == 'frm':
            if val not in self.__ibos:
                raise ValueError("form value has to be one of 's'quare, 't'riangle, 'c'ircle")
            # swap ibo
            ibo = self.datasets[shape]['ibo']
            new_ibo = self.__ibos[val]
            if ibo == new_ibo:
                return
            if ibo:
                self.datasets[shape]['indx'].release()
            self.datasets[shape]['ibo'] = new_ibo
            indx_block = new_ibo.cache.request_block(size=1)
            self.datasets[shape]['indx'] = indx_block
            # put index value
            indx_block['idx'] = self.datasets[shape]['vrtx'].indices
        else:
            raise AttributeError

    def create_dataset(self, size):
        dataset = {'vrtx': self.__vbo.cache.request_block(size),
                'indx': self.__square_ibo.cache.request_block(size),
                'ibo': self.__square_ibo}
        dataset['indx']['idx'] = dataset['vrtx'].indices
        return dataset

    def free_finalizer(self, dataset: dict):
        """
        automatically release blocks when blocks dict looses shape
        :param dataset:
        :return:
        """
        # for gc being late
        if dataset:
            if dataset['vrtx']:
                dataset['vrtx'].release()
            if dataset['indx']:
                dataset['indx'].release()
            dataset.clear()

    def render(self):
        self.__vbo.push_cache()
        self.__render_square()
        self.__render_circle()
        self.__render_triangle()

    def __render_square(self):
        if not self.__square_ibo.cache.active_size:
            return
        with self.__square_vao:
            with self.__square_prgrm:
                # update uniforms
                camera = get_current_ogl().manager.window.devices.cameras.current
                self.__square_prgrm.uniforms['PM'] = camera.body.PM
                self.__square_prgrm.uniforms['VM'] = camera.tripod.VM
                self.__square_prgrm.uniforms['MM'] = [[1, 0, 0, 0],
                                                      [0, 1, 0, 0],
                                                      [0, 0, 1, 0],
                                                      [0, 0, 0, 1]]
                self.__square_prgrm.push_uniforms()
                self.__square_ibo.push_cache()
                # mode, count, type, indices
                gl.glDrawElements(gl.GL_POINTS,
                                  self.__square_ibo.cache.active_size,
                                  self.__square_ibo.cache.gldtype[0],
                                  ctypes.c_void_p(0))

    def __render_circle(self):
        if not self.__circle_ibo.cache.active_size:
            return
        with self.__circle_vao:
            with self.__circle_prgrm:
                # update uniforms
                camera = get_current_ogl().manager.window.devices.cameras.current

                self.__circle_prgrm.uniforms['PM'] = camera.body.PM
                self.__circle_prgrm.uniforms['VM'] = camera.tripod.VM
                self.__circle_prgrm.uniforms['MM'] = [[1, 0, 0, 0],
                                                      [0, 1, 0, 0],
                                                      [0, 0, 1, 0],
                                                      [0, 0, 0, 1]]
                pane = get_current_ogl().manager.window.devices.panes.current
                self.__circle_prgrm.uniforms['VPP'] = *pane.pos.xy, *pane.size.xy
                self.__circle_prgrm.push_uniforms()
                self.__circle_ibo.push_cache()

                gl.glDrawElements(gl.GL_POINTS,
                                  self.__circle_ibo.cache.active_size,
                                  self.__circle_ibo.cache.gldtype[0],
                                  ctypes.c_void_p(0))

    def __render_triangle(self):
        if not self.__triangle_ibo.cache.active_size:
            return
        with self.__triangle_vao:
            with self.__triangle_prgrm:
                # update uniforms
                camera = get_current_ogl().manager.window.devices.cameras.current

                self.__triangle_prgrm.uniforms['PM'] = camera.body.PM
                self.__triangle_prgrm.uniforms['VM'] = camera.tripod.VM
                self.__triangle_prgrm.uniforms['MM'] = [[1, 0, 0, 0],
                                                        [0, 1, 0, 0],
                                                        [0, 0, 1, 0],
                                                        [0, 0, 0, 1]]
                self.__triangle_prgrm.push_uniforms()
                self.__triangle_ibo.push_cache()
                gl.glDrawElements(gl.GL_POINTS,
                                  self.__triangle_ibo.cache.active_size,
                                  self.__triangle_ibo.cache.gldtype[0],
                                  ctypes.c_void_p(0))


class LineRenderer(Renderer):
    """
    prgrm parameter layout:

    ! programs should follow fixed attribute locations
    layout (location = 0) in vec4 vtx;
    layout (location = 1) in float thk;
    layout (location = 2) in vec4 clr;
    ... add more to expand render possibility

    :param self.__sharp_prgrm: program drawing thick sharp line
    :param self.__trnsf_ufrm_cache: buffer cache of transformation matrices
    """
    __sharp_prgrm = meta.MetaPrgrm(
        vrtx_path=os.path.join(os.path.dirname(__file__), 'shaders/linSharp_vrtx_shdr.glsl'),
        geom_path=os.path.join(os.path.dirname(__file__), 'shaders/linSharp_geom_shdr.glsl'),
        frgm_path=os.path.join(os.path.dirname(__file__), 'shaders/linSharp_frgm_shdr.glsl'))

    def __init__(self):
        super().__init__()
        self.__vbo = self.__sharp_prgrm.vrtx_attr_schema.create_vrtx_bffr()
        self.__ibo = meta.MetaIndxBffr(dtype='uint')
        self.__vao = meta.MetaVrtxArry(self.__vbo, indx_bffr=self.__ibo)

    def create_dataset(self, size):
        dataset = {'vrtx': self.__vbo.cache.request_block(size),
                   'indx': self.__ibo.cache.request_block(size)}
        dataset['indx']['idx'] = dataset['vrtx'].indices
        return dataset

    def free_finalizer(self, dataset):
        if dataset:
            for v in dataset.values():
                v.release()
            dataset.clear()

    def update_cache(self, shape, arg_name, value):
        dataset = self.datasets[shape]
        if arg_name in ('geo', 'clr','thk'):
            dataset['vrtx'][arg_name] = value
        else:
            raise AttributeError

    def render(self):
        self.__vbo.push_cache()
        self.__render_sharp()

    def __render_sharp(self):
        if not self.__ibo.cache.active_size:
            return
        with self.__vao:
            with self.__sharp_prgrm:
                camera = get_current_ogl().manager.window.devices.cameras.current
                self.__sharp_prgrm.uniforms['VM'] = camera.tripod.VM
                self.__sharp_prgrm.uniforms['PM'] = camera.body.PM
                self.__sharp_prgrm.uniforms['MM'] = [[1, 0, 0, 0],
                                                     [0, 1, 0, 0],
                                                     [0, 0, 1, 0],
                                                     [0, 0, 0, 1]]
                self.__sharp_prgrm.push_uniforms()
                self.__ibo.push_cache()
                gl.glDrawElements(gl.GL_LINES,
                                  self.__ibo.cache.active_size,
                                  self.__ibo.cache.gldtype[0],
                                  ctypes.c_void_p(0))


@Singleton
class PolylineRenderer(Renderer):
    __sharp_prgrm = meta.MetaPrgrm(
        vrtx_path=get_shader_fullpath('shaders/plinSharp_vrtx_shdr.glsl'),
        geom_path=get_shader_fullpath('shaders/plinSharp_geom_shdr.glsl'),
        frgm_path=get_shader_fullpath('shaders/plinSharp_frgm_shdr.glsl')
    )

    def __init__(self):
        super().__init__()
        self.__vbo = self.__sharp_prgrm.vrtx_attr_schema.create_vrtx_bffr()
        self.__ibo = meta.MetaIndxBffr(dtype='uint')
        self.__vao = meta.MetaVrtxArry(self.__vbo, indx_bffr=self.__ibo)

    def create_dataset(self, size):
        dataset = {'vrtx': self.__vbo.cache.request_block(size),
                   'indx': self.__ibo.cache.request_block(size)}
        dataset['indx']['idx'] = dataset['vrtx'].indices
        return dataset

    def free_finalizer(self, dataset, *args, **kargs):
        if dataset:
            dataset['vrtx'].release()
            dataset['indx'].release()
            dataset.clear()

    def update_cache(self, shape, arg_name, value):
        self.datasets[shape]['vrtx'][arg_name] = value

    def render(self):
        self.__vbo.push_cache()
        self.__ibo.push_cache()
        self.__render_sharp()

    def __render_sharp(self):
        if not self.__ibo.cache.active_size:
            return
        with self.__vao:
            with self.__sharp_prgrm:
                # uniforms
                camera = get_current_ogl().manager.window.devices.cameras.current
                self.__sharp_prgrm.uniforms['VM'] = camera.tripod.VM
                self.__sharp_prgrm.uniforms['PM'] = camera.body.PM
                self.__sharp_prgrm.uniforms['MM'] = [[1, 0, 0, 0],
                                                     [0, 1, 0, 0],
                                                     [0, 0, 1, 0],
                                                     [0, 0, 0, 1]]
                self.__sharp_prgrm.push_uniforms()

                gl.glDrawElements(gl.GL_LINE_STRIP,
                                  self.__ibo.cache.active_size,
                                  self.__ibo.cache.gldtype[0],
                                  ctypes.c_void_p(0))


class TriangleRenderer(Renderer):
    """
    full spec schema of triangle object.

    use this schema as programs are not obliged to implement all attributes

    ! programs should follow fixed attribute name and locations
    layout(location = 0) in vtx;
    layout(location = 1) in edge_thk;
    layout(location = 2) in edge_clr;
    layout(location = 3) in fill_clr;
    ... add more to expand render possibility

    :param self.__fill_prgrm: for drawing triangle fill
    :param self.__edge_prgrm: for drawing triangle thick edge
    :param self.__trnsf_ufrm_cache: buffer cache of transformation matrices
    """

    __prgrm = meta.MetaPrgrm(
        vrtx_path=os.path.join(os.path.dirname(__file__), 'shaders/tgls/tglSharpEdge_vrtx_shdr.glsl'),
        geom_path=os.path.join(os.path.dirname(__file__), 'shaders/tgls/tglSharpEdge_geom_shdr.glsl'),
        frgm_path=os.path.join(os.path.dirname(__file__), 'shaders/tgls/tglSharpEdge_frgm_shdr.glsl'))

    def __init__(self):
        super().__init__()

        self.__vbo = self.__prgrm.vrtx_attr_schema.union(self.__prgrm.vrtx_attr_schema).create_vrtx_bffr()
        self.__ibo = meta.MetaIndxBffr('uint')
        self.__vao = meta.MetaVrtxArry(self.__vbo, indx_bffr=self.__ibo)

    def create_dataset(self, size):
        vb = self.__vbo.cache.request_block(size)
        ib = self.__ibo.cache.request_block(size)
        ib['idx'] = vb.indices
        return {'vrtx': vb, 'indx': ib}

    def free_finalizer(self, dataset):
        if dataset:
            for block in dataset.values():
                block.release()
            dataset.clear()

    def update_cache(self, shape, arg_name, value):
        self.datasets[shape]['vrtx'][arg_name] = value

    def __update_global_ufrm(self, prgrm):
        """
        update transformation uniforms
        :return:
        """
        camera = get_current_ogl().manager.window.devices.cameras.current
        prgrm.uniforms['PM'] = camera.body.PM
        prgrm.uniforms['VM'] = camera.tripod.VM
        prgrm.uniforms['MM'] = [[1, 0, 0, 0],
                                [0, 1, 0, 0],
                                [0, 0, 1, 0],
                                [0, 0, 0, 1]]
        prgrm.push_uniforms()

    def render(self, is_render_edge=True):
        """

        :param is_render_edge: bool, do render edge?
        :return:
        """
        self.__vbo.push_cache()
        self.__ibo.push_cache()
        with self.__vao:
            if not self.__ibo.cache.active_size:
                return
            with self.__prgrm:
                self.__update_global_ufrm(self.__prgrm)
                gl.glDrawElements(gl.GL_TRIANGLES,
                                  self.__ibo.cache.active_size,
                                  self.__ibo.cache.gldtype[0],
                                  ctypes.c_void_p(0))
