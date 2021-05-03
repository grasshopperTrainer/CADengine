import ctypes as ct

import ckernel.render_context.opengl_context.entities.meta as meta
from .base import Renderer, get_shader_fullpath
from ckernel.render_context.opengl_context.context_stack import get_current_ogl
import ckernel.render_context.opengl_context.opengl_hooker as gl
from ckernel.constants import PRIMITIVE_RESTART_VAL as PRV


class PolygonRenderer(Renderer):
    __fill_prgrm = meta.MetaPrgrm(
        vrtx_path=get_shader_fullpath('shaders/pgon/pgonFill_vrtx_shdr.glsl'),
        frgm_path=get_shader_fullpath('shaders/pgon/pgonFill_frgm_shdr.glsl'))

    __edge_prgrm = meta.MetaPrgrm(
        vrtx_path=get_shader_fullpath('shaders/pgon/pgonSharpEdge_vrtx_shdr.glsl'),
        geom_path=get_shader_fullpath('shaders/pgon/pgonSharpEdge_geom_shdr.glsl'),
        frgm_path=get_shader_fullpath('shaders/pgon/pgonSharpEdge_frgm_shdr.glsl'))

    def __init__(self):
        super().__init__()

        self.__vbo = self.__fill_prgrm.vrtx_attr_schema.create_vrtx_bffr()
        self.__fill_ibo = meta.MetaIndxBffr(dtype='uint')
        self.__fill_vao = meta.MetaVrtxArry(self.__vbo, indx_bffr=self.__fill_ibo)
        self.__edge_ibo = meta.MetaIndxBffr(dtype='uint')
        self.__edge_vao = meta.MetaVrtxArry(self.__vbo, indx_bffr=self.__edge_ibo)

    def create_dataset(self, size):
        return {'vrtx': self.__vbo.cache.request_block(size),
                'fill_indxs': None,
                'edge_indxs': None}

    def free_finalizer(self, dataset):
        if dataset:
            for block in dataset.values():
                block.release()
            dataset.clear()

    def update_cache(self, shape, arg_name, value):
        dataset = self.datasets[shape]
        if arg_name == 'fill_indxs':
            offset = dataset['vrtx'].indices[0]
            ib = self.__fill_ibo.cache.request_block(size=len(value) + 1)
            ib['idx', :-1] = [offset + i if i != PRV else PRV for i in value]
            ib['idx', -1] = PRV
            dataset[arg_name] = ib
        elif arg_name == 'edge_indxs':
            offset = dataset['vrtx'].indices[0]
            ib = self.__edge_ibo.cache.request_block(size=len(value) + 1)
            ib['idx', :-1] = [offset + i for i in value]
            ib['idx', -1] = PRV
            dataset[arg_name] = ib
        else:
            print(arg_name, value)
            self.datasets[shape]['vrtx'][arg_name] = value

    def render(self):
        self.__vbo.push_cache()
        self.__render_fill()
        self.__render_edge()

    def __update_umiforms(self, prgrm):
        camera = get_current_ogl().manager.window.devices.cameras.current
        prgrm.uniforms['PM'] = camera.body.PM
        prgrm.uniforms['VM'] = camera.tripod.VM
        prgrm.uniforms['MM'] = [[1, 0, 0, 0],
                                [0, 1, 0, 0],
                                [0, 0, 1, 0],
                                [0, 0, 0, 1]]
        prgrm.push_uniforms()

    def __render_fill(self):
        self.__fill_ibo.push_cache()
        with self.__fill_vao:
            with self.__fill_prgrm as prgrm:
                self.__update_umiforms(prgrm)
                gl.glDrawElements(gl.GL_QUAD_STRIP,
                                  self.__fill_ibo.cache.active_size,
                                  self.__fill_ibo.cache.gldtype[0],
                                  ct.c_void_p(0))

    def __render_edge(self):
        self.__edge_ibo.push_cache()
        with self.__edge_vao:
            with self.__edge_prgrm as prgrm:
                self.__update_umiforms(prgrm)
                gl.glDrawElements(gl.GL_LINE_STRIP_ADJACENCY,
                                  self.__edge_ibo.cache.active_size,
                                  self.__edge_ibo.cache.gldtype[0],
                                  ct.c_void_p(0))
